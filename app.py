import streamlit as st
import google.generativeai as genai
from fpdf import FPDF
import qrcode
from io import BytesIO
import arabic_reshaper
from bidi.algorithm import get_display

# --- 1. SETUP ---
# This pulls from your Streamlit Secrets
try:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=GOOGLE_API_KEY)
except:
    st.error("API Key missing! Please add GOOGLE_API_KEY to Streamlit Secrets.")

# --- 2. BEAUTIFUL HERITAGE UI ---
background_image = "https://i.pinimg.com/1200x/a3/8a/ca/a38acae15a962ecc7ab69d30dd42d5f3.jpg"

st.markdown(f"""
    <style>
    .stApp {{
        background-image: url("{background_image}");
        background-size: cover;
    }}
    .main-box {{
        background-color: rgba(245, 240, 225, 0.9);
        padding: 30px;
        border-radius: 15px;
        border: 2px solid #3e2723;
        color: #3e2723;
    }}
    h1 {{
        color: #f5f0e1 !important;
        text-shadow: 2px 2px 4px #000;
        text-align: center;
    }}
    div.stButton > button {{
        background-color: #c2a382 !important;
        color: white !important;
        width: 100%;
        font-weight: bold;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. PDF TEMPLATE FUNCTION ---
def create_pdf(text, lang):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_draw_color(62, 39, 35)
    pdf.set_line_width(2)
    pdf.rect(10, 10, 190, 277) # The Template Border
    
    try:
        pdf.add_font('Amiri', '', 'Amiri-Regular.ttf', uni=True)
        pdf.set_font('Amiri', size=25)
    except:
        pdf.set_font('Arial', size=20) # Fallback if font file is missing

    if lang == "Arabic":
        reshaped = arabic_reshaper.reshape(text)
        display_text = get_display(reshaped)
        pdf.multi_cell(0, 15, txt=display_text, align='R')
    else:
        pdf.multi_cell(0, 15, txt=text, align='C')
    return pdf.output(dest='S')

# --- 4. APP INTERFACE ---
st.markdown("<h1>Foundation Day Poetry</h1>", unsafe_allow_html=True)
st.markdown("<h1>قصيدة يوم التأسيس</h1>", unsafe_allow_html=True)

with st.container():
    st.markdown('<div class="main-box">', unsafe_allow_html=True)
    user_input = st.text_input("أدخل كلمات من التراث (مثل: الدرعية، فخر، عز):")
    lang = st.selectbox("Choose language / اختر اللغة:", ["Arabic", "English"])
    generate_btn = st.button("Generate Poem")
    st.markdown('</div>', unsafe_allow_html=True)

if generate_btn and user_input:
    with st.spinner("Writing..."):
        try:
            # Using the updated model name to fix the 'Not Found' error
            model = genai.GenerativeModel("gemini-1.5-flash-latest")
            prompt = f"Write a beautiful poem about {user_input} for Saudi Foundation Day in {lang}."
            response = model.generate_content(prompt)
            
            poem = response.text
            st.markdown(f"### Result:\n{poem}")
            
            # PDF and QR Code
            pdf_bytes = create_pdf(poem, lang)
            st.download_button("📩 Download PDF Souvenir", data=pdf_bytes, file_name="Foundation_Day_Poem.pdf")
            
            qr = qrcode.make(st.query_params.get("url", "https://share.streamlit.io/")) 
            buf = BytesIO()
            qr.save(buf)
            st.image(buf, caption="Scan to share!", width=200)
            
        except Exception as e:
            st.error(f"Generation Error: {e}")
