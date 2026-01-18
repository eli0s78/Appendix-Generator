# Developer Mode Guide

## Overview
Developer Mode allows you to work on the Appendix Generator without manually entering your Google AI Studio API key every time. The API key is stored locally in a `.env` file and automatically loaded when the app starts.

## Setup Instructions

### 1. Add Your API Key

Open the `.env` file and add your Google AI Studio API key:

```bash
# Developer Mode Configuration
DEVELOPER_MODE=true

# Your Google AI Studio API Key
GOOGLE_API_KEY=your-actual-api-key-here
```

Replace `your-actual-api-key-here` with your actual API key from [Google AI Studio](https://aistudio.google.com/apikey).

### 2. Run the App

Start the app normally:

```bash
streamlit run app.py
```

The app will automatically:
- Load your API key from `.env`
- Validate the key
- Configure the Gemini client
- Show a "🔧 Developer Mode Active" indicator in the sidebar

## Features

### Auto-Loading
- API key is automatically loaded when the app starts
- No need to manually enter or validate the key
- Session persists across page refreshes

### Visual Indicators
- **Green badge**: "🔧 Developer Mode Active" shows when dev mode is enabled
- **Info box**: Displays the loaded API key status and active model
- **Disabled input**: API key field is disabled (read-only) when dev mode is active

### Security
- `.env` file is excluded from git via `.gitignore`
- API key never appears in version control
- `.env.example` is provided as a template (without actual keys)

## Disabling Developer Mode

To disable developer mode, either:

1. **Option A**: Set `DEVELOPER_MODE=false` in `.env`
2. **Option B**: Delete or rename the `.env` file

The app will revert to normal mode where you manually enter the API key.

## Restoring Production Mode

When you're done developing and want to restore the production setup:

1. Set `DEVELOPER_MODE=false` in `.env` (or delete the file)
2. The app will return to normal mode
3. Users will be prompted to enter their API key in the sidebar

## File Structure

```
Appendix-Generator/
├── .env                 # Your local config (ignored by git)
├── .env.example         # Template file (committed to git)
├── .gitignore           # Ensures .env is never committed
└── app.py               # Modified to support developer mode
```

## Troubleshooting

### Developer mode not working?
- Check that `DEVELOPER_MODE=true` in `.env`
- Verify your API key is correctly set (no spaces, quotes, or extra characters)
- Restart the Streamlit app

### API key validation fails?
- Ensure you have a valid Google AI Studio API key
- Check your internet connection
- Try creating a new API key

### Changes not reflecting?
- Streamlit auto-reloads when files change
- If stuck, manually restart with `Ctrl+C` and `streamlit run app.py`
