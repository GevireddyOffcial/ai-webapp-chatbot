import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv

# --- Configuration ---
# Load environment variables (if running locally and .env file exists)
try:
    load_dotenv()
except Exception as e:
    print(f"Error loading .env file (this is fine if deployed and env vars are set): {e}")

# Set Streamlit page configuration
st.set_page_config(
    page_title="Gemini Chatbot",
    page_icon="✨",  # You can use an emoji or a path to an image
    layout="centered", # "wide" or "centered"
    initial_sidebar_state="expanded", # "auto", "expanded", "collapsed"
)

# --- Helper Function to Initialize Chat Session ---
def initialize_chat_session(api_key, model_name, system_instruction=None, safety_settings=None, generation_config=None):
    """Initializes the Gemini model and starts a chat session."""
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(
            model_name=model_name,
            safety_settings=safety_settings,
            generation_config=generation_config,
            system_instruction=system_instruction if system_instruction else None
        )
        chat = model.start_chat(history=[])
        return chat
    except Exception as e:
        st.error(f"Error initializing Gemini model: {e}")
        return None

# --- Streamlit UI ---
st.title("💬 Gemini Chatbot")
st.caption("A friendly AI assistant powered by Google Gemini")

# --- Sidebar for Configuration ---
with st.sidebar:
    st.header("Configuration")

    # API Key Input
    # Try to get API key from environment first, then from user input
    env_api_key = os.getenv("GOOGLE_API_KEY")
    api_key_input = st.text_input(
        "Google Gemini API Key",
        type="password",
        value=env_api_key if env_api_key else "",
        help="Get your API key from [Google AI Studio](https://aistudio.google.com/app)."
    )

    # Model Selection
    available_models = {
        "Gemini 1.5 Flash (Latest)": "gemini-1.5-flash-latest",
        "Gemini 1.0 Pro": "gemini-1.0-pro",
        "Gemini 1.5 Pro (Latest)": "gemini-1.5-pro-latest",
    }
    selected_model_display_name = st.selectbox(
        "Select Model",
        options=list(available_models.keys()),
        index=0 # Default to Flash
    )
    MODEL_NAME = available_models[selected_model_display_name]

    # System Prompt (Persona)
    system_prompt = st.text_area(
        "System Prompt (Optional)",
        placeholder="e.g., You are a helpful and witty AI assistant named Sparky.",
        height=100,
        help="Define the bot's persona or give it specific instructions."
    )

    # Advanced Settings (collapsible)
    with st.expander("Advanced Settings"):
        temperature = st.slider("Temperature", 0.0, 1.0, 0.7, 0.05, help="Controls randomness. Lower is more deterministic.")
        max_tokens = st.number_input("Max Output Tokens", min_value=50, max_value=8192, value=2048, step=100, help="Maximum length of the response.")
        # You can add Top-P, Top-K here if needed

    # Clear Chat Button
    if st.button("Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.session_state.chat_session = None # Will be re-initialized
        st.rerun()


# --- Session State Initialization ---
# This ensures variables persist across Streamlit reruns (user interactions)
if "api_key" not in st.session_state:
    st.session_state.api_key = api_key_input # Initialize from input or env

if "model_name" not in st.session_state:
    st.session_state.model_name = MODEL_NAME

if "system_prompt" not in st.session_state:
    st.session_state.system_prompt = system_prompt

# Initialize chat messages list in session state if it doesn't exist
if "messages" not in st.session_state:
    st.session_state.messages = [] # Stores dicts like {"role": "user", "content": "Hi"}

# Initialize chat_session in session state
# Re-initialize if API key, model, or system prompt changes
if "chat_session" not in st.session_state or \
   st.session_state.api_key != api_key_input or \
   st.session_state.model_name != MODEL_NAME or \
   st.session_state.system_prompt != system_prompt:

    st.session_state.api_key = api_key_input
    st.session_state.model_name = MODEL_NAME
    st.session_state.system_prompt = system_prompt

    if st.session_state.api_key:
        # Define safety settings (can be made configurable in UI too)
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        ]
        generation_config = {
            "temperature": temperature,
            "max_output_tokens": max_tokens,
        }
        st.session_state.chat_session = initialize_chat_session(
            api_key=st.session_state.api_key,
            model_name=st.session_state.model_name,
            system_instruction=st.session_state.system_prompt if st.session_state.system_prompt.strip() else None,
            safety_settings=safety_settings,
            generation_config=generation_config
        )
        if st.session_state.chat_session:
            # Clear previous messages if settings changed, as context is new
            st.session_state.messages = []
            st.toast(f"Chat session initialized with {selected_model_display_name}!", icon="✅")
        else:
            st.error("Failed to initialize chat. Please check API key and model.")
    else:
        st.session_state.chat_session = None
        if not env_api_key: # Only show warning if not pre-filled by .env
            st.warning("Please enter your Gemini API Key in the sidebar to start chatting.")


# --- Display Chat History ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Handle User Input and Chat Logic ---
if user_prompt := st.chat_input("Ask Gemini..."):
    if not st.session_state.api_key:
        st.error("⚠️ Please enter your Gemini API Key in the sidebar first!")
    elif not st.session_state.chat_session:
        st.error("⚠️ Chat session not initialized. Please check your API key and configuration in the sidebar.")
    else:
        # Add user message to chat history and display it
        st.session_state.messages.append({"role": "user", "content": user_prompt})
        with st.chat_message("user"):
            st.markdown(user_prompt)

        # Get response from Gemini
        try:
            with st.chat_message("assistant"):
                message_placeholder = st.empty() # For streaming
                full_response_content = ""

                # Send message to the model (with streaming)
                response_stream = st.session_state.chat_session.send_message(user_prompt, stream=True)

                for chunk in response_stream:
                    # Check for safety issues in the chunk or overall response (simplified here)
                    # For more robust error handling, inspect chunk.prompt_feedback or response_stream.prompt_feedback
                    # and candidate.finish_reason after the loop.
                    if hasattr(chunk, 'text'):
                        full_response_content += chunk.text
                        message_placeholder.markdown(full_response_content + "▌") # Blinking cursor effect
                    else:
                        # This can happen if there's an issue like a block before text generation
                        st.warning(f"Received an unexpected chunk: {chunk}")
                        break # Or handle more gracefully

                message_placeholder.markdown(full_response_content) # Final response

            # Add assistant's response to chat history
            st.session_state.messages.append({"role": "assistant", "content": full_response_content})

        except genai.types.BlockedPromptException as e:
            st.error(f"⚠️ Your input was blocked by the safety filters: {e}")
            st.session_state.messages.append({"role": "assistant", "content": f"I'm sorry, I can't respond to that due to safety guidelines. (Blocked Prompt: {e})"})
        except genai.types.StopCandidateException as e:
             st.error(f"⚠️ My response was stopped before completion: {e}")
             st.session_state.messages.append({"role": "assistant", "content": f"My apologies, my response was cut short. (Stop Candidate: {e})"})
        except Exception as e:
            st.error(f"An error occurred: {e}")
            st.session_state.messages.append({"role": "assistant", "content": f"Sorry, an unexpected error occurred: {e}"})
            # Optionally, re-initialize chat if it's a critical error
            # st.session_state.chat_session = None
            # st.rerun()