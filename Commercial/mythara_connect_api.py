# Copyright © 2026 Mythara Labs LLC. All rights reserved.

"""
MytharaConnect API - Railway Deployment

FastAPI server exposing MytharaConnect as a chat API endpoint
Integrates with the pricing page via embedded chat widget
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict
import hashlib
import os
import logging
from datetime import datetime

# Import MytharaConnect
from mythara_connect import MytharaConnect

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="MytharaConnect API",
    description="Industry-aware AI sales agent with Mythara governance",
    version="1.0.0",
)

# CORS for pricing page integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://mytharaarchive-production.up.railway.app",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize MytharaConnect (singleton)
mythara_bot = None


def get_mythara_bot():
    """Get or initialize MytharaConnect instance"""
    global mythara_bot
    if mythara_bot is None:
        mythara_bot = MytharaConnect(
            full_autonomy=True, enable_voice=False
        )  # No voice on server
    return mythara_bot


# Rate limiting (simple in-memory - use Redis for production)
CHAT_RATE_LIMITS = {}


def check_chat_rate_limit(ip: str) -> bool:
    """Check if IP has exceeded chat rate limit (30 messages per hour)"""
    now = datetime.now()
    if ip not in CHAT_RATE_LIMITS:
        CHAT_RATE_LIMITS[ip] = []

    # Clean old entries (older than 1 hour)
    CHAT_RATE_LIMITS[ip] = [
        ts for ts in CHAT_RATE_LIMITS[ip] if (now - ts).total_seconds() < 3600
    ]

    # Check limit
    if len(CHAT_RATE_LIMITS[ip]) >= 30:
        return False

    CHAT_RATE_LIMITS[ip].append(now)
    return True


# Pydantic models
class ChatMessage(BaseModel):
    message: str
    prospect_email: Optional[EmailStr] = None
    company_name: Optional[str] = None
    selected_industry: Optional[str] = None
    conversation_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    industry_detected: Optional[str] = None
    validation_status: Dict
    conversation_id: str
    requires_human_review: bool


class IndustrySelectionRequest(BaseModel):
    prospect_email: EmailStr
    company_name: Optional[str] = None


# API Endpoints


@app.get("/", response_class=HTMLResponse)
async def root():
    """API documentation landing page"""
    return """
    <html>
        <head><title>MytharaConnect API</title></head>
        <body style="font-family: monospace; padding: 40px;">
            <h1>🔗 MytharaConnect API</h1>
            <p>Industry-aware AI sales agent with Mythara SSIP governance</p>
            
            <h2>Endpoints:</h2>
            <ul>
                <li><code>GET /health</code> - Health check</li>
                <li><code>POST /v1/chat/discovery</code> - Start discovery conversation</li>
                <li><code>POST /v1/chat/message</code> - Send chat message</li>
                <li><code>GET /v1/chat/widget</code> - Get chat widget HTML</li>
                <li><code>GET /api/docs</code> - OpenAPI documentation</li>
            </ul>
            
            <h2>Integration:</h2>
            <p>Add this to your pricing page:</p>
            <pre>&lt;script src="https://mytharaarchive-production.up.railway.app/v1/chat/widget.js"&gt;&lt;/script&gt;</pre>
            
            <p><a href="/api/docs">→ Full API Documentation</a></p>
        </body>
    </html>
    """


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    bot = get_mythara_bot()
    return {
        "status": "healthy",
        "service": "MytharaConnect",
        "version": "1.0.0",
        "bot_ready": bot is not None,
        "governance": "SSIP enabled",
        "timestamp": datetime.now().isoformat(),
    }


@app.post("/v1/chat/discovery", response_model=ChatResponse)
async def start_discovery(request: IndustrySelectionRequest, http_request: Request):
    """
    Start discovery conversation - sends industry selection email

    Returns industry discovery email asking prospect to identify their vertical
    """
    # Rate limiting
    client_ip = http_request.client.host
    if not check_chat_rate_limit(client_ip):
        raise HTTPException(
            status_code=429, detail="Rate limit exceeded. Try again later."
        )

    bot = get_mythara_bot()

    # Generate discovery email
    discovery_email = bot.craft_discovery_email(
        prospect_email=request.prospect_email, company_name=request.company_name or ""
    )

    # Generate conversation ID
    conversation_id = hashlib.sha256(
        f"{request.prospect_email}{datetime.now().isoformat()}".encode()
    ).hexdigest()[:16]

    return ChatResponse(
        response=discovery_email,
        industry_detected=None,  # Not yet - waiting for prospect to select
        validation_status={"approved": True, "risk_score": 0, "stage": "discovery"},
        conversation_id=conversation_id,
        requires_human_review=False,
    )


@app.post("/v1/chat/message", response_model=ChatResponse)
async def chat_message(chat: ChatMessage, http_request: Request):
    """
    Process chat message from prospect

    Detects intent, generates industry-tailored response, validates with Mythara governance
    """
    # Rate limiting
    client_ip = http_request.client.host
    if not check_chat_rate_limit(client_ip):
        raise HTTPException(
            status_code=429, detail="Rate limit exceeded. Try again later."
        )

    bot = get_mythara_bot()

    # If prospect selected industry, generate tailored follow-up
    if chat.selected_industry:
        response_email = bot.craft_industry_specific_followup(
            prospect_email=chat.prospect_email or "unknown@example.com",
            selected_industry=chat.selected_industry,
            company_name=chat.company_name or "",
        )

        return ChatResponse(
            response=response_email,
            industry_detected=chat.selected_industry,
            validation_status={
                "approved": True,
                "risk_score": 10,
                "stage": "education",
            },
            conversation_id=chat.conversation_id or "unknown",
            requires_human_review=False,
        )

    # Otherwise, detect intent and generate response
    email_data = {
        "prospect_email": chat.prospect_email or "unknown@example.com",
        "company_name": chat.company_name or "",
        "body": chat.message,
    }

    # Detect industry from email
    industry = bot.detect_industry(email_data)

    # Classify intent (simple keyword matching - could use LLM)
    intent = "unknown"
    message_lower = chat.message.lower()

    if any(
        word in message_lower
        for word in ["interested", "yes", "sounds good", "let's talk", "schedule"]
    ):
        intent = "interested"
    elif any(word in message_lower for word in ["how", "what", "explain", "?"]):
        intent = "question"
    elif any(
        word in message_lower
        for word in ["no", "not interested", "stop", "unsubscribe"]
    ):
        intent = "not_interested"

    # Generate response
    response = bot.generate_soulful_response(email_data, intent)

    # Get validation status from last response
    validation_result = bot._validate_with_mythara(response, email_data)

    return ChatResponse(
        response=response,
        industry_detected=industry,
        validation_status={
            "approved": validation_result["approved"],
            "risk_score": validation_result["risk_score"],
            "violations": validation_result["violations"],
            "warnings": validation_result["warnings"],
        },
        conversation_id=chat.conversation_id
        or hashlib.sha256(
            f"{chat.prospect_email}{datetime.now().isoformat()}".encode()
        ).hexdigest()[:16],
        requires_human_review=validation_result["requires_human_review"],
    )


@app.get("/v1/chat/widget.js", response_class=HTMLResponse)
async def chat_widget_script():
    """
    JavaScript widget for embedding MytharaConnect chat on pricing page
    """
    return """
// MytharaConnect Chat Widget
(function() {
    const API_BASE = 'https://mytharaarchive-production.up.railway.app';
    
    // Create chat widget HTML
    const widgetHTML = `
        <div id="mythara-chat-widget" style="position: fixed; bottom: 20px; right: 20px; z-index: 9999;">
            <button id="mythara-chat-toggle" style="
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                border-radius: 50%;
                width: 60px;
                height: 60px;
                font-size: 24px;
                cursor: pointer;
                box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            ">💬</button>
            
            <div id="mythara-chat-box" style="
                display: none;
                position: absolute;
                bottom: 80px;
                right: 0;
                width: 380px;
                height: 500px;
                background: white;
                border-radius: 12px;
                box-shadow: 0 8px 24px rgba(0,0,0,0.3);
                flex-direction: column;
            ">
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 16px; border-radius: 12px 12px 0 0; font-weight: bold;">
                    🔗 MytharaConnect
                    <span style="float: right; cursor: pointer;" id="mythara-close">✕</span>
                </div>
                
                <div id="mythara-messages" style="flex: 1; overflow-y: auto; padding: 16px; font-family: system-ui;">
                    <div style="background: #f0f0f0; padding: 12px; border-radius: 8px; margin-bottom: 12px;">
                        Hi! I'm MytharaConnect, an AI sales agent. 
                        <br><br>
                        Before I share anything, which industry best describes your organization?
                        <br><br>
                        <select id="industry-select" style="width: 100%; padding: 8px; margin-top: 8px; border-radius: 4px;">
                            <option value="">Select your industry...</option>
                            <option value="banking">Banking/Financial Services</option>
                            <option value="healthcare">Healthcare/Life Sciences</option>
                            <option value="insurance">Insurance/Actuarial</option>
                            <option value="education">Education/Academic</option>
                            <option value="tech_saas">Technology/SaaS</option>
                            <option value="retail">Retail/E-commerce</option>
                            <option value="government">Government/Public Sector</option>
                        </select>
                        <button id="submit-industry" style="
                            width: 100%;
                            padding: 10px;
                            margin-top: 8px;
                            background: #667eea;
                            color: white;
                            border: none;
                            border-radius: 4px;
                            cursor: pointer;
                        ">Continue</button>
                    </div>
                </div>
                
                <div style="padding: 16px; border-top: 1px solid #eee;">
                    <input id="mythara-input" type="text" placeholder="Type your message..." style="
                        width: calc(100% - 60px);
                        padding: 10px;
                        border: 1px solid #ddd;
                        border-radius: 20px;
                    ">
                    <button id="mythara-send" style="
                        width: 50px;
                        padding: 10px;
                        background: #667eea;
                        color: white;
                        border: none;
                        border-radius: 50%;
                        cursor: pointer;
                        margin-left: 8px;
                    ">➤</button>
                </div>
            </div>
        </div>
    `;
    
    // Inject widget
    document.body.insertAdjacentHTML('beforeend', widgetHTML);
    
    // Event handlers
    let conversationId = null;
    let selectedIndustry = null;
    
    document.getElementById('mythara-chat-toggle').addEventListener('click', () => {
        document.getElementById('mythara-chat-box').style.display = 'flex';
    });
    
    document.getElementById('mythara-close').addEventListener('click', () => {
        document.getElementById('mythara-chat-box').style.display = 'none';
    });
    
    document.getElementById('submit-industry').addEventListener('click', async () => {
        const industry = document.getElementById('industry-select').value;
        if (!industry) return;
        
        selectedIndustry = industry;
        
        // Show loading
        const messagesDiv = document.getElementById('mythara-messages');
        messagesDiv.innerHTML += `<div style="text-align: center; color: #999;">⏳ Tailoring response...</div>`;
        
        // Call API
        const response = await fetch(`${API_BASE}/v1/chat/message`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: `I selected: ${industry}`,
                selected_industry: industry,
                prospect_email: 'prospect@example.com',
                conversation_id: conversationId
            })
        });
        
        const data = await response.json();
        conversationId = data.conversation_id;
        
        // Display response
        messagesDiv.innerHTML = `
            <div style="background: #f0f0f0; padding: 12px; border-radius: 8px; white-space: pre-wrap; font-size: 13px;">
                ${data.response}
            </div>
        `;
    });
    
    document.getElementById('mythara-send').addEventListener('click', async () => {
        const input = document.getElementById('mythara-input');
        const message = input.value.trim();
        if (!message) return;
        
        const messagesDiv = document.getElementById('mythara-messages');
        
        // Show user message
        messagesDiv.innerHTML += `
            <div style="background: #667eea; color: white; padding: 10px; border-radius: 8px; margin-bottom: 8px; margin-left: 40px;">
                ${message}
            </div>
        `;
        
        input.value = '';
        
        // Call API
        const response = await fetch(`${API_BASE}/v1/chat/message`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: message,
                selected_industry: selectedIndustry,
                conversation_id: conversationId
            })
        });
        
        const data = await response.json();
        conversationId = data.conversation_id;
        
        // Show bot response
        messagesDiv.innerHTML += `
            <div style="background: #f0f0f0; padding: 12px; border-radius: 8px; margin-bottom: 8px; white-space: pre-wrap; font-size: 13px;">
                ${data.response}
            </div>
        `;
        
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    });
})();
"""


@app.get("/v1/chat/widget", response_class=HTMLResponse)
async def chat_widget_embed():
    """HTML snippet to embed MytharaConnect chat on any page"""
    return """
<!DOCTYPE html>
<html>
<head>
    <title>MytharaConnect Chat Widget</title>
</head>
<body>
    <h1>MytharaConnect Chat Widget - Embed Code</h1>
    <p>Add this to your pricing page's HTML (before closing &lt;/body&gt; tag):</p>
    
    <pre style="background: #f5f5f5; padding: 20px; border-radius: 8px;">
&lt;script src="https://mytharaarchive-production.up.railway.app/v1/chat/widget.js"&gt;&lt;/script&gt;
    </pre>
    
    <h2>Test it:</h2>
    <script src="/v1/chat/widget.js"></script>
</body>
</html>
"""


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
