from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import requests
import os
from dotenv import load_dotenv

# Load .env file for your Gemini API key
load_dotenv()
GEMINI_API_KEY =  os.getenv("API_KEY") # set this in .env

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def hello():
    return {"response":"Hello from server"}


@app.post("/api/chat_gemini")
async def chat_gemini(request: Request):
    body = await request.json()
    user_message = body.get("message")
    print(user_message)
    if not user_message:
        return {"error": "No message provided"}

    # Prepare the Gemini API request
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"

    # Build the request body according to Gemini spec
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {
                        "text": str(user_message)
                    }
                ]
            }
        ]
    }

    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": GEMINI_API_KEY
    }

    resp = requests.post(url, headers=headers, json=payload)
    resp_json = resp.json()

    # Extract the model's reply
    try:
        candidates = resp_json.get("candidates", [])
        if not candidates:
            reply_text = "No reply from Gemini"
        else:
            # The first candidate -> its content -> first part -> text
            content = candidates[0].get("content", {})
            parts = content.get("parts", [])
            if not parts:
                reply_text = "No parts in reply"
            else:
                reply_text = parts[0].get("text", "")
    except Exception as e:
        reply_text = f"Error parsing Gemini response: {e}"

    return {
        "reply": reply_text,
        "raw": resp_json
    }
