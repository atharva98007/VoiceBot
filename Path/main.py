import os
import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from google import genai
from google.genai import types

app = FastAPI(title="Hindi-Telugu Hybrid Voice Bot (Gemini)")

# Enable CORS so your frontend can communicate seamlessly
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the Gemini Client directly with your key string
client = genai.Client(api_key="AIzaSyCE9Qs5eun-LoldLcsD7fLtfiRv132DiBA")

LOGS_DIR = "logs"
os.makedirs(LOGS_DIR, exist_ok=True)

# In-memory dictionary to hold persistent chat sessions for multi-turn memory
active_chats = {}

class ChatRequest(BaseModel):
    session_id: str
    message: str

def save_log_to_file(session_id: str, chat_history):
    """Saves the conversation logs to a JSON file."""
    file_path = os.path.join(LOGS_DIR, f"{session_id}.json")
    
    readable_history = []
    for message in chat_history:
        if message.role == "system":
            continue
        readable_history.append({
            "role": "User" if message.role == "user" else "Bot",
            "text": message.parts[0].text if message.parts else ""
        })

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(readable_history, f, ensure_ascii=False, indent=4)

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    session_id = request.session_id
    user_message = request.message

    if session_id not in active_chats:
        system_instruction = (
            "You are an interactive AI voice bot helper for Sankar Group. [cite: 58] "
            "You must communicate in a natural mix of Hindi and Telugu (Hinglish/Telugish hybrid language). [cite: 4] "
            "Example interactions:\n"
            "User: Namaste, naa peru Raju\n"
            "Bot: Namaste Raju ji, aapko kaise help chahiye?\n"
            "User: Mujhe ek software demo kavali\n"
            "Bot: Sure, meeku demo schedule chestanu\n\n"
            "Keep your responses short, natural, and helpful. They must be voice-bot friendly."
        )
        
        active_chats[session_id] = client.chats.create(
            model="gemini-2.5-flash",
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.7
            )
        )
    
    try:
        chat_session = active_chats[session_id]
        response = chat_session.send_message(user_message)
        bot_response = response.text
        
        history = chat_session.get_history()
        save_log_to_file(session_id, history)
        
        return {
            "status": "success",
            "bot_response": bot_response
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# NEW ROUTE: Serves the frontend index.html natively on http://127.0.0.1:1000/
@app.get("/", response_class=HTMLResponse)
async def get_frontend():
    # Make sure index.html is located in the exact same folder as main.py
    if not os.path.exists("index.html"):
        return """
        <html>
            <body style='font-family:sans-serif; text-align:center; padding-top:50px;'>
                <h2 style='color:#ef4444;'>index.html Not Found!</h2>
                <p>Please place your <b>index.html</b> file directly inside this folder: <code>""" + os.getcwd() + """</code></p>
            </body>
        </html>
        """
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()

# ADDED: Program execution entry point specifying port 1000
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=1000, reload=True)