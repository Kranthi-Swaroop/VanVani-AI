"""Main FastAPI application for VanVani AI."""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response, Form
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from twilio.twiml.voice_response import VoiceResponse, Gather

from app.config import get_settings
from app.voice_handler import VoiceHandler
from app.database.sql_db import init_database
from app.utils.analytics import log_call

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
settings = get_settings()

class WebChatRequest(BaseModel):
    message: str
    language: str = "hi"
    sessionId: str = "web-session"

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management."""
    logger.info("Starting VanVani AI...")
    await init_database()
    app.state.voice_handler = VoiceHandler()
    yield
    logger.info("Shutting down VanVani AI...")

app = FastAPI(
    title=settings.app_name,
    description="Voice-based AI system for rural Chhattisgarh",
    version="1.0.0",
    lifespan=lifespan
)

# Static files for web demo
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/")
async def root():
    return {"status": "active", "service": settings.app_name}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "environment": settings.environment,
        "database": "connected"
    }

@app.post("/webhook/incoming-call")
async def handle_incoming_call(request: Request, From: str = Form(...)):
    """Initial call handler for Twilio."""
    logger.info(f"Incoming call from: {From}")
    await log_call(From, "incoming", "initiated")
    
    response = VoiceResponse()
    welcome_text = (
        "नमस्कार! मैं वनवाणी हूं। "
        "आप गोंडी, हल्बी, छत्तीसगढ़ी, या हिंदी में बात कर सकते हैं। "
        "कृपया अपना सवाल बोलें।"
    )
    
    gather = Gather(
        input='speech',
        action='/webhook/process-speech',
        method='POST',
        language='hi-IN',
        speechTimeout='auto',
        speechModel='phone_call'
    )
    gather.say(welcome_text, language='hi-IN')
    response.append(gather)
    response.say("मुझे आपकी आवाज़ नहीं सुनाई दी। कृपया फिर से कोशिश करें।", language='hi-IN')
    
    return Response(content=str(response), media_type="application/xml")

@app.post("/webhook/process-speech")
async def process_speech(
    request: Request,
    SpeechResult: str = Form(None),
    From: str = Form(...),
    CallSid: str = Form(...)
):
    """Process speech and generate AI response."""
    if not SpeechResult:
        response = VoiceResponse()
        response.say("मुझे आपकी आवाज़ नहीं सुनाई दी। कृपया फिर से कोशिश करें।", language='hi-IN')
        return Response(content=str(response), media_type="application/xml")
    
    try:
        voice_handler = request.app.state.voice_handler
        ai_response, detected_language = await voice_handler.process_query(
            SpeechResult, 
            From,
            CallSid
        )
        
        response = VoiceResponse()
        response.say(ai_response, language=detected_language)
        
        gather = Gather(
            input='speech',
            action='/webhook/process-speech',
            method='POST',
            language=detected_language,
            speechTimeout='auto',
            timeout=5
        )
        
        follow_up = "क्या आपको और कुछ जानकारी चाहिए?" if detected_language == 'hi-IN' else "Do you need more information?"
        gather.say(follow_up, language=detected_language)
        response.append(gather)
        
        goodbye = "धन्यवाद! फिर से कॉल करें।" if detected_language == 'hi-IN' else "Thank you! Call again."
        response.say(goodbye, language=detected_language)
        
        await log_call(From, "processed", SpeechResult, ai_response)
        return Response(content=str(response), media_type="application/xml")
        
    except Exception as e:
        logger.error(f"Error processing speech: {e}")
        response = VoiceResponse()
        response.say("क्षमा करें, कुछ समस्या हो गई है। कृपया बाद में फिर से कोशिश करें।", language='hi-IN')
        return Response(content=str(response), media_type="application/xml")

@app.post("/webhook/call-status")
async def call_status(CallSid: str = Form(...), CallStatus: str = Form(...)):
    logger.info(f"Call {CallSid} status: {CallStatus}")
    return {"status": "received"}

@app.get("/analytics/dashboard")
async def analytics_dashboard():
    from app.utils.analytics import get_analytics
    return await get_analytics()

@app.post("/admin/reload-knowledge-base")
async def reload_knowledge_base():
    try:
        from app.database.vector_db import reload_vector_db
        await reload_vector_db()
        return {"status": "success", "message": "Knowledge base reloaded"}
    except Exception as e:
        logger.error(f"Error reloading knowledge base: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/api/web-chat")
async def web_chat(request: WebChatRequest, req: Request):
    """Handle web interface chat."""
    try:
        voice_handler = req.app.state.voice_handler
        response, detected_lang = await voice_handler.process_query(
            user_input=request.message,
            caller_id="WEB_USER",
            call_sid=request.sessionId,
            language=request.language
        )
        return {"response": response, "language": detected_lang, "status": "success"}
    except Exception as e:
        logger.error(f"Web chat error: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=settings.debug)


