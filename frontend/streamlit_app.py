import streamlit as st
import requests
import base64
from PIL import Image
import io
import os


# 1. Configuration
PORTFOLIO_TOKEN = st.secrets.get("X_PORTFOLIO_TOKEN", "")
# Check if running in a Codespace or local environment
if os.getenv("CODESPACES") == "true":
    # If in Codespace, use the local port 8000 URL
    BACKEND_URL = "http://localhost:8000"
else:
    # Fallback to Cloud Run for production
    BACKEND_URL = "https://fridge-backend-service-845166114793.us-central1.run.app"


# 2. Helper Function (Keep at top level for test access)
def compress_image(uploaded_file):
    img = Image.open(uploaded_file)
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    img.thumbnail((1024, 1024)) 
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85) 
    return buf.getvalue()


# 3. All UI and Execution logic MUST be inside main()
def main():
    st.set_page_config(page_title="AI Fridge Chef", page_icon="🍳", layout="centered")
    st.title("🍳 AI Fridge Chef")
    st.markdown("### Applied AI Portfolio: Enterprise Microservice Edition 🚀")

    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        st.image(uploaded_file, caption="Your Fridge", use_container_width=True)

        if st.button("Generate Recipes"):
            if not PORTFOLIO_TOKEN:
                st.error("Missing X_PORTFOLIO_TOKEN in Secrets.")
                st.stop()

            with st.spinner("Analyzing..."):
                try:
                    image_bytes = compress_image(uploaded_file)
                    base64_string = base64.b64encode(image_bytes).decode('utf-8')
                    
                    response = requests.post(
                        f"{BACKEND_URL}/analyze", 
                        json={"image_base64": base64_string}, 
                        headers={"X-Portfolio-Token": PORTFOLIO_TOKEN},
                        timeout=90 
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        if not result.get("is_valid_fridge_image", True):
                            st.error(f"🛑 **Validation Error:** {result.get('error_message')}")
                        else:
                            st.success("Recipes generated!")
                            
                            # 1. Ingredients & Essentials Columns
                            col1, col2 = st.columns(2)
                            with col1:
                                st.subheader("🛒 Found Ingredients")
                                ingredients = result.get("ingredients", [])
                                if ingredients:
                                    for item in ingredients:
                                        st.write(f"- {item}")
                                else:
                                    st.info("No specific ingredients identified.")
                            
                            with col2:
                                st.subheader("⚠️ Missing Essentials")
                                missing = result.get("missing_essentials", [])
                                if missing:
                                    for item in missing:
                                        st.write(f"- {item}")
                                else:
                                    st.write("You're all set!")

                            st.divider()

                            # 2. Recipe Recommendations
                            st.subheader("👨‍🍳 Chef's Recommendations")
                            recipes = result.get("recipes", [])
                            if recipes:
                                for recipe in recipes:
                                    with st.expander(f"📖 {recipe.get('name', 'Untitled Recipe')}"):
                                        st.write(f"**Description:** {recipe.get('description', 'No description provided.')}")
                                        
                                        st.write("**Ingredients needed:**")
                                        for req in recipe.get("ingredients_needed", []):
                                            st.write(f"- {req}")
                                            
                                        st.write("**Instructions:**")
                                        st.write(recipe.get("instructions", "Follow standard cooking procedures."))
                            else:
                                st.warning("No specific recipes could be generated for these items.")
                    else:
                        st.error(f"Backend Error: {response.status_code}")
                        
                except Exception as e:
                    st.error(f"Network error: {e}")

if __name__ == "__main__":
    main()