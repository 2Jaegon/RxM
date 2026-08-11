import os
try:
    from langchain_ollama import ChatOllama, OllamaEmbeddings
except ImportError:
    from langchain_community.chat_models import ChatOllama
    from langchain_community.embeddings import OllamaEmbeddings

try:
    from langchain_chroma import Chroma
except ImportError:
    from langchain_community.vectorstores import Chroma
try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    from langchain.text_splitter import RecursiveCharacterTextSplitter

try:
    from langchain_classic.chains import create_retrieval_chain
    from langchain_classic.chains.combine_documents import create_stuff_documents_chain
except ImportError:
    from langchain.chains import create_retrieval_chain
    from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from services.masking_service import mask_text, unmask_text

# Initialize ChromaDB persistent directory
CHROMA_DB_DIR = os.environ.get("CHROMA_DB_DIR", "./chroma_db")

def get_vector_store(equipment_type: str):
    """Gets or creates a Chroma collection for a specific equipment type."""
    ollama_base_url = os.environ.get("OLLAMA_BASE_URL", "http://host.docker.internal:11434")
    ollama_model = os.environ.get("OLLAMA_MODEL", "gemma2")
    embeddings = OllamaEmbeddings(base_url=ollama_base_url, model=ollama_model)
    # Use equipment_type as the collection name to isolate knowledge
    collection_name = "".join([c if c.isalnum() else "_" for c in equipment_type.lower()])
    if not collection_name:
        collection_name = "default_equipment"
        
    return Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory=CHROMA_DB_DIR
    )

def get_prescription(equipment_type: str, anomaly_keywords: list[str], context_data: dict) -> str:
    """Generates a troubleshooting prescription based on detected anomalies."""
    if not anomaly_keywords:
        return "No significant anomalies detected. Equipment is operating normally."

    query = f"Anomalies detected: {', '.join(anomaly_keywords)}. What are the causes and what actions should be taken?"
    
    # Mask proprietary terms in query
    masked_query, mask_map = mask_text(query)
    
    ollama_base_url = os.environ.get("OLLAMA_BASE_URL", "http://host.docker.internal:11434")
    ollama_model = os.environ.get("OLLAMA_MODEL", "gemma2")
    llm = ChatOllama(base_url=ollama_base_url, model=ollama_model, temperature=0.2)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert prescriptive maintenance engineer AI. Based on the provided manuals and past maintenance history, provide a clear, step-by-step troubleshooting guide for the reported anomalies. If you don't know the answer based on the context, suggest standard engineering checks."),
        ("human", "Context: {context}\n\nQuery: {input}")
    ])
    
    vector_store = get_vector_store(equipment_type)
    retriever = vector_store.as_retriever(search_kwargs={"k": 3})
    
    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    rag_chain = create_retrieval_chain(retriever, question_answer_chain)
    
    try:
        response = rag_chain.invoke({"input": masked_query})
        prescription = response["answer"]
        # Unmask proprietary terms in response
        final_prescription = unmask_text(prescription, mask_map)
        return final_prescription
    except Exception as e:
        return f"Error generating prescription: {str(e)}. Please check your Ollama connection and model."

def update_knowledge_base(equipment_type: str, issue_description: str, action_taken: str):
    """Adds engineer feedback into the RAG database for adaptive learning."""
    text_to_add = f"Past Issue: {issue_description}\nSuccessful Action Taken: {action_taken}"
    
    masked_text, _ = mask_text(text_to_add) # Masking before storing in DB (optional depending on DB security, but good practice if using cloud DBs)
    
    vector_store = get_vector_store(equipment_type)
    vector_store.add_texts([masked_text])
    # Note: Chroma auto-persists in newer versions, but we can rely on persist_directory

def upload_document(file_content: bytes, filename: str, equipment_type: str):
    """Processes uploaded manuals and adds them to ChromaDB."""
    # Basic text extraction assuming txt for now. PDF would require PyPDF2 or pdfminer
    text = ""
    if filename.endswith(".txt"):
        text = file_content.decode('utf-8')
    elif filename.endswith(".csv"):
        text = file_content.decode('utf-8')
    else:
        # Fallback naive decode
        try:
            text = file_content.decode('utf-8')
        except:
            text = str(file_content)
    
    masked_text, _ = mask_text(text)
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_text(masked_text)
    
    if chunks:
        vector_store = get_vector_store(equipment_type)
        vector_store.add_texts(chunks)

def chat_with_rag(message: str, equipment_type: str, history: list[dict]) -> str:
    """
    Conversational RAG: takes a user message + chat history and returns an AI answer
    grounded in the equipment-specific knowledge base.
    """
    ollama_base_url = os.environ.get("OLLAMA_BASE_URL", "http://host.docker.internal:11434")
    ollama_model = os.environ.get("OLLAMA_MODEL", "gemma2")
    llm = ChatOllama(base_url=ollama_base_url, model=ollama_model, temperature=0.3)

    masked_message, mask_map = mask_text(message)

    # Build history context string
    history_text = ""
    for turn in history[-6:]:  # last 3 exchanges
        role = "사용자" if turn.get("role") == "user" else "AI"
        history_text += f"{role}: {turn.get('content', '')}\n"

    system_prompt = (
        "당신은 제조 설비 및 예지 보전 전문가 AI입니다. "
        "제공된 지식 베이스(매뉴얼, 과거 이력)를 바탕으로 사용자의 질문에 명확하고 실용적으로 답변하세요. "
        "한국어로 답변하며, 지식 베이스에 정보가 없을 경우 일반적인 엔지니어링 조언을 제공하세요."
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "참고 문서:\n{context}\n\n이전 대화:\n" + history_text + "\n사용자 질문: {input}")
    ])

    vector_store = get_vector_store(equipment_type)
    retriever = vector_store.as_retriever(search_kwargs={"k": 3})

    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    rag_chain = create_retrieval_chain(retriever, question_answer_chain)

    try:
        response = rag_chain.invoke({"input": masked_message})
        answer = response["answer"]
        return unmask_text(answer, mask_map)
    except Exception as e:
        return f"오류가 발생했습니다: {str(e)}. Ollama 연결 및 모델 상태를 확인해주세요."
