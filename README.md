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

### Quick Deploy (5 minutes)

See [QUICK_DEPLOY.md](QUICK_DEPLOY.md) for a fast deployment guide.

### Complete Workflow Setup

For a comprehensive guide on setting up GitHub, automatic deployments, and development workflow:

📖 **[Read the Full Deployment Guide](DEPLOYMENT_GUIDE.md)**

This includes:
- One-time GitHub and Streamlit Cloud setup
- Automatic deployment on every push
- Development best practices
- Troubleshooting common issues
- Managing secrets and environment variables

### Quick Steps

1. **Create GitHub repository** and push your code
2. **Connect to Streamlit Cloud** at [share.streamlit.io](https://share.streamlit.io)
3. **Deploy** by selecting your repo, branch (`main`), and file (`app.py`)
4. **Your app is live!** Future updates deploy automatically when you push to GitHub

For detailed instructions, see [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

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
