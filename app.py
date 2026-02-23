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
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=GOOGLE_API_KEY)
except:
    st.error("API Key missing! Add it to Streamlit Secrets.")

# --- 2. PAGE CONFIG ---
st.set_page_config(page_title="Foundation Day Poetry", layout="wide")

# --- 3. STYLING ---
background_image_url = "https://i.pinimg.com/1200x/a3/8a/ca/a38acae15a962ecc7ab69d30dd42d5f3.jpg"

st.markdown(f'''
<style>
@import url('https://fonts.googleapis.com/css2?family=Amiri:wght@700&family=Playfair+Display:wght@700&display=swap');
header {{visibility: hidden;}}
.stApp {{ background-image: url("{background_image_url}"); background-size: cover; background-attachment: fixed; }}
.main-title {{
    font-size: 65px !important; font-weight: 700 !important; text-align: center !important;
    color: #f5f0e1 !important; text-shadow: 3px 3px 15px rgba(0,0,0,0.8) !important; 
}}
.english-font {{ font-family: 'Playfair Display', serif !important; }}
.arabic-font {{ font-family: 'Amiri', serif !important; }}
[data-testid="stForm"] {{
    max-width: 550px; margin: 0 auto; background-color: rgba(245, 240, 225, 0.95); 
    padding: 30px; border-radius: 15px; border: 2px solid #3e2723; 
}}
.poem-container {{
    background-color: rgba(245, 240, 225, 0.93); padding: 40px; border-radius: 15px; 
    border: 3px double #3e2723; max-width: 750px; margin: 30px auto;
    color: #3e2723 !important; font-family: 'Amiri', serif; 
    font-weight: bold; font-size: 32px; text-align: center; line-height: 2.2;
}}
.action-box {{
    text-align: center; background: rgba(245, 240, 225, 0.95);
    padding: 25px; border-radius: 15px; max-width: 450px; margin: 20px auto; border: 2px solid #3e2723;
}}
</style>
''', unsafe_allow_html=True)

# --- 4. PDF FUNCTION (FIXED BINARY FORMAT) ---
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
            pdf.cell(0, 10, "Arabic Font Error. Check App Screen.", ln=True)
    else:
        pdf.set_font('Arial', size=14)
        pdf.cell(0, 10, "Font file missing. Check App Screen.", ln=True)
    
    # FIX: Convert to Bytes so Streamlit can download it
    return bytes(pdf.output())

# --- 5. UI ---
st.markdown("<h1 class='main-title english-font'>Foundation Day Poetry</h1>", unsafe_allow_html=True)
st.markdown("<h1 class='main-title arabic-font'>قصيدة يوم التأسيس</h1>", unsafe_allow_html=True)

with st.form(key="poem_form"):
    user_prompt = st.text_input("Heritage Words / كلمات التراث:")
    language = st.selectbox("Language / اللغة:", ["Arabic", "English"])
    submit_button = st.form_submit_button("Generate / ابدأ")

# --- 6. LOGIC ---
if submit_button and user_prompt:
    with st.spinner("Writing..."):
        try:
            # AUTO-FIND MODEL
            models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            model_name = next((m for m in models if "gemini-1.5-flash" in m), models[0])
            model = genai.GenerativeModel(model_name)
            
            prompt = f"Write a beautiful poem about {user_prompt} for Saudi Foundation Day in {language}."
            response = model.generate_content(prompt)

            if response.text:
                poem_text = response.text.strip()
                dir_css = "rtl" if language == "Arabic" else "ltr"
                st.markdown(f'<div class="poem-container" style="direction: {dir_css};">{poem_text.replace("\n", "<br>")}</div>', unsafe_allow_html=True)

                # Action Box
                pdf_bytes = create_pdf(poem_text, language)
                
                st.markdown('<div class="action-box">', unsafe_allow_html=True)
                st.download_button("📩 Download PDF Souvenir", data=pdf_bytes, file_name="Poem.pdf", mime="application/pdf")
                
                # QR CODE
                qr_url = "https://ai-poetry-lz3kfqnaegzlfbvnaluovg.streamlit.app"
                qr = qrcode.QRCode(box_size=10, border=4)
                qr.add_data(qr_url)
                qr.make(fit=True)
                img = qr.make_image(fill_color="#3e2723", back_color="white")
                
                buf = BytesIO()
                img.save(buf, format="PNG")
                st.image(buf, caption="Scan to share!", width=200)
                st.markdown('</div>', unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Error during generation: {e}")

