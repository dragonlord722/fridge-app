import streamlit as st
import requests
import base64

# Your live Cloud Run Microservice URL
BACKEND_URL = "https://fridge-backend-service-845166114793.us-central1.run.app"

st.set_page_config(page_title="AI Fridge Chef", page_icon="🍳")
st.title("🍳 AI Fridge Chef")
st.markdown("**Enterprise Microservice Edition** 🚀")

st.write("Upload a picture of your fridge, and our cloud backend will generate recipes!")

uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    st.image(uploaded_file, caption="Your Fridge", use_column_width=True)

    if st.button("Generate Recipes"):
        with st.spinner("Sending image to Cloud Run backend..."):
            try:
                # 1. Convert the image to Base64
                image_bytes = uploaded_file.getvalue()
                base64_string = base64.b64encode(image_bytes).decode('utf-8')
                
                # 2. Package for Pydantic
                payload = {"image_base64": base64_string}
                
                # 3. Call the Cloud Run API
                response = requests.post(f"{BACKEND_URL}/analyze", json=payload)
                
                # 4. Handle the response
                if response.status_code == 200:
                    result = response.json()
                    st.success("Recipes generated successfully!")
                    
                    st.markdown("### 🛒 Ingredients Found:")
                    for item in result.get("ingredients", []):
                        st.write(f"- {item}")
                        
                    st.markdown("### ⚠️ Missing Essentials:")
                    for missing in result.get("missing_essentials", []):
                        st.write(f"- {missing}")
                        
                    st.markdown("### 👨‍🍳 Recipe Suggestions:")
                    for recipe in result.get("recipes", []):
                        st.write(f"**{recipe.get('name', 'Recipe')}** ({recipe.get('cuisine', 'Unknown')})")
                        
                else:
                    st.error(f"Backend Error (Status {response.status_code})")
                    st.write(response.text)
                    
            except requests.exceptions.RequestException as e:
                st.error(f"Failed to connect to the backend microservice: {e}")