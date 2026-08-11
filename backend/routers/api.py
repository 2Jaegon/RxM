from fastapi import APIRouter, UploadFile, File, Form
from pydantic import BaseModel
import pandas as pd
import io
from services.fdc_service import process_sensor_data
from services.rag_service import get_prescription, update_knowledge_base, upload_document, chat_with_rag

router = APIRouter()

class PrescriptionRequest(BaseModel):
    equipment_type: str
    anomaly_keywords: list[str]
    context_data: dict

class FeedbackRequest(BaseModel):
    equipment_type: str
    issue_description: str
    action_taken: str

class ChatRequest(BaseModel):
    message: str
    equipment_type: str
    history: list[dict] = []

@router.post("/analyze")
async def analyze_data(file: UploadFile = File(...), equipment_type: str = Form(...)):
    """
    Endpoint to receive CSV sensor data, preprocess, and perform FDC.
    """
    contents = await file.read()
    df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
    
    # Process data with FDC (and MATLAB engine for FFT if applicable)
    result = process_sensor_data(df, equipment_type)
    return {"status": "success", "data": result}

@router.post("/prescription")
def request_prescription(req: PrescriptionRequest):
    """
    Endpoint to get a troubleshooting prescription from RAG.
    """
    prescription = get_prescription(req.equipment_type, req.anomaly_keywords, req.context_data)
    return {"status": "success", "prescription": prescription}

@router.post("/feedback")
def submit_feedback(req: FeedbackRequest):
    """
    Endpoint for adaptive learning (Adaptive Prescriptive Maintenance).
    """
    update_knowledge_base(req.equipment_type, req.issue_description, req.action_taken)
    return {"status": "success", "message": "Feedback integrated into RAG database."}

@router.post("/admin/upload_manual")
async def upload_manual(file: UploadFile = File(...), equipment_type: str = Form(...)):
    """
    Endpoint for admin to upload PDF/TXT manuals to update ChromaDB.
    """
    contents = await file.read()
    # Save temporarily or process directly
    upload_document(contents, file.filename, equipment_type)
    return {"status": "success", "message": f"Manual {file.filename} added to knowledge base."}

@router.post("/chat")
def chat(req: ChatRequest):
    """
    Conversational RAG endpoint. Accepts a user message and returns an AI response
    grounded in the equipment knowledge base.
    """
    answer = chat_with_rag(req.message, req.equipment_type, req.history)
    return {"status": "success", "answer": answer}
