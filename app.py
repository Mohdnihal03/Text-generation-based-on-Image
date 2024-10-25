import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

# Configure the API key
GOOGLE_API_KEY = "AIzaSyB5YNQHPvA2Xe0_5dqUCh4SpNKAxlFXs9M"
genai.configure(api_key=GOOGLE_API_KEY)

# Initialize the Generative Model
model = genai.GenerativeModel('gemini-1.5-flash')

def encode_image(image):
    # Convert PIL image to bytes
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    image_bytes = buffered.getvalue()
    # Encode to base64
    image_b64 = base64.b64encode(image_bytes).decode('utf-8')
    return image_b64

def analyze_image_and_suggest_text(image, brand_info):
    try:
        # Convert image to RGB mode if it's not
        if image.mode != 'RGB':
            image = image.convert('RGB')
            
        # Encode image to base64
        image_data = {
            "mime_type": "image/jpeg",
            "data": encode_image(image)
        }
        
        prompt = f"""
        Analyze this banner image and suggest text placement with the following details:
        1. Header text (suggest text and placement - top left/center/right)
        2. Main promotional text (suggest text and placement)
        3. Footer/CTA text (suggest text and placement)
        4. Color suggestions that complement the image
        
        Brand Information: {brand_info}
        
        Provide suggestions in a structured format considering:
        - Image composition and focal points
        - Color balance
        - Visual hierarchy
        - White space availability
        """
        
        response = model.generate_content([prompt, image_data])
        return response.text
    except Exception as e:
        return f"Error analyzing image: {str(e)}"

def get_text_suggestions(text_type, brand_info):
    prompt = f"Generate compelling {text_type} text for a banner advertisement for: {brand_info}"
    response = model.generate_content(prompt)
    return response.text

# Streamlit interface
st.set_page_config(page_title="Banner Text Suggester", layout="wide")
st.title("🎨 Banner Text Placement Suggester")
st.write("Upload a banner image to get AI-powered suggestions for text placement and content")

# Sidebar for brand information
with st.sidebar:
    st.header("Brand Information")
    brand_name = st.text_input("Brand Name")
    industry = st.text_input("Industry")
    target_audience = st.text_input("Target Audience")
    campaign_objective = st.text_area("Campaign Objective")
    
    brand_info = f"""
    Brand: {brand_name}
    Industry: {industry}
    Target Audience: {target_audience}
    Campaign Objective: {campaign_objective}
    """

# Main content area
col1, col2 = st.columns([2, 3])

with col1:
    st.subheader("Upload Banner Image")
    uploaded_file = st.file_uploader("Choose an image...", type=['png', 'jpg', 'jpeg'])
    
    if uploaded_file is not None:
        # Open and display the image
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Banner", use_column_width=True)

with col2:
    if uploaded_file is not None and all([brand_name, industry, target_audience, campaign_objective]):
        st.subheader("AI Suggestions")
        
        # Get comprehensive suggestions using the PIL Image directly
        with st.spinner("Analyzing image and generating suggestions..."):
            suggestions = analyze_image_and_suggest_text(image, brand_info)
            st.markdown("### 📍 Placement Suggestions")
            st.write(suggestions)
            
        # Individual text element generation
        with st.expander("Generate Specific Text Elements"):
            if st.button("Generate Header Options"):
                header_suggestions = get_text_suggestions("header", brand_info)
                st.markdown("### Header Options")
                st.write(header_suggestions)
                
            if st.button("Generate Main Text Options"):
                main_text_suggestions = get_text_suggestions("main promotional", brand_info)
                st.markdown("### Main Text Options")
                st.write(main_text_suggestions)
                
            if st.button("Generate CTA Options"):
                cta_suggestions = get_text_suggestions("call-to-action", brand_info)
                st.markdown("### CTA Options")
                st.write(cta_suggestions)
    else:
        st.info("Please upload an image and fill in all brand information to get suggestions.")

# Display usage instructions
with st.expander("How to Use"):
    st.markdown("""
    1. Fill in your brand information in the sidebar
    2. Upload your banner image
    3. Get AI-powered suggestions for:
        - Text placement
        - Color combinations
        - Content recommendations
    4. Use the expander section to generate specific text elements
    """)

# Add CSS for better visual hierarchy
st.markdown("""
<style>
    .stExpander {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 10px;
    }
    .stButton>button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)