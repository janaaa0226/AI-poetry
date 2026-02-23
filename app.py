import streamlit as st
import google.generativeai as genai
from fpdf import FPDF
import qrcode
from io import BytesIO
import arabic_reshaper
from bidi.algorithm import get_display
import os

# --- 1. SETUP ---
try:
    # Using secrets for security as discussed
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=GOOGLE_API_KEY)
except:
    st.error("API Key missing! Add it to Streamlit Secrets.")

# --- 2. PAGE CONFIG ---
st.set_page_config(page_title="Foundation Day Poetry", layout="wide")

# --- 3. STYLING (Original UI structure with Improved Colors) ---
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
    text-shadow: 3px 3px 15px rgba(0, 0, 0, 0.7) !important; 
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

div.stTextInput > div > div > input, div.stSelectbox > div > div > div {{
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
    transition: 0.3s !important;
}}

div.stButton > button:hover {{
    background-color: #3e2723 !important;
    color: #c2a382 !important;
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

# --- 4. PDF ENGINE ---
def create_pdf(text, lang):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_draw_color(62, 39, 35)
    pdf.rect(10, 10, 190, 277)
    
    font_path = "Amiri-Regular.ttf"
    if os.path.exists(font_path):
        try:
            pdf.add_font('Amiri', '', font_path, uni=True)
            pdf.set_font('Amiri', size=25)
            if lang == "Arabic":
                text = get_display(arabic_reshaper.reshape(text))
                pdf.multi_cell(0, 15, txt=text, align='R')
            else:
                pdf.multi_cell(0, 15, txt=text, align='C')
        except:
            pdf.set_font('Arial', size=14)
    else:
        pdf.set_font('Arial', size=14)
    
    return bytes(pdf.output())

# --- 5. APP UI ---
st.markdown("<h1 class='main-title english-font'>Foundation Day Poetry</h1>", unsafe_allow_html=True)
st.markdown("<h1 class='main-title arabic-font'>قصيدة يوم التأسيس</h1>", unsafe_allow_html=True)

with st.form(key="poem_form"):
    user_prompt = st.text_input("أدخل كلمات من التراث (مثل: الدرعية، فخر، عز):")
    language = st.selectbox("Choose language / اختر اللغة:", ["Arabic", "English"])
    submit_button = st.form_submit_button("Generate")

# --- 6. GENERATION LOGIC ---
if submit_button and user_prompt:
    with st.spinner("Generating..."):
        try:
            available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            working_model_name = next((m for m in available_models if "gemini-1.5-flash" in m), available_models[0])

            model = genai.GenerativeModel(
                model_name=working_model_name,
                system_instruction="You are a master poet. If Arabic is requested, write a soul-touching Classical Fasiha. Provide ONLY the poem."
            )

            if language == "Arabic":
                full_prompt = f"نظم قصيدة فصيحة مذهلة ومؤثرة تلامس الروح عن {user_prompt} بمناسبة يوم التأسيس."
            else:
                full_prompt = f"Write an amazing, soul-touching, and elegant English poem about {user_prompt} for Saudi Foundation Day."

            response = model.generate_content(full_prompt)

            if response.text:
                direction = "rtl" if language == "Arabic" else "ltr"
                clean_poem = response.text.strip().replace("\n", "<br>")

                st.markdown(f'''
                    <div class="poem-container" style="direction: {direction};">
                        {clean_poem}
                    </div>
                ''', unsafe_allow_html=True)

                # Action Box for PDF and QR
                pdf_bytes = create_pdf(response.text.strip(), language)
                
                st.markdown('<div class="action-box">', unsafe_allow_html=True)
                st.download_button("📩 Download PDF Souvenir", data=pdf_bytes, file_name="Poem.pdf", mime="application/pdf")
                
                qr_url = "https://ai-poetry-lz3kfqnaegzlfbvnaluovg.streamlit.app"
                qr = qrcode.make(qr_url)
                buf = BytesIO()
                qr.save(buf)
                st.image(buf, caption="Scan to share!", width=200)
                st.markdown('</div>', unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Error: {e}")
