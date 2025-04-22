import os
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
        
        with st.expander("Chat Issues"):
            st.info("""
            If the chat isn't responding:
            1. Check your internet connection
            2. Verify your API key is valid
            3. Try clearing the chat history
            """)

    elif selected == "Math Solver":
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

        user_prompt = st.chat_input("Enter your math problem")
        if user_prompt:
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

if __name__ == "__main__":
    main()
