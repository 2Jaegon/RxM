import streamlit as st
import plotly.graph_objects as go
import pandas as pd


def apply_custom_css():
    st.markdown("""
    <style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css');

    /* ── STITCH GEMINI DARK DESIGN SYSTEM ───────
       bg-app     : #131314 (Gemini dark main background)
       bg-sidebar : #1E1F20 (Gemini dark sidebar background)
       bg-hover   : #282A2C (Gemini hover / active item)
       bg-pill    : #282A2C (Gemini pill background)
       border     : #2D2F31 (Gemini border line)
       text-main  : #E3E3E3 (Gemini primary text)
       text-sub   : #C4C7C5 (Gemini secondary text)
       text-mute  : #8E918F (Gemini muted text)
       accent     : #A8C7FA (Gemini spark blue)
    ────────────────────────────────────────── */

    html, body, [class*="css"], * {
        font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }
    .stApp { background-color: #131314; color: #E3E3E3; }

    /* ABSOLUTELY NUKE STREAMLIT SIDEBAR & HEADER */
    [data-testid="stSidebar"],
    section[data-testid="stSidebar"],
    [data-testid="stSidebarNav"],
    [data-testid="stSidebarHeader"],
    [data-testid="stSidebarCollapseButton"],
    [data-testid="stSidebarCollapsedControl"],
    [data-testid="collapsedControl"],
    div[data-testid="stSidebarCollapsedControl"],
    button[data-testid="stSidebarCollapseButton"],
    button[aria-label*="sidebar"],
    button[aria-label*="Sidebar"],
    header[data-testid="stHeader"],
    .stApp > header,
    [data-testid="stHeader"] {
        display: none !important;
        visibility: hidden !important;
        opacity: 0 !important;
        pointer-events: none !important;
        width: 0px !important;
        height: 0px !important;
        margin: 0 !important;
        padding: 0 !important;
        position: absolute !important;
        top: -9999px !important;
        left: -9999px !important;
    }

    [data-testid="stAppViewContainer"] > section:first-child {
        display: none !important;
    }

    .block-container {
        padding: 1rem 2rem !important;
        max-width: 100% !important;
        margin: 0 auto !important;
    }

    /* MAIN CONTENT AREA */
    .main-content { padding: 0.5rem 1rem; }
    
    iframe.stIFrame {
        height: 85vh !important;
    }

    /* CHAT MESSAGES */
    .chat-topbar { padding-bottom: 0.8rem; margin-bottom: 1rem; border-bottom: 1px solid #2D2F31; }
    .chat-messages-container { min-height: 320px; }
    .chat-row { display: flex; margin-bottom: 1.6rem; gap: 0.9rem; }
    .user-row { justify-content: flex-end; }
    .ai-row   { justify-content: flex-start; }

    .chat-bubble {
        max-width: 75%;
        padding: 0.95rem 1.25rem;
        border-radius: 18px;
        font-size: 0.92rem;
        font-weight: 400;
        line-height: 1.78;
    }
    .user-bubble {
        background: #282A2C;
        color: #FFFFFF;
        border-bottom-right-radius: 4px;
    }
    .ai-bubble {
        background: #1E1F20;
        color: #E3E3E3;
        border: 1px solid #2D2F31;
        border-bottom-left-radius: 4px;
    }
    .chat-avatar {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        background: #282A2C;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
        margin-top: 2px;
    }
    .chat-avatar img {
        width: 20px;
        height: 20px;
        object-fit: contain;
    }

    /* CHAT WELCOME SCREEN (STITCH GEMINI 1:1) */
    .chat-welcome {
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 4rem 2rem 2.5rem;
        text-align: center;
    }
    .chat-welcome-logo { margin-bottom: 1.2rem; }
    .chat-welcome-logo-img { width: 42px; height: 42px; object-fit: contain; }
    .chat-welcome-title { font-size: 1.7rem; font-weight: 600; color: #FFFFFF; margin-bottom: 0.6rem; letter-spacing: -0.01em; }
    .chat-welcome-sub { font-size: 0.9rem; font-weight: 400; color: #C4C7C5; line-height: 1.75; margin-bottom: 2.2rem; }
    .chat-suggestions { display: flex; flex-direction: column; gap: 0.65rem; width: 100%; max-width: 500px; }
    .chat-suggestion {
        background: #1E1F20;
        border: 1px solid #2D2F31;
        border-radius: 16px;
        padding: 0.9rem 1.25rem;
        font-size: 0.88rem;
        font-weight: 400;
        color: #E3E3E3;
        text-align: left;
        cursor: pointer;
        transition: background 0.15s, border-color 0.15s;
    }
    .chat-suggestion:hover { border-color: #A8C7FA; background: #282A2C; color: #FFFFFF; }

    /* CHAT INPUT BAR (GEMINI STITCH FLOATING BAR) */
    [data-testid="stChatInput"] {
        background: #1E1F20 !important;
        border: 1px solid #2D2F31 !important;
        border-radius: 28px !important;
        padding: 0.4rem 0.8rem !important;
    }
    [data-testid="stChatInput"] textarea { background: transparent !important; color: #FFFFFF !important; font-size: 0.92rem !important; }
    [data-testid="stChatInput"] button { color: #A8C7FA !important; }

    /* PANEL */
    .rxm-panel { background: #1E1F20; border: 1px solid #2D2F31; border-radius: 16px; padding: 1.6rem; }

    /* SECTION TITLE */
    .rxm-section-title {
        font-size: 0.82rem;
        font-weight: 700;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: #A8C7FA;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid #2D2F31;
    }

    /* LABEL */
    .rxm-label {
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: #C4C7C5;
        margin-bottom: 0.4rem;
    }

    /* STATUS BLOCK */
    .rxm-status-block {
        display: flex; align-items: center; gap: 0.9rem;
        padding: 0.9rem 1.2rem; border-radius: 14px; margin-top: 1.1rem;
        border: 1px solid #2D2F31; background: #131314;
    }
    .rxm-status-indicator { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
    .status-normal .rxm-status-indicator { background: #A8C7FA; box-shadow: 0 0 6px #A8C7FA88; }
    .status-alert  .rxm-status-indicator { background: #F2B8B5; box-shadow: 0 0 6px #F2B8B588; }
    .rxm-status-title { font-size: 0.88rem; font-weight: 600; color: #FFFFFF; }
    .rxm-status-detail { font-size: 0.75rem; font-weight: 400; color: #C4C7C5; margin-top: 0.15rem; }

    /* EMPTY STATE */
    .rxm-empty-state {
        display: flex; flex-direction: column; align-items: center;
        justify-content: center; height: 380px;
        text-align: center; line-height: 1.8; font-size: 0.9rem; color: #C4C7C5;
    }
    .rxm-empty-icon { font-size: 3rem; color: #A8C7FA; margin-bottom: 1.2rem; }

    /* PRESCRIPTION CARD */
    .rxm-prescription {
        background: #1E1F20; border: 1px solid #2D2F31;
        border-left: 4px solid #A8C7FA; border-radius: 14px;
        padding: 1.5rem; margin-top: 1.2rem;
    }
    .rxm-prescription-title {
        font-size: 0.78rem; font-weight: 700; letter-spacing: 0.12em;
        text-transform: uppercase; color: #A8C7FA; margin-bottom: 0.9rem;
    }
    .rxm-prescription-body { font-size: 0.92rem; font-weight: 400; line-height: 1.9; color: #FFFFFF; }

    /* WIDGETS */
    .stSelectbox > div > div {
        background-color: #1E1F20 !important; border: 1px solid #2D2F31 !important;
        border-radius: 12px !important; color: #FFFFFF !important;
        font-size: 0.88rem !important; font-weight: 500 !important;
    }
    [data-testid="stFileUploader"] {
        background: #1E1F20; border: 1px dashed #2D2F31; border-radius: 14px; padding: 1rem;
    }
    [data-testid="stFileUploader"] label { color: #FFFFFF !important; font-size: 0.85rem !important; }

    .main-content .stButton > button {
        background: #1E1F20 !important; color: #A8C7FA !important;
        border: 1px solid #A8C7FA !important; border-radius: 20px !important;
        font-size: 0.8rem !important; font-weight: 600 !important;
        letter-spacing: 0.05em !important;
        padding: 0.6rem 1.2rem !important; transition: all 0.18s ease !important;
    }
    .main-content .stButton > button:hover { background: #A8C7FA !important; color: #131314 !important; }
    .main-content .stButton > button[kind="primary"] { background: #A8C7FA !important; color: #131314 !important; font-weight: 700 !important; }
    .main-content .stButton > button[kind="primary"]:hover { background: #D3E3FD !important; }

    .stTextInput > div > div > input {
        background: #1E1F20 !important; border: 1px solid #2D2F31 !important;
        border-radius: 12px !important; color: #FFFFFF !important; font-size: 0.88rem !important;
    }
    .stSpinner > div { border-top-color: #A8C7FA !important; }
    .stSuccess { background: #132718 !important; border: 1px solid #1C4D26 !important; color: #6DD58C !important; border-radius: 12px !important; font-size: 0.88rem !important; }
    .stError   { background: #2B1617 !important; border: 1px solid #602224 !important; color: #F2B8B5 !important; border-radius: 12px !important; font-size: 0.88rem !important; }
    .stWarning { background: #2A2012 !important; border: 1px solid #5A401A !important; color: #F5D996 !important; border-radius: 12px !important; font-size: 0.88rem !important; }
    hr { border-color: #2D2F31 !important; }
    h1,h2,h3 { font-weight: 600; color: #FFFFFF; }
    </style>
    """, unsafe_allow_html=True)


def render_timeseries_chart(df: pd.DataFrame):
    time_col = df.columns[0]
    value_cols = [
        col for col in df.columns
        if col != time_col
        and not col.endswith('_ma')
        and not col.endswith('_ucl')
        and not col.endswith('anomaly')
        and col != 'anomaly_score'
    ]
    if not value_cols:
        st.warning("표시할 숫자형 열을 찾을 수 없습니다.")
        return

    main_col = value_cols[0]
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df[time_col], y=df[main_col], mode='lines',
        name=main_col, line=dict(color='#A8C7FA', width=2.0)
    ))
    if f'{main_col}_ma' in df.columns:
        fig.add_trace(go.Scatter(
            x=df[time_col], y=df[f'{main_col}_ma'], mode='lines',
            name='이동 평균', line=dict(color='#8E918F', width=1.2, dash='dash')
        ))
    if f'{main_col}_ucl' in df.columns:
        fig.add_trace(go.Scatter(
            x=df[time_col], y=df[f'{main_col}_ucl'], mode='lines',
            name='관리 한계선', line=dict(color='#F5D996', width=1.2, dash='dot')
        ))
    if 'is_anomaly' in df.columns and df['is_anomaly'].any():
        anom = df[df['is_anomaly']]
        fig.add_trace(go.Scatter(
            x=anom[time_col], y=anom[main_col], mode='markers',
            name='이상 감지', marker=dict(color='#F2B8B5', size=8, symbol='x', line=dict(width=2))
        ))
        for _, row in anom.iterrows():
            fig.add_vrect(
                x0=row[time_col], x1=row[time_col],
                fillcolor="rgba(242,184,181,0.12)", layer="below", line_width=0
            )

    fig.update_layout(
        title=None, template="plotly_dark",
        plot_bgcolor="#131314", paper_bgcolor="#131314",
        margin=dict(l=10, r=10, t=15, b=15),
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                    font=dict(size=11, color="#C4C7C5"), bgcolor="rgba(0,0,0,0)"),
        xaxis=dict(gridcolor="#282A2C", linecolor="#2D2F31", tickfont=dict(color="#C4C7C5", size=11)),
        yaxis=dict(gridcolor="#282A2C", linecolor="#2D2F31", tickfont=dict(color="#C4C7C5", size=11))
    )
    st.plotly_chart(fig, use_container_width=True)


def render_prescription_card(prescription: str):
    body = prescription.replace('\n', '<br>')
    st.markdown(f"""
    <div class="rxm-prescription">
        <div class="rxm-prescription-title">AI 조치 가이드</div>
        <div class="rxm-prescription-body">{body}</div>
    </div>
    """, unsafe_allow_html=True)
