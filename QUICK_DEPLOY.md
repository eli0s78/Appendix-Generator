# ⚡ Quick Deploy - 5 Minutes to Live App

Follow these steps to get your app live on Streamlit Cloud in minutes.

## 🎯 Prerequisites

- GitHub account
- Git installed on your computer
- Your app working locally (test with `streamlit run app.py`)

## 📝 Step-by-Step Deployment

### 1️⃣ Create GitHub Repository (2 minutes)

1. Go to [github.com/new](https://github.com/new)
2. Repository name: `appendix-generator`
3. Make it **Public**
4. Click **Create repository**
5. **Copy the repository URL** (looks like `https://github.com/USERNAME/appendix-generator.git`)

### 2️⃣ Push Your Code to GitHub (1 minute)

Open terminal in your project folder and run:

```bash
# Add all files
git add .

# Create first commit
git commit -m "Initial commit: Appendix Generator"

# Add GitHub remote (replace USERNAME with your GitHub username)
git remote add origin https://github.com/USERNAME/appendix-generator.git

# Push to GitHub
git push -u origin main
```

**If you get an error about branch name:**
```bash
git branch -M main
git push -u origin main
```

### 3️⃣ Deploy to Streamlit Cloud (2 minutes)

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click **Sign in** → Use your GitHub account
3. Click **New app**
4. Fill in:
   - Repository: `USERNAME/appendix-generator`
   - Branch: `main`
   - Main file path: `app.py`
5. Click **Deploy**
6. Wait 2-3 minutes ⏱️

### 4️⃣ Share Your App! 🎉

Your app is now live at:
```
https://USERNAME-appendix-generator.streamlit.app
```

Copy this URL and share it with anyone!

---

## 🔄 Future Updates (30 seconds each)

After making changes locally:

```bash
git add .
git commit -m "Description of what you changed"
git push origin main
```

**Done!** Streamlit Cloud auto-deploys in 2-3 minutes.

---

## 🆘 Troubleshooting

### "Authentication failed" when pushing to GitHub

**Option 1: Use Personal Access Token (Recommended)**
1. Go to [github.com/settings/tokens](https://github.com/settings/tokens)
2. Click "Generate new token (classic)"
3. Select scopes: `repo` (all)
4. Copy the token
5. When Git asks for password, paste the token instead

**Option 2: Use GitHub CLI**
```bash
# Install GitHub CLI first: https://cli.github.com/
gh auth login
```

### "Repository not found"

Make sure the repository URL is correct:
```bash
git remote -v  # Check current remote
git remote set-url origin https://github.com/CORRECT-USERNAME/appendix-generator.git
```

### Deployment fails on Streamlit Cloud

1. Check the logs: App page → "Manage app" → "Logs"
2. Common fixes:
   - Missing package in `requirements.txt`
   - File path case sensitivity (use lowercase)
   - Large files in repo (remove PDFs, use `.gitignore`)

---

## 📚 More Details

For comprehensive workflow documentation, see [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

---

**Need help?** Check [docs.streamlit.io](https://docs.streamlit.io) or the Streamlit Community forum.
