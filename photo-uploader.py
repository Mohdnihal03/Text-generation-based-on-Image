import streamlit as st
from PIL import Image
import traceback
from dataclasses import dataclass
from typing import List
from libs.logger import Logger
from libs.gemini_vision import GeminiVision

# Define data class for text suggestions
@dataclass
class BannerTextSuggestion:
    text: str
    position: str
    styling: dict
    reasoning: str

# Define BannerAnalyzer class
class BannerAnalyzer:
    def __init__(self, api_key: str, temperature: float = 0.3):
        self.gemini = GeminiVision(api_key, temperature)
        self.logger = Logger.get_logger('banner_analyzer.log')
        
    def analyze_banner(self, image, prompt: str = None) -> List[BannerTextSuggestion]:
        """Analyze banner image and suggest text placements."""
        try:
            default_prompt = """
            Analyze this banner image and suggest optimal text placements. Consider:
            1. Best locations for headlines, subheadings, and body text
            2. Recommended text styling (size, color, font weight)
            3. Areas with good contrast for text
            4. Balanced composition
            Provide specific placement suggestions with reasoning.
            """
            
            analysis_prompt = prompt if prompt else default_prompt
            image_contents = [analysis_prompt, image]
            
            response = self.gemini.generate_content(image_contents)
            return self._parse_suggestions(response.text)
            
        except Exception as e:
            self.logger.error(f"Error analyzing banner: {str(e)}")
            raise

    def _parse_suggestions(self, gemini_response: str) -> List[BannerTextSuggestion]:
        """Parse Gemini's response into structured suggestions."""
        try:
            suggestions = []
            sections = gemini_response.split('\n\n')
            for section in sections:
                if not section.strip():
                    continue
                lines = section.split('\n')
                if len(lines) < 3:
                    continue
                suggestion = BannerTextSuggestion(
                    text=lines[0].replace('Text: ', '').strip(),
                    position=lines[1].replace('Position: ', '').strip(),
                    styling={'size': 'default', 'color': 'default', 'weight': 'normal'},
                    reasoning=lines[-1].strip()
                )
                for line in lines:
                    if 'style:' in line.lower():
                        style_parts = line.split(':')[1].strip().split(',')
                        for part in style_parts:
                            key, value = part.strip().split('=')
                            suggestion.styling[key.strip()] = value.strip()
                suggestions.append(suggestion)
            return suggestions
        except Exception as e:
            self.logger.error(f"Error parsing suggestions: {str(e)}")
            return []

def init_session_state():
    """Initialize session state variables."""
    if 'api_key' not in st.session_state:
        st.session_state['api_key'] = ''
    if 'analyzer' not in st.session_state:
        st.session_state['analyzer'] = None
    if 'banner_image' not in st.session_state:
        st.session_state['banner_image'] = None
    if 'suggestions' not in st.session_state:
        st.session_state['suggestions'] = None

def main():
    # Set app title
    st.title("Photo Uploader & Banner Text Placement Analyzer")
    
    init_session_state()
    
    # Section for photo upload
    st.subheader("Photo Uploader")
    uploaded_file = st.file_uploader("Upload a photo", type=["jpg", "jpeg", "png"], key="photo_uploader")
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Photo", use_column_width=True)
        st.write("Image Details:")
        st.write(f"Format: {image.format}")
        st.write(f"Size: {image.size}")
        st.write(f"Mode: {image.mode}")
    else:
        st.write("Please upload a photo to continue.")
    
    # Section for banner analysis
    st.subheader("Banner Text Placement Analyzer")
    
    # Sidebar for API key
    with st.sidebar:
        api_key = st.text_input("Gemini API Key", type="password", value=st.session_state['api_key'])
        if api_key != st.session_state['api_key']:
            st.session_state['api_key'] = api_key
            if api_key:
                st.session_state['analyzer'] = BannerAnalyzer(api_key)
    
    # Banner image upload and analysis
    banner_file = st.file_uploader("Upload a banner image for analysis", type=['png', 'jpg', 'jpeg'], key="banner_uploader")
    if banner_file and st.session_state['api_key']:
        try:
            banner_image = Image.open(banner_file)
            st.image(banner_image, caption="Uploaded Banner", use_column_width=True)
            custom_prompt = st.text_area(
                "Custom Analysis Prompt (optional)",
                placeholder="Leave empty for default analysis"
            )
            if st.button("Analyze Banner"):
                with st.spinner("Analyzing banner..."):
                    suggestions = st.session_state['analyzer'].analyze_banner(
                        banner_image, 
                        custom_prompt if custom_prompt else None
                    )
                    st.subheader("Text Placement Suggestions")
                    for i, suggestion in enumerate(suggestions, 1):
                        with st.expander(f"Suggestion {i}: {suggestion.text[:30]}..."):
                            st.write(f"**Position:** {suggestion.position}")
                            st.write("**Styling:**")
                            for key, value in suggestion.styling.items():
                                st.write(f"- {key}: {value}")
                            st.write(f"**Reasoning:** {suggestion.reasoning}")
        except Exception as e:
            st.error(f"Error processing banner: {str(e)}")
            st.session_state['analyzer'].logger.error(traceback.format_exc())

if __name__ == "__main__":
    main()
