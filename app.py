import streamlit as st
import google.generativeai as genai
from fpdf import FPDF
import qrcode
from io import BytesIO
import uuid
import arabic_reshaper
from bidi.algorithm import get_display

# --- 1. SETUP API KEY ---
# Note: Later we can move this to "Secrets" for better security!
GOOGLE_API_KEY = "AIzaSyDWnxDreHF4lo5vRIuhifTRknEzC1DOpNE"
genai.configure(api_key=GOOGLE_API_KEY)

# --- 2. PAGE CONFIG ---
st.set_page_config(page_title="Foundation Day Poetry", layout="wide")

# --- 3. STYLING (Hiding UI + Heritage Theme) ---
background_image_url = "https://i.pinimg.com/1200x/a3/8a/ca/a38acae15a962ecc7ab69d30dd42d5f3.jpg"

st.markdown(f'''
<style>
@import url('https://fonts.googleapis.com/css2?family=Amiri:wght@700&family=Playfair+Display:wght@700&display=swap');

/* Hides the top bar and deploy button */
header {{visibility: hidden;}}
#MainMenu {{visibility: hidden;}}
footer {{visibility: hidden;}}
div.stDeployButton {{display:none;}}

.stApp {{ background-image: url("{background_image_url}"); background-size: cover; background-attachment: fixed; }}

.main-title {{
    font-size: 65px !important; font-weight: 700 !important; text-align: center !important;
    color: #f5f0e1 !important; text-shadow: 3px 3px 15px rgba(194, 163, 130, 0.9) !important;
    margin: 10px 0px !important; line-height: 1.2 !important;
}}

.english-font {{ font-family: 'Playfair Display', serif !important; }}
.arabic-font {{ font-family: 'Amiri', serif !important; }}

[data-testid="stForm"] {{
    max-width: 500px; margin: 0 auto; background-color: rgba(245, 240, 225, 0.95); 
    padding: 30px; border-radius: 15px; border: 2px solid #3e2723; 
    box-shadow: 0px 8px 25px rgba(0,0,0,0.3);
}}

[data-testid="stWidgetLabel"] p {{
    color: #3e2723 !important; font-weight: bold !important; font-size: 22px !important; 
    font-family: 'Amiri', serif !important; text-align: right;
}}

/* Input boxes & Select box color match */
div.stTextInput > div > div > input, div.stSelectbox > div > div > div {{
    background-color: #c2a382 !important; color: #3e2723 !important; 
    border-radius: 8px !important; border: 2px solid #3e2723 !important; 
    font-weight: bold !important; height: 45px;
}}

/* Generate button forced color match */
div.stButton > button {{
    background-color: #c2a382 !important; color: #3e2723 !important; 
    width: 100% !important; font-weight: bold !important; font-size: 22px !important;
    font-family: 'Amiri', serif !important; height: 55px !important; 
    border: 2px solid #3e2723 !important; border-radius: 8px !important;
    transition: 0.3s !important;
}}

div.stButton > button:hover {{
    background-color: #3e2723 !important;
    color: #c2a382 !important;
}}

.poem-container {{
    background-color: rgba(245, 240, 225, 0.93); padding: 40px; border-radius: 15px; border: 3px double #3e2723;
    max-width: 750px; margin: 30px auto; color: #3e2723 !important; 
    font-family: 'Amiri', serif; font-weight: bold; font-size: 30px;
    text-align: center; line-height: 2.2; box-shadow: 0px 10px 25px rgba(0,0,0,0.5);
}}

.qr-box {{
    background: white; padding: 15px; border-radius: 10px; border: 2px solid #3e2723;
    text-align: center; width: fit-content; margin: 20px auto;
}}
</style>
''', unsafe_allow_html=True)

# --- 4. APP UI ---
st.markdown("<h1 class='main-title english-font'>Foundation Day Poetry</h1>", unsafe_allow_html=True)
st.markdown("<h1 class='main-title arabic-font'>قصيدة يوم التأسيس</h1>", unsafe_allow_html=True)

with st.form(key="poem_form"):
    user_prompt = st.text_input("أدخل كلمات من التراث (مثل: الدرعية، فخر، عز):")
    language = st.selectbox("Choose language / اختر اللغة:", ["Arabic", "English"])
    submit_button = st.form_submit_button("Generate")

# --- 5. LOGIC ---
if submit_button and user_prompt:
    with st.spinner("Writing your poem..."):
        try:
            model = genai.GenerativeModel(model_name="gemini-1.5-flash")
            
            if language == "Arabic":
                full_prompt = f"نظم قصيدة فصيحة مذهلة ومؤثرة تلامس الروح عن {user_prompt} بمناسبة يوم التأسيس."
            else:
                full_prompt = f"Write an amazing, soul-touching, and elegant English poem about {user_prompt} for Saudi Foundation Day."

            response = model.generate_content(full_prompt)

            if response.text:
                poem_text = response.text.strip()
                
                # Show on Screen
                direction = "rtl" if language == "Arabic" else "ltr"
                st.markdown(f'<div class="poem-container" style="direction: {direction};">{poem_text.replace("\n", "<br>")}</div>', unsafe_allow_html=True)

                # --- PDF GENERATION ---
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", size=16) 
                
                # Fix Arabic text for PDF
                if language == "Arabic":
                    reshaped_text = arabic_reshaper.reshape(poem_text)
                    display_text = get_display(reshaped_text)
                else:
                    display_text = poem_text
                
                pdf.multi_cell(0, 10, txt=display_text, align='C')
                pdf_data = pdf.output()
                unique_id = str(uuid.uuid4())[:8]

                # --- QR CODE ---
                # This links back to the app itself as a placeholder
                qr_url = f"https://foundation-day-poetry.streamlit.app/?id={unique_id}"
                
                qr = qrcode.make(qr_url)
                buf = BytesIO()
                qr.save(buf)

                st.markdown("<div class='qr-box'>", unsafe_allow_html=True)
                st.image(buf, caption="Scan to share your poem!", width=200)
                st.markdown("</div>", unsafe_allow_html=True)

                st.download_button(
                    label="Download PDF Poem",
                    data=pdf_data,
                    file_name=f"FoundationDay_Poem_{unique_id}.pdf",
                    mime="application/pdf"
                )

        except Exception as e:
            st.error(f"Error: {e}")
