import streamlit as st
import google.generativeai as genai
from fpdf import FPDF
import qrcode
from io import BytesIO
import arabic_reshaper
from bidi.algorithm import get_display

# --- SETUP ---
GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
genai.configure(api_key=GOOGLE_API_KEY)

# --- PDF TEMPLATE FUNCTION ---
def create_pdf(text, lang):
    pdf = FPDF()
    pdf.add_page()
    
    # Add a border for the "Template" look
    pdf.set_line_width(1)
    pdf.rect(5, 5, 200, 287) 
    
    # Register Arabic Font
    pdf.add_font('Amiri', '', 'Amiri-Regular.ttf', uni=True)
    pdf.set_font('Amiri', size=25)
    
    # Reshape Arabic text
    if lang == "Arabic":
        reshaped = arabic_reshaper.reshape(text)
        display_text = get_display(reshaped)
        align = 'R'
    else:
        display_text = text
        align = 'C'
        
    pdf.multi_cell(0, 15, txt=display_text, align=align)
    return pdf.output(dest='S')

# --- UI ---
st.title("🇸🇦 Foundation Day Poetry")

user_input = st.text_input("Enter heritage words / أدخل كلمات التراث")
lang = st.selectbox("Language", ["Arabic", "English"])

if st.button("Generate Poem"):
    model = genai.GenerativeModel("gemini-1.5-flash")
    prompt = f"Write a short, beautiful poem about {user_input} for Saudi Foundation Day in {lang}."
    response = model.generate_content(prompt)
    
    poem = response.text
    st.markdown(f"### Your Poem:\n{poem}")
    
    # Create the PDF souvenir
    pdf_bytes = create_pdf(poem, lang)
    
    # Generate QR Code (Points to the Download)
    # Note: For a live QR code to work, the user usually needs to see the download button
    st.download_button("📩 Download Your Poem PDF", data=pdf_bytes, file_name="poem.pdf")
    
    # Create a QR that links to your app URL
    qr = qrcode.make("https://your-app-link.streamlit.app") 
    buf = BytesIO()
    qr.save(buf)
    st.image(buf, caption="Scan to share this app!")
