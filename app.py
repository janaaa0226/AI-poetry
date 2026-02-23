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
    st.error("API Key missing! Add it to Streamlit Secrets.")

# --- 2. PAGE CONFIG ---
st.set_page_config(page_title="Foundation Day Poetry", layout="wide")

# --- 3. THE ORIGINAL HERITAGE UI ---
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
    font-size: 65px !important;
    font-weight: 700 !important;
    text-align: center !important;
    color: #f5f0e1 !important; 
    text-shadow: 3px 3px 15px rgba(194, 163, 130, 0.9) !important; 
    margin: 10px 0px !important;
    line-height: 1.2 !important;
}}

.english-font {{ font-family: 'Playfair Display', serif !important; }}
.arabic-font {{ font-family: 'Amiri', serif !important; }}

[data-testid="stForm"] {{
    max-width: 500px; 
    margin: 0 auto; 
    background-color: rgba(245, 240, 225, 0.95); 
    padding: 30px; 
    border-radius: 15px; 
    border: 2px solid #3e2723; 
    box-shadow: 0px 8px 25px rgba(0,0,0,0.3);
}}

[data-testid="stWidgetLabel"] p {{
    color: #3e2723 !important; 
    font-weight: bold !important;
    font-size: 22px !important; 
    font-family: 'Amiri', serif !important;
    text-align: right;
}}

div.stTextInput > div > input, div.stSelectbox > div > div > div {{
    background-color: #c2a382 !important; 
    color: #3e2723 !important; 
    border-radius: 8px !important; 
    border: 2px solid #3e2723 !important; 
    font-weight: bold !important; 
    height: 45px;
}}

div.stButton > button {{
    background-color: #c2a382 !important; 
    color: #3e2723 !important; 
    width: 100% !important; 
    font-weight: bold !important; 
    font-size: 22px !important;
    font-family: 'Amiri', serif !important;
    height: 55px !important; 
    border: 2px solid #3e2723 !important; 
    border-radius: 8px !important;
}}

.poem-container {{
    background-color: rgba(245, 240, 225, 0.93); 
    padding: 40px; border-radius: 15px; border: 3px double #3e2723;
    max-width: 750px; margin: 30px auto;
    color: #3e2723 !important; 
    font-family: 'Amiri', serif; 
    font-weight: bold; font-size: 30px;
    text-align: center; line-height: 2.2;
    box-shadow: 0px 10px 25px rgba(0,0,0,0.5);
}}

.action-box {{
    text-align: center; 
    background: rgba(245, 240, 225, 0.95);
    padding: 25px; border-radius: 15px; 
    max-width: 450px; margin: 20px auto;
    border: 2px solid #3e2723;
}}
</style>
''', unsafe_allow_html=True)

# --- 4. GUEST TEMPLATE LOGIC ---
query_params = st.query_params
if "poem" in query_params:
    try:
        encoded_poem = query_params["poem"]
        decoded_poem = base64.b64decode(encoded_poem).decode('utf-8')
        
        # Display ONLY the poem on the Heritage background
        st.markdown(f'<div class="poem-container" style="margin-top: 100px;">{decoded_poem.replace("\n", "<br>")}</div>', unsafe_allow_html=True)
        
        if st.button("Create Your Own Poem / أنشئ قصيدتك"):
            st.query_params.clear()
            st.rerun()
        st.stop()
    except:
        st.query_params.clear()
        st.rerun()

# --- 5. MAIN APP UI ---
st.markdown("<h1 class='main-title english-font'>Foundation Day Poetry</h1>", unsafe_allow_html=True)
st.markdown("<h1 class='main-title arabic-font'>قصيدة يوم التأسيس</h1>", unsafe_allow_html=True)

with st.form(key="poem_form"):
    user_prompt = st.text_input("أدخل كلمات من التراث (مثل: الدرعية، فخر، عز):")
    language = st.selectbox("Choose language / اختر اللغة:", ["Arabic", "English"])
    submit_button = st.form_submit_button("Generate")

# --- 6. GENERATION & QR LOGIC ---
if submit_button and user_prompt:
    with st.spinner("Generating..."):
        try:
            available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            working_model_name = next((m for m in available_models if "gemini-1.5-flash" in m), available_models[0])

            model = genai.GenerativeModel(model_name=working_model_name)

            if language == "Arabic":
                full_prompt = f"نظم قصيدة فصيحة مذهلة ومؤثرة تلامس الروح عن {user_prompt} بمناسبة يوم التأسيس."
            else:
                full_prompt = f"Write an amazing, soul-touching, and elegant English poem about {user_prompt} for Saudi Foundation Day."

            response = model.generate_content(full_prompt)

            if response.text:
                poem_text = response.text.strip()
                st.markdown(f'<div class="poem-container">{poem_text.replace("\n", "<br>")}</div>', unsafe_allow_html=True)

                # Generate the Unique Shareable Link
                encoded_poem = base64.b64encode(poem_text.encode('utf-8')).decode('utf-8')
                app_url = "https://ai-poetry-lz3kfqnaegzlfbvnaluovg.streamlit.app"
                share_link = f"{app_url}/?poem={encoded_poem}"

                # Action Box
                st.markdown('<div class="action-box">', unsafe_allow_html=True)
                
                qr = qrcode.make(share_link)
                buf = BytesIO()
                qr.save(buf)
                st.image(buf, caption="Scan to see this poem on your phone!", width=200)
                st.markdown('</div>', unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Error: {e}")
