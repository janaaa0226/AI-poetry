import streamlit as st
import google.generativeai as genai
from fpdf import FPDF
import qrcode
from io import BytesIO
import arabic_reshaper
from bidi.algorithm import get_display
import os
import base64

# --- 1. SETUP ---
try:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=GOOGLE_API_KEY)
except:
    st.error("API Key missing!")

# --- 2. PAGE CONFIG ---
st.set_page_config(page_title="Foundation Day Poetry", layout="wide")

# --- 3. THE "HERITAGE TEMPLATE" CSS ---
background_image_url = "https://i.pinimg.com/1200x/a3/8a/ca/a38acae15a962ecc7ab69d30dd42d5f3.jpg"

st.markdown(f'''
<style>
@import url('https://fonts.googleapis.com/css2?family=Amiri:wght@700&family=Playfair+Display:wght@700&display=swap');
header {{visibility: hidden;}}
#MainMenu {{visibility: hidden;}}
footer {{visibility: hidden;}}
div.stDeployButton {{display:none;}}

.stApp {{ background-image: url("{background_image_url}"); background-size: cover; background-attachment: fixed; }}

.main-title {{
    font-size: 65px !important; font-weight: 700 !important; text-align: center !important;
    color: #f5f0e1 !important; text-shadow: 3px 3px 15px rgba(0,0,0,0.7) !important; 
    margin: 10px 0px !important;
}}

.poem-template {{
    background-color: rgba(245, 240, 225, 0.96); 
    padding: 60px; border-radius: 20px; border: 8px double #3e2723;
    max-width: 800px; margin: 50px auto;
    color: #3e2723 !important; font-family: 'Amiri', serif; 
    font-weight: bold; font-size: 35px; text-align: center; line-height: 2.5;
    box-shadow: 0px 15px 35px rgba(0,0,0,0.6);
}}

[data-testid="stForm"] {{
    max-width: 500px; margin: 0 auto; background-color: rgba(245, 240, 225, 0.95); 
    padding: 30px; border-radius: 15px; border: 2px solid #3e2723; 
}}

div.stButton > button {{
    background-color: #c2a382 !important; color: #3e2723 !important; 
    font-weight: bold !important; font-size: 22px !important; height: 55px !important; 
    border: 2px solid #3e2723 !important; border-radius: 8px !important;
}}

.action-box {{
    text-align: center; background: rgba(245, 240, 225, 0.95);
    padding: 25px; border-radius: 15px; max-width: 450px; margin: 20px auto; border: 2px solid #3e2723;
}}
</style>
''', unsafe_allow_html=True)

# --- 4. GUEST VIEW LOGIC (The Template) ---
# This checks if the URL has a poem inside it
query_params = st.query_params
if "poem" in query_params:
    # Decode the poem from the URL
    encoded_poem = query_params["poem"]
    decoded_poem = base64.b64decode(encoded_poem).decode('utf-8')
    
    st.markdown(f'<h1 class="main-title">Your Heritage Poem</h1>', unsafe_allow_html=True)
    st.markdown(f'<div class="poem-template">{decoded_poem.replace("\n", "<br>")}</div>', unsafe_allow_html=True)
    
    if st.button("Create Your Own Poem"):
        st.query_params.clear()
        st.rerun()
    st.stop() # Stops the rest of the app from loading for the guest

# --- 5. MAIN APP UI ---
st.markdown("<h1 class='main-title'>Foundation Day Poetry</h1>", unsafe_allow_html=True)

with st.form(key="poem_form"):
    user_prompt = st.text_input("Heritage Words / كلمات التراث:")
    language = st.selectbox("Language / اللغة:", ["Arabic", "English"])
    submit_button = st.form_submit_button("Generate")

if submit_button and user_prompt:
    with st.spinner("Writing..."):
        try:
            # AI Logic
            models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            model_name = next((m for m in models if "gemini-1.5-flash" in m), models[0])
            model = genai.GenerativeModel(model_name)
            
            prompt = f"Write a beautiful short poem about {user_prompt} for Saudi Foundation Day in {language}."
            response = model.generate_content(prompt)

            if response.text:
                poem_text = response.text.strip()
                st.markdown(f'<div class="poem-template">{poem_text.replace("\n", "<br>")}</div>', unsafe_allow_html=True)

                # --- 6. SMART QR CODE LOGIC ---
                # Encode the poem into the URL so the QR code carries the text
                encoded_for_url = base64.b64encode(poem_text.encode('utf-8')).decode('utf-8')
                base_url = "https://ai-poetry-lz3kfqnaegzlfbvnaluovg.streamlit.app"
                shareable_url = f"{base_url}/?poem={encoded_for_url}"
                
                st.markdown('<div class="action-box">', unsafe_allow_html=True)
                
                qr = qrcode.make(shareable_url)
                buf = BytesIO()
                qr.save(buf)
                st.image(buf, caption="Scan to see this poem on your phone!", width=250)
                st.markdown('</div>', unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Error: {e}")
