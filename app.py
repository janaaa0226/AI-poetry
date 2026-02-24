import streamlit as st
import google.generativeai as genai
import qrcode
from io import BytesIO
import base64

# SETUP 
try:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=GOOGLE_API_KEY)
except:
    st.error("API Key missing! Add it to Streamlit Secrets.")

#  PAGE CONFIG 
st.set_page_config(page_title="Foundation Day Poetry", layout="wide")

#  UI 
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
    margin: 10px 0px !important; line-height: 1.2 !important;
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

[data-testid="stWidgetLabel"] p {{ color: #2b1d0e !important; font-weight: 900 !important; }}

div.stTextInput > div > div > input, div.stSelectbox > div > div > div {{
    background-color: #a68b6a !important; color: #ffffff !important; 
    border-radius: 8px !important; border: 2px solid #3e2723 !important; font-weight: bold !important;
}}

div.stButton > button {{
    background-color: #3e2723 !important; color: #f5f0e1 !important; 
    font-weight: bold !important; font-size: 22px !important; height: 55px !important; 
    border: 2px solid #3e2723 !important; border-radius: 8px !important;
}}

.action-box {{
    text-align: center; background: rgba(245, 240, 225, 0.95);
    padding: 25px; border-radius: 15px; max-width: 450px; margin: 20px auto; border: 2px solid #3e2723;
}}
</style>
''', unsafe_allow_html=True)

# GUEST VIEW LOGIC 
query_params = st.query_params
if "poem" in query_params:
    try:
        encoded_poem = query_params["poem"]
        decoded_poem = base64.b64decode(encoded_poem).decode('utf-8')
        st.markdown(f'<div class="poem-template" style="margin-top:100px;">{decoded_poem.replace("\n", "<br>")}</div>', unsafe_allow_html=True)
        if st.button("Create Your Own Poem / أنشئ قصيدتك"):
            st.query_params.clear()
            st.rerun()
        st.stop()
    except:
        st.query_params.clear()
        st.rerun()

#  MAIN APP UI 
st.markdown("<h1 class='main-title'>Foundation Day Poetry</h1>", unsafe_allow_html=True)
st.markdown("<h1 class='main-title' style='font-family:Amiri; font-size:55px !important;'>قصيدة يوم التأسيس</h1>", unsafe_allow_html=True)

with st.form(key="poem_form"):
    user_prompt = st.text_input("أدخل كلمات من التراث (مثل: الدرعية، فخر، عز):")
    language = st.selectbox("Choose language / اختر اللغة:", ["Arabic", "English"])
    submit_button = st.form_submit_button("Generate")

# THE SMART LOGIC (AUTO-SELECTS MODEL) 
if submit_button and user_prompt:
    with st.spinner("Writing..."):
        try:
            # 1. FIND MODELS 
            available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            
            # 2. PICK THE BEST: Look for 1.5-flash first (high limit), then 1.5-pro  then anything else.
            best_model = next((m for m in available_models if "1.5-flash" in m), 
                         next((m for m in available_models if "1.5-pro" in m), 
                         available_models[0]))
            
            model = genai.GenerativeModel(best_model)
            
            prompt = f"Write a short poem about {user_prompt} for Saudi Foundation Day. Use ONLY the {language} language. No translations."
            response = model.generate_content(prompt)

            if response.text:
                poem_text = response.text.strip()
                st.markdown(f'<div class="poem-template">{poem_text.replace("\n", "<br>")}</div>', unsafe_allow_html=True)

                encoded_for_url = base64.b64encode(poem_text.encode('utf-8')).decode('utf-8')
                shareable_url = f"https://ai-poetry-lz3kfqnaegzlfbvnaluovg.streamlit.app/?poem={encoded_for_url}"
                
                st.markdown('<div class="action-box">', unsafe_allow_html=True)
                qr = qrcode.make(shareable_url)
                buf = BytesIO()
                qr.save(buf)
                st.image(buf, caption="Scan to see this poem on your phone!", width=250)
                st.markdown('</div>', unsafe_allow_html=True)

        except Exception as e:
            if "429" in str(e):
                st.error("Too many poems at once! Please wait 30 seconds and try again.")
            else:
                st.error(f"Error: {e}")
