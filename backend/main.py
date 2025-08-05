# backend/main.py - COMPLETE UPDATED VERSION

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from services.document_service import process_document_upload
from services.email_service import ingest_sample_emails
from services.gmail_service import gmail_service
from services.ai_service import ask_question

app = FastAPI(
    title="Lexsy Legal Assistant API",
    description="AI-powered legal document assistant with Gmail integration and RAG capabilities",
    version="2.0.0"
)

# CORS - Update for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "message": "Lexsy Legal Assistant API with Gmail Integration", 
        "version": "2.0.0",
        "features": ["Document Processing", "Gmail OAuth", "AI Chat", "Multi-Client"],
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health")
def health():
    return {"status": "ok", "gmail_available": True}

# Document endpoints
@app.post("/api/documents/{client_id}/upload")
async def upload_document(client_id: int, file: UploadFile = File(...)):
    """Upload and process a document (PDF, DOCX, TXT) for a specific client"""
    try:
        result = process_document_upload(client_id, file) 
        return JSONResponse(content={"success": True, **result})
    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

# Email endpoints
@app.post("/api/emails/{client_id}/ingest-sample-emails")
async def ingest_emails(client_id: int):
    """Ingest sample emails for a specific client"""
    try:
        result = ingest_sample_emails(client_id)
        return JSONResponse(content={"success": True, **result})
    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

# Gmail Authentication Endpoints
@app.get("/auth/gmail")
async def initiate_gmail_auth():
    """Initiate Gmail OAuth flow"""
    try:
        auth_url = gmail_service.get_authorization_url()
        return JSONResponse(content={"auth_url": auth_url})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/auth/callback")
async def gmail_auth_callback(code: str = Query(...)):
    """Handle Gmail OAuth callback"""
    try:
        result = gmail_service.handle_oauth_callback(code)
        # Redirect to frontend with success message
        return RedirectResponse(url="/?gmail_auth=success")
    except Exception as e:
        return RedirectResponse(url=f"/?gmail_auth=error&message={str(e)}")

@app.get("/auth/gmail/status")
async def gmail_auth_status():
    """Check Gmail authentication status"""
    is_authenticated = gmail_service.is_authenticated()
    return JSONResponse(content={"authenticated": is_authenticated})

# Gmail Integration Endpoints
@app.post("/api/gmail/{client_id}/ingest-mock")
async def ingest_mock_gmail(client_id: int):
    """Ingest mock Gmail conversation for demo"""
    try:
        result = gmail_service.create_mock_conversation(client_id)
        return JSONResponse(content={"success": True, **result})
    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

@app.post("/api/gmail/{client_id}/ingest-thread")
async def ingest_gmail_thread(client_id: int, thread_id: str = Form(...)):
    """Ingest a specific Gmail thread"""
    try:
        result = gmail_service.ingest_gmail_thread(client_id, thread_id)
        return JSONResponse(content={"success": True, **result})
    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

# AI Chat endpoint
@app.post("/api/chat/{client_id}/ask")
async def chat_with_ai(client_id: int, question: str = Form(...)):
    """Ask a question about the client's documents and emails using AI"""
    try:
        result = ask_question(client_id, question)
        return JSONResponse(content={"success": True, **result})
    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})