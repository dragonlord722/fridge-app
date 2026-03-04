import os
import json
import base64
from io import BytesIO
from PIL import Image
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from pydantic import BaseModel
from google import genai

# --- 1. INITIALIZATION & RATE LIMITER ---
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="Fridge AI Backend")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# --- 2. CORS POLICY ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://ravi-fridge-chef.streamlit.app"], 
    allow_methods=["POST"],
    allow_headers=["*"],
)

# --- 3. DATA MODELS & HELPERS ---
class ImagePayload(BaseModel):
    image_base64: str

def decode_image(base64_string: str) -> Image.Image:
    try:
        if "," in base64_string:
            base64_string = base64_string.split(",")[1]
        image_data = base64.b64decode(base64_string)
        return Image.open(BytesIO(image_data))
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid base64 image encoding")

# --- 4. SECURITY MIDDLEWARE ---
PORTFOLIO_TOKEN = os.environ.get("X_PORTFOLIO_TOKEN", "fallback-secret-for-local-dev")

@app.middleware("http")
async def verify_portfolio_token(request: Request, call_next):
    if request.url.path == "/analyze":
        token = request.headers.get("X-Portfolio-Token")
        if token != PORTFOLIO_TOKEN:
            # FIX: Must RAISE, not return
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Unauthorized: Invalid Portfolio Token"
            )
    response = await call_next(request)
    return response

# --- 5. THE ENDPOINT ---
@app.post("/analyze")
@limiter.limit("5/minute") # FIX: Added the actual rate limit decorator
async def analyze_fridge(payload: ImagePayload, request: Request): # Added request param for Limiter
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="LLM API Key not configured.")
    
    try:
        image = decode_image(payload.image_base64)
        client = genai.Client(api_key=api_key)
        
        prompt = """
You are a highly precise Culinary Vision Engine. Your task is to analyze the provided image 
and return a strictly formatted JSON response.

### STEP 1: VALIDATION
Determine if the image contains food, kitchen ingredients, or a refrigerator interior. 
- If the image is absolutely not food or a kitchen, you **MUST** set 'is_valid_fridge_image' to false. Do not attempt to find food in documents, screenshots of software, or vehicles.
- If the image is NOT food-related (e.g., a car, a pet, a person, electronics, or blurry/unidentifiable), 
  set 'is_valid_fridge_image' to false and provide a helpful 'error_message'.
- If the image IS food-related, set 'is_valid_fridge_image' to true.

### STEP 2: EXTRACTION (Only if is_valid_fridge_image is true)
1. 'ingredients': List all identifiable food items.
2. 'missing_essentials': Identify 2-3 staples typically found in an Indian kitchen that are absent.
3. 'recipes': Suggest 2-3 pure vegetarian Indian or Fusion recipes. Each must have 'name' and 'cuisine'.

### OUTPUT FORMAT
Return ONLY a JSON object with this exact structure:
{
  "is_valid_fridge_image": boolean,
  "error_message": string or null,
  "ingredients": list,
  "missing_essentials": list,
  "recipes": [{"name": string, "cuisine": string}]
}
"""
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[image, prompt],
            config={"response_mime_type": "application/json"} 
        )
        
        response_data = json.loads(response.text)
        
        # Staff Tip: Even if the LLM fails to return a key, 
        # we provide defaults to keep the Frontend stable.
        return {
            "is_valid_fridge_image": response_data.get("is_valid_fridge_image", False),
            "error_message": response_data.get("error_message", "Invalid image provided."),
            "ingredients": response_data.get("ingredients", []),
            "missing_essentials": response_data.get("missing_essentials", []),
            "recipes": response_data.get("recipes", [])
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))