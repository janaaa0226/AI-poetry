import streamlit as st
import google.generativeai as genai
from fpdf import FPDF
import qrcode
from io import BytesIO
import arabic_reshaper
from bidi.algorithm import get_display
import os

# --- 1. API SETUP ---
try:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=GOOGLE_API_KEY)
except Exception as e:
    st.error("Missing GOOGLE_API_KEY in Streamlit Secrets!")

# --- 2. PAGE CONFIG ---
st.set_page_config(page_title="Saudi Foundation Day Poetry", layout="wide")

# --- 3. FULL HERITAGE CSS (Your Original Design) ---
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
    color: #f5f0e1 !important; text-shadow: 3px 3px 15px rgba(0,0,0,0.8) !important; 
    margin: 10px 0px !important; line-height: 1.2 !important;
}}

.english-font {{ font-family: 'Playfair Display', serif !important; }}
.arabic-font {{ font-family: 'Amiri', serif !important; }}

[data-testid="stForm"] {{
    max-width: 550px; margin: 0 auto; background-color: rgba(245, 240, 225, 0.95); 
    padding: 30px; border-radius: 15px; border: 2px solid #3e2723; 
    box-shadow: 0px 8px 25px rgba(0,0,0,0.3);
}}

[data-testid="stWidgetLabel"] p {{
    color: #3e2723 !important; font-weight: bold !important;
    font-size: 22px !important; font-family: 'Amiri', serif !important; text-align: right;
}}

div.stTextInput > div > div > input, div.stSelectbox > div > div > div {{
    background-color: #c2a382 !important; color: #3e2723 !important; 
    border-radius: 8px !important; border: 2px solid #3e2723 !important; 
    font-weight: bold !important; height: 45px;
}}

div.stButton > button {{
    background-color: #c2a382 !important; color: #3e2723 !important; 
    width: 100% !important; font-weight: bold !important; font-size: 24px !important;
    font-family: 'Amiri', serif !important; height: 60px !important; 
    border: 2px solid #3e2723 !important; border-radius: 8px !important;
}}

.poem-container {{
    background-color: rgba(245, 240, 225, 0.93); padding: 40px; border-radius: 15px; 
    border: 3px double #3e2723; max-width: 750px; margin: 30px auto;
    color: #3e2723 !important; font-family: 'Amiri', serif; 
    font-weight: bold; font-size: 32px; text-align: center; line-height: 2.2;
    box-shadow: 0px 10px 25px rgba(0,0,0,0.5);
}}

.action-box {{
    text-align: center; background: rgba(245, 240, 225, 0.95);
    padding: 25px; border-radius: 15px; max-width: 450px; margin: 20px auto;
    border: 2px solid #3e2723;
}}
</style>
''', unsafe_allow_html=True)

# --- 4. PDF ENGINE (UNICODE SAFE) ---
def create_pdf(text, lang):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_draw_color(62, 39, 35)
    pdf.set_line_width(2)
    pdf.rect(10, 10, 190, 277) # Heritage Border
    
    font_path = "Amiri-Regular.ttf"
    if os.path.exists(font_path):
        try:
            pdf.add_font('Amiri', '', font_path, uni=True)
            pdf.set_font('Amiri', size=25)
            if lang == "Arabic":
                reshaped = arabic_reshaper.reshape(text)
                display_text = get_display(reshaped)
                pdf.multi_cell(0, 15, txt=display_text, align='R')
            else:
                pdf.multi_cell(0, 15, txt=text, align='C')
            return pdf.output(dest='S')
        except:
            pass
    
    # Fallback if font is missing to prevent crashing the whole app
    pdf.set_font('Arial', size=16)
    pdf.multi_cell(0, 10, txt="To view your poem in full Arabic calligraphy, please scan the QR code on the screen.", align='C')
    return pdf.output(dest='S')

# --- 5. UI CONTENT ---
st.markdown("<h1 class='main-title english-font'>Foundation Day Poetry</h1>", unsafe_allow_html=True)
st.markdown("<h1 class='main-title arabic-font'>قصيدة يوم التأسيس</h1>", unsafe_allow_html=True)

with st.form(key="poem_form"):
    user_prompt = st.text_input("أدخل كلمات من التراث (مثلاً: الدرعية، فخر، عز):")
    language = st.selectbox("Language / اللغة:", ["Arabic", "English"])
    submit_button = st.form_submit_button("Generating ")

# --- 6. LOGIC & GENERATION ---
if submit_button and user_prompt:
    with st.spinner("Writing your poem..."):
        try:
            # FIX: Automatic Model Selection to avoid 404
            models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            model_to_use = next((m for m in models if "gemini-1.5-flash" in m), models[0])
            
            model = genai.GenerativeModel(
                model_name=model_to_use,
                system_instruction="You are a master poet. For Arabic, use Classical Fasiha. For English, use elegant, sophisticated verse. Focus on Saudi Heritage."
            )

            if language == "Arabic":
                full_prompt = f"نظم قصيدة فصيحة مذهلة ومؤثرة تلامس الروح عن {user_prompt} بمناسبة يوم التأسيس."
            else:
                full_prompt = f"Write an amazing, soul-touching, and elegant English poem about {user_prompt} for Saudi Foundation Day."

            response = model.generate_content(full_prompt)

            if response.text:
                poem_text = response.text.strip()
                direction = "rtl" if language == "Arabic" else "ltr"
                
                # Display the poem on screen
                st.markdown(f'<div class="poem-container" style="direction: {direction};">{poem_text.replace("\n", "<br>")}</div>', unsafe_allow_html=True)

                # Generate Souvenir PDF
                pdf_bytes = create_pdf(poem_text, language)
                
                # Action Box for QR and Download
                st.markdown('<div class="action-box">', unsafe_allow_html=True)
                st.download_button("📩 Download PDF Souvenir", data=pdf_bytes, file_name="Foundation_Day_Poem.pdf")
                
                # QR Code Generation (Using your live URL)
                qr_url = "https://ai-poetry-lz3kfqnaegzlfbvnaluovg.streamlit.app"
                qr = qrcode.QRCode(version=1, box_size=10, border=4)
                qr.add_data(qr_url)
                qr.make(fit=True)
                
                img_qr = qr.make_image(fill_color="#3e2723", back_color="white")
                buf = BytesIO()
                img_qr.save(buf, format="PNG")
                
                st.image(buf, caption="Scan to share with others!", width=250)
                st.markdown('</div>', unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Error during generation: {e}")
