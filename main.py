import os
from PIL import Image
import streamlit as st
from streamlit_option_menu import option_menu
import time
from google.api_core import retry
from google.api_core import exceptions
from dotenv import load_dotenv
import platform
import google.generativeai as genai

# Set page config at the very beginning
st.set_page_config(
    page_title="AI Math Solver",
    page_icon="🧮",
    layout="centered",
)

import pytesseract

# Load environment variables
load_dotenv()

# working directory path
working_dir = os.path.dirname(os.path.abspath(__file__))

# Get API key from environment variable
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
if not GOOGLE_API_KEY:
    st.error("""
    Please set the GOOGLE_API_KEY environment variable in the .env file.
    Create a .env file in the project root with:
    GOOGLE_API_KEY=your_api_key_here
    """)
    st.stop()

# Configure the Gemini API
genai.configure(api_key=GOOGLE_API_KEY)

# Define model configurations
GEMINI_PRO_MODEL = "gemini-1.5-pro"
GEMINI_PRO_VISION_MODEL = "gemini-1.5-pro-vision"

# Check if Tesseract is installed and set the path based on OS
TESSERACT_AVAILABLE = pytesseract.pytesseract.tesseract_cmd is not None

generation_config_gemini = {
    "max_output_tokens": 2048,
    "temperature": 1,
    "top_p": 1,
}

safety_settings_gemini = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    }
]

system_instruction = "You are a professional math solving assistant for Student. Your answer must be in English. Given a math problem, solve it step-by-step and provide a clear and concise explanation of the solution in English."

def handle_api_error(e):
    if isinstance(e, exceptions.ResourceExhausted):
        st.error("""
        API rate limit exceeded. 
        Please wait a minute before trying again.
        If this happens frequently, consider:
        1. Upgrading your API quota
        2. Reducing the frequency of requests
        3. Using a different API key
        """)
        time.sleep(60)  # Wait for 60 seconds
        return True
    elif isinstance(e, exceptions.PermissionDenied):
        st.error("""
        API key is invalid or has insufficient permissions.
        Please check your API key in the .env file and ensure it has the necessary permissions.
        """)
        return False
    elif isinstance(e, exceptions.InvalidArgument):
        st.error("""
        Invalid input provided to the API.
        Please check your input and try again.
        """)
        return False
    else:
        st.error(f"""
        An unexpected error occurred: {str(e)}
        Please try again or contact support if the issue persists.
        """)
        return False

@retry.Retry(predicate=retry.if_exception_type(exceptions.ResourceExhausted))
def gemini_pro_vision_response(prompt, image):
    try:
        model = genai.GenerativeModel(GEMINI_PRO_VISION_MODEL)
        response = model.generate_content([prompt, image])
        return response.text
    except Exception as e:
        if handle_api_error(e):
            return gemini_pro_vision_response(prompt, image)
        return "Error processing image. Please try again."

def clear_history():
    # Clear chat history and messages
    if "history" in st.session_state:
        st.session_state.history = []
        st.session_state.messages = []

    # also clear the chat session at streamlit interface
    if "chat_session" in st.session_state:
        del st.session_state.chat_session


# Function to translate roles between Gemini-Pro and Streamlit terminology
def translate_role_for_streamlit(user_role):
    if user_role == "model":
        return "assistant"
    else:
        return user_role


def extract_text_from_image(image):
    if not TESSERACT_AVAILABLE:
        return "Tesseract OCR is not installed. Please install it to use image text extraction."
    try:
        with st.spinner("Extracting text from image..."):
            text = pytesseract.image_to_string(image, lang='vie+eng')
            if not text.strip():
                return "No text was found in the image."
            return text
    except Exception as e:
        return f"Error extracting text from image: {str(e)}"


def send_message_with_retry(chat_session, message, **kwargs):
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            return chat_session.send_message(message, **kwargs)
        except Exception as e:
            retry_count += 1
            if handle_api_error(e):
                if retry_count < max_retries:
                    st.info(f"Retrying... (Attempt {retry_count + 1}/{max_retries})")
                    continue
            return None
    
    st.error("Maximum retry attempts reached. Please try again later.")
    return None


def main():
    with st.sidebar:
        selected = option_menu('Menu AI',
                               [
                                'Math Solver',
                                'Configuration'],
                               menu_icon='robot', 
                               icons=['chat-square-text-fill', 'badge-cc-fill', 'calculator-fill', 'gear-fill'],
                               default_index=0
                               )

    if selected == 'Configuration':
        st.title("⚙️ Configuration & Troubleshooting")
        
        # API Key Status
        st.subheader("API Key Status")
        if GOOGLE_API_KEY:
            st.success("✅ Google API Key is configured")
            st.info("API Key starts with: " + GOOGLE_API_KEY[:8] + "...")
        else:
            st.error("❌ Google API Key is not configured")
            st.info("Create a .env file with: GOOGLE_API_KEY=your_api_key_here")

        # Tesseract Status
        st.subheader("Tesseract OCR Status")
        if TESSERACT_AVAILABLE:
            st.success("✅ Tesseract OCR is installed and working")
            try:
                version = pytesseract.get_tesseract_version()
                st.info(f"Tesseract Version: {version}")
            except:
                pass
        else:
            st.error("❌ Tesseract OCR is not installed")
            if platform.system() == 'Windows':
                st.info("""
                To install Tesseract on Windows:
                1. Download the installer from: https://github.com/UB-Mannheim/tesseract/wiki
                2. Run the installer
                3. Add Tesseract to your system PATH
                4. Restart this application
                """)
            else:
                st.info("""
                To install Tesseract:
                - Linux: sudo apt-get install tesseract-ocr
                - macOS: brew install tesseract
                """)

        # System Information
        st.subheader("System Information")
        st.info(f"""
        - Operating System: {platform.system()} {platform.release()}
        - Python Version: {platform.python_version()}
        - Working Directory: {working_dir}
        """)

        # Common Issues
        st.subheader("Common Issues & Solutions")
        with st.expander("API Rate Limiting"):
            st.info("""
            If you see "API rate limit exceeded" errors:
            1. Wait a minute before trying again
            2. Reduce the frequency of your requests
            3. Consider upgrading your API quota
            """)
        
        with st.expander("Image Processing Issues"):
            st.info("""
            If image processing isn't working:
            1. Ensure Tesseract OCR is installed
            2. Check if the image is clear and readable
            3. Try a different image format (JPG, PNG)
            """)
        
        with st.expander("Chat Issues"):
            st.info("""
            If the chat isn't responding:
            1. Check your internet connection
            2. Verify your API key is valid
            3. Try clearing the chat history
            """)

    elif selected == 'Gemini ChatBot':
        upload_image = None

        # upload image
        upload_image = st.sidebar.file_uploader(
            "Upload Image", type=["jpg", "png", "jpeg"])

        if selected != st.session_state.get('previous_model', None):
            clear_history()
            st.session_state['previous_model'] = selected
        
        model = genai.GenerativeModel(GEMINI_PRO_MODEL)

        # Initialize chat session in Streamlit if not already present
        if "chat_session" not in st.session_state:  # Renamed for clarity
            st.session_state.chat_session = model.start_chat(history=[])

        # Display the chatbot's title on the page
        st.title("🤖 AI Math Solver")

        # Display the chat history
        for message in st.session_state.chat_session.history:
            with st.chat_message(translate_role_for_streamlit(message.role)):
                st.markdown(message.parts[0].text)

        # Input field for user's message
        user_prompt = st.chat_input("Enter your input")
        if user_prompt:
            upload_image = None
            # Add user's message to chat and display it
            st.chat_message("user").markdown(user_prompt)

            # Send user's message to Gemini-Pro and get the response
            try:
                response = st.session_state.chat_session.send_message(
                    user_prompt,
                    generation_config=generation_config_gemini
                )
                if response:
                    with st.chat_message("assistant"):
                        st.markdown(response.text)
            except Exception as e:
                handle_api_error(e)

        if upload_image is not None:
            img = Image.open(upload_image)
            output_text = extract_text_from_image(img)
            st.chat_message("user").markdown(output_text)

            # Send user's message to Gemini-Pro and get the response
            response = send_message_with_retry(st.session_state.chat_session, output_text)
            if response:
                with st.chat_message("assistant"):
                    st.markdown(response.text)
    # Image captioning page
    elif selected == "Image Analysis":

        st.title("📷 Image Analysis")

        uploaded_image = st.file_uploader(
            "Upload Image", type=["jpg", "jpeg", "png"])

        if st.button("Analyze Image"):
            image = Image.open(uploaded_image)

            col1, col2 = st.columns(2)

            with col1:
                resized_img = image.resize((800, 500))
                st.image(resized_img)

            default_prompt = "Describe the image in Vietnamese"
            # get the caption of the image from the gemini-pro-vision LLM
            caption = gemini_pro_vision_response(default_prompt, image)

            with col2:
                st.info(caption)

    elif selected == "Math Solver":

        upload_image = None
        # upload image
        upload_image = st.sidebar.file_uploader(
            'Upload image', type=["jpg", "png", "jpeg"])

        if selected != st.session_state.get('previous_model', None):
            clear_history()
            st.session_state['previous_model'] = selected
        st.title("🧮 Math Solver")

        model = genai.GenerativeModel(GEMINI_PRO_MODEL)
        if "chat_session" not in st.session_state:
            st.session_state.chat_session = model.start_chat(history=[])

        # Display the chat history
        for message in st.session_state.chat_session.history:
            with st.chat_message(translate_role_for_streamlit(message.role)):
                st.markdown(message.parts[0].text)

        user_prompt = st.chat_input("Enter your input")
        if user_prompt:
            upload_image = None
            st.chat_message("user").markdown(user_prompt)
            
            try:
                response = st.session_state.chat_session.send_message(
                    [system_instruction, user_prompt],
                    generation_config=generation_config_gemini
                )
                if response:
                    with st.chat_message("assistant"):
                        st.markdown(response.text)
            except Exception as e:
                handle_api_error(e)
        if upload_image is not None:
            img = Image.open(upload_image)
            output_text = extract_text_from_image(img)
            user_prompt = output_text
            st.chat_message("user").markdown(user_prompt)

            # Send user's message to Gemini-Pro and get the response
            response = send_message_with_retry(st.session_state.chat_session, user_prompt)
            if response:
                with st.chat_message("assistant"):
                    st.markdown(response.text)


if __name__ == "__main__":
    main()
