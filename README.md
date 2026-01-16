# 🔮 Forward Thinking - Foresight Appendix Generator

A web application that helps generate future-oriented appendices for academic books using AI (Google Gemini).

## 🌟 Features

- **Upload PDF books** and automatically extract text
- **AI-powered analysis** creates a structured planning table with chapter groupings
- **Review and customize** the planning table before generation
- **Generate comprehensive appendices** following a proven foresight framework
- **Download** as Markdown or Word documents

## 🚀 Quick Start (Run Locally)

### Prerequisites

- Python 3.9 or higher
- A Google AI Studio API key (free)

### Installation

1. **Clone this repository:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/foresight-app.git
   cd foresight-app
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the app:**
   ```bash
   streamlit run app.py
   ```

4. **Open in browser:**
   The app will open automatically at `http://localhost:8501`

## 🔑 Getting Your API Key

1. Go to [Google AI Studio](https://aistudio.google.com/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key and paste it in the app's sidebar

**The free tier is generous and sufficient for personal use.**

## 📖 How to Use

### Step 1: Configure
- Enter your Google AI Studio API key in the sidebar
- Click "Validate Key" to confirm it works

### Step 2: Upload Book
- Upload your PDF book
- Click "Extract Book Content"

### Step 3: Analyze
- Click "Analyze Book & Create Planning Table"
- Wait for the AI to analyze the book structure

### Step 4: Review
- Review the generated planning table
- Request changes if needed (e.g., "Combine chapters 4 and 5")

### Step 5: Generate
- Select a chapter/group from the dropdown
- Click "Generate Appendix"
- Download the result as .md or .docx

## ☁️ Deploy to Streamlit Cloud (Free)

### Step 1: Create GitHub Account
If you don't have one, go to [github.com](https://github.com) and sign up.

### Step 2: Create Repository
1. Click the "+" button in GitHub → "New repository"
2. Name it `foresight-app`
3. Make it Public
4. Click "Create repository"

### Step 3: Upload Files
1. In your new repository, click "uploading an existing file"
2. Drag and drop ALL files from this project:
   - `app.py`
   - `requirements.txt`
   - `prompts/` folder (with all files inside)
   - `utils/` folder (with all files inside)
   - `README.md`
3. Click "Commit changes"

### Step 4: Deploy to Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with your GitHub account
3. Click "New app"
4. Select your repository: `YOUR_USERNAME/foresight-app`
5. Branch: `main`
6. Main file path: `app.py`
7. Click "Deploy"

### Step 5: Access Your App
After a few minutes, your app will be live at:
```
https://YOUR_USERNAME-foresight-app-app-XXXX.streamlit.app
```

Share this URL with anyone who wants to use the app!

## 📁 Project Structure

```
foresight-app/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── prompts/
│   ├── __init__.py
│   ├── prompt1.py        # Book analysis prompt
│   └── prompt2.py        # Appendix generation prompt
└── utils/
    ├── __init__.py
    ├── pdf_handler.py    # PDF text extraction
    ├── llm_client.py     # Gemini API integration
    └── export.py         # Export to .md/.docx
```

## 🔧 Troubleshooting

### "Invalid API key"
- Make sure you copied the entire key
- Check that the key is from Google AI Studio (not Google Cloud)
- Try creating a new key

### "Error extracting text"
- Make sure the PDF has selectable text (not scanned images)
- Try a smaller PDF first

### "Error during analysis"
- The book might be too long; try uploading a shorter sample
- Check your internet connection
- Try again in a few minutes (API rate limits)

## 📝 License

MIT License - Feel free to use and modify!

## 🙏 Acknowledgments

- Built with [Streamlit](https://streamlit.io)
- Powered by [Google Gemini](https://ai.google.dev)
- PDF extraction by [pdfplumber](https://github.com/jsvine/pdfplumber)
