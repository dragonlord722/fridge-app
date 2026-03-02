import os
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from pydantic import BaseModel

# 1. Initialize Rate Limiter (5 requests per minute per IP)
limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# 2. CORS Policy: Replace with your actual Streamlit URL!
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://ravi-fridge-chef.streamlit.app"], 
    allow_methods=["POST"],
    allow_headers=["*"],
)

# 3. Custom Header Security Middleware
PORTFOLIO_TOKEN = os.environ.get("X_PORTFOLIO_TOKEN", "fallback-secret-for-local-dev")

@app.middleware("http")
async def verify_portfolio_token(request: Request, call_next):
    # Only protect the analyze endpoint
    if request.url.path == "/analyze":
        token = request.headers.get("X-Portfolio-Token")
        if token != PORTFOLIO_TOKEN:
            return HTTPException(status_code=401, detail="Unauthorized: Invalid Portfolio Token")
    return await call_next(request)

# ... (rest of your /analyze route logic remains the same)

# 3. THE ENDPOINT
# We define a POST route. The `payload: ImagePayload` argument tells FastAPI to use our Pydantic contract.
@app.post("/analyze")
async def analyze_fridge(payload: ImagePayload):
    
    # SECURITY: We pull the API key from the environment, NOT a local file. 
    # This ensures that when deployed to GCP, Cloud Run can inject the secret securely.
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="LLM API Key not configured in environment.")
    
    try:
        # 4. THE CORE LOGIC (google-genai)
        image = decode_image(payload.image_base64)
        client = genai.Client(api_key=api_key)
        
        prompt = """You are a culinary AI assistant. Analyze the provided image of a refrigerator or ingredients. 
        Return a valid JSON object with exactly three keys:
        1. 'ingredients': A list of strings of identified food items.
        2. 'missing_essentials': A list of 2-3 common staple items that seem to be missing.
        3. 'recipes': A list of 2-3 suggested pure vegetarian Indian or fusion recipes based heavily on the found ingredients. Each recipe should be an object with 'name' and 'cuisine' keys."""
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[image, prompt],
            # Enforcing strict JSON output at the API level
            config={"response_mime_type": "application/json"} 
        )
        
        # We parse the string response into a Python dictionary, and FastAPI automatically 
        # converts it into a proper JSON HTTP response for the client.
        return json.loads(response.text)
        
    except ValueError as ve:
        # Catches the base64 decoding errors (Client Error)
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        # Catches API or LLM processing errors (Server Error)
        raise HTTPException(status_code=500, detail=str(e))
    
