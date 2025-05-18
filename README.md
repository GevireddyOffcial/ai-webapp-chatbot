# Gemini Chatbot

A friendly AI assistant web app powered by Google Gemini, built with [Streamlit](https://streamlit.io/).

## Features

- Chat with Google Gemini models (1.5 Flash, 1.0 Pro, 1.5 Pro)
- Customizable system prompt/persona
- Adjustable temperature and max output tokens
- Safety settings to block harmful content
- Chat history and session management
- Easy configuration via sidebar and `.env` file

## Setup

### 1. Clone the repository

```sh
git clone <your-repo-url>
cd ai-webapp-chatbo
```

### 2. Install dependencies

It's recommended to use a virtual environment:

```sh
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure your API key

Create a `.env` file in the project root with your Google Gemini API key:

```
GOOGLE_API_KEY="your-google-api-key-here"
```

Or, enter your API key in the sidebar when running the app.

### 4. Run the app

```sh
streamlit run app.py
```

The app will open in your browser at [http://localhost:8501](http://localhost:8501).

## Usage

- Enter your Google Gemini API key in the sidebar (or use the `.env` file).
- Select the desired Gemini model.
- Optionally, set a system prompt/persona and adjust advanced settings.
- Start chatting!

## File Structure

- [`app.py`](app.py): Main Streamlit application.
- [`requirements.txt`](requirements.txt): Python dependencies.
- [`.env`](.env): (Optional) Store your API key securely.
- [`.gitignore`](.gitignore): Files and folders to ignore in git.

## Notes

- Get your API key from [Google AI Studio](https://aistudio.google.com/app).
- Your API key is **never** shared or logged by this app.
- For production, ensure your `.env` is not committed to version control.

## License

MIT License