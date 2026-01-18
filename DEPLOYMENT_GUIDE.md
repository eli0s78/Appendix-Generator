# 🚀 Deployment Guide - Appendix Generator

This guide explains the complete workflow from local development to live deployment on Streamlit Cloud with automatic updates.

## 📋 Table of Contents

1. [One-Time Setup](#one-time-setup)
2. [Development Workflow](#development-workflow)
3. [Deployment Workflow](#deployment-workflow)
4. [Automatic Updates](#automatic-updates)
5. [Troubleshooting](#troubleshooting)

---

## 🔧 One-Time Setup

### Prerequisites

- Python 3.9+ installed locally
- Git installed on your machine
- GitHub account ([sign up here](https://github.com/join))
- Streamlit Cloud account (free, uses GitHub to sign in)

### Step 1: Set Up GitHub Repository

1. **Go to GitHub** and create a new repository:
   - Click the `+` icon → `New repository`
   - Repository name: `appendix-generator` (or your preferred name)
   - Description: "AI-powered foresight appendix generator for academic books"
   - Visibility: **Public** (required for free Streamlit Cloud deployment)
   - **DO NOT** initialize with README, .gitignore, or license (we already have these)
   - Click `Create repository`

2. **Copy the repository URL** - it will look like:
   ```
   https://github.com/YOUR_USERNAME/appendix-generator.git
   ```

### Step 2: Connect Local Repository to GitHub

Run these commands in your project directory:

```bash
# Add all files to Git
git add .

# Create your first commit
git commit -m "Initial commit: Appendix Generator app"

# Add GitHub as remote origin (replace with YOUR repository URL)
git remote add origin https://github.com/YOUR_USERNAME/appendix-generator.git

# Push to GitHub
git push -u origin main
```

**Note:** If you get an error about `master` vs `main` branch, run:
```bash
git branch -M main
git push -u origin main
```

### Step 3: Deploy to Streamlit Cloud

1. **Go to [share.streamlit.io](https://share.streamlit.io)**

2. **Sign in** with your GitHub account

3. **Click "New app"**

4. **Configure your app:**
   - Repository: `YOUR_USERNAME/appendix-generator`
   - Branch: `main`
   - Main file path: `app.py`
   - App URL (optional): Choose a custom subdomain or use the default

5. **Click "Deploy"**

6. **Wait 2-3 minutes** for the initial deployment

7. **Your app is live!** 🎉
   - URL format: `https://YOUR_USERNAME-appendix-generator.streamlit.app`
   - Share this link with anyone!

---

## 💻 Development Workflow

### Working Locally

1. **Activate your virtual environment** (if using one):
   ```bash
   # Windows
   .venv\Scripts\activate

   # macOS/Linux
   source .venv/bin/activate
   ```

2. **Run the app locally**:
   ```bash
   streamlit run app.py
   ```

3. **Make your changes**:
   - Edit code in your preferred editor
   - Test locally at `http://localhost:8501`
   - Make sure everything works before deploying

4. **Test thoroughly**:
   - Upload a PDF
   - Generate appendices
   - Check downloads
   - Verify UI/UX changes

---

## 🌐 Deployment Workflow

### When You're Ready to Deploy

Once you've tested your changes locally and they're working perfectly:

```bash
# 1. Check what files changed
git status

# 2. Add all changes to staging
git add .

# 3. Commit with a descriptive message
git commit -m "Add feature: improved PDF extraction"

# 4. Push to GitHub
git push origin main
```

**That's it!** Streamlit Cloud will automatically:
- Detect the push to your GitHub repository
- Start rebuilding your app
- Deploy the new version (usually takes 2-3 minutes)
- Keep your app live during the update

### Commit Message Best Practices

Use clear, descriptive commit messages:

```bash
# Good examples
git commit -m "Fix: PDF upload error for files over 50MB"
git commit -m "Add: Dark mode toggle in settings"
git commit -m "Update: Improved planning table UI"
git commit -m "Refactor: Optimize LLM client for faster responses"

# Bad examples
git commit -m "changes"
git commit -m "updates"
git commit -m "fix"
```

---

## 🔄 Automatic Updates

### How It Works

Streamlit Cloud watches your GitHub repository. When you push to the `main` branch:

1. **GitHub** receives your push
2. **Streamlit Cloud** detects the change via webhook
3. **Automatic rebuild** starts
4. **New version** goes live in 2-3 minutes

### Monitoring Deployments

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click on your app
3. View the "Logs" tab to see:
   - Build progress
   - Deployment status
   - Runtime errors (if any)

### Viewing App Logs

Real-time logs help debug issues:
- Click "Manage app" → "Logs"
- See Python print statements
- Monitor errors and warnings
- Check resource usage

---

## 🛠️ Troubleshooting

### Issue: Git push is rejected

**Error**: `Updates were rejected because the remote contains work that you do not have locally`

**Solution**:
```bash
git pull origin main --rebase
git push origin main
```

### Issue: Streamlit Cloud deployment fails

**Check these common issues:**

1. **Missing dependencies** in `requirements.txt`
   - Add any new packages you installed
   - Include version numbers for stability

2. **File paths are case-sensitive**
   - Windows is case-insensitive, but Linux (Streamlit Cloud) is not
   - Use `utils/export.py`, not `Utils/Export.py`

3. **Large files**
   - GitHub has a 100MB file size limit
   - Use `.gitignore` for test PDFs and large assets

4. **Environment variables**
   - Secrets should be in Streamlit Cloud secrets, not `.env`
   - Never commit `.env` to GitHub

### Issue: App works locally but not on Streamlit Cloud

**Check deployment logs:**
1. Go to your app on share.streamlit.io
2. Click "Manage app" → "Logs"
3. Look for error messages
4. Common causes:
   - Missing file imports
   - Absolute file paths (use relative paths)
   - Dependencies not in requirements.txt

### Issue: Want to revert to a previous version

```bash
# View commit history
git log --oneline

# Revert to a specific commit
git revert COMMIT_HASH

# Push the revert
git push origin main
```

---

## 🔐 Managing Secrets

### For Local Development

Use [.env](.env) file (already in `.gitignore`):
```env
GOOGLE_API_KEY=your-key-here
```

### For Streamlit Cloud

1. Go to your app on [share.streamlit.io](https://share.streamlit.io)
2. Click "⚙️ Settings" → "Secrets"
3. Add secrets in TOML format:
   ```toml
   GOOGLE_API_KEY = "your-key-here"
   ```
4. Click "Save"
5. App will restart automatically

**Access secrets in code:**
```python
import streamlit as st

# This works both locally (from .env) and on Streamlit Cloud (from secrets)
api_key = st.secrets.get("GOOGLE_API_KEY", "")
```

---

## 📦 Adding New Dependencies

Whenever you install a new Python package:

```bash
# Install the package
pip install package-name

# Update requirements.txt
pip freeze > requirements.txt

# Commit and push
git add requirements.txt
git commit -m "Add package-name dependency"
git push origin main
```

---

## 🎯 Quick Reference

### Daily Development Cycle

```bash
# 1. Start working
streamlit run app.py

# 2. Make changes and test locally

# 3. When ready to deploy
git add .
git commit -m "Description of changes"
git push origin main

# 4. Wait 2-3 minutes - new version is live!
```

### Useful Git Commands

```bash
# Check status
git status

# View commit history
git log --oneline

# Discard local changes
git checkout -- filename.py

# Create a new branch for experimental features
git checkout -b feature-name

# Switch back to main
git checkout main

# See differences before committing
git diff
```

---

## 📞 Getting Help

- **Streamlit Docs**: [docs.streamlit.io](https://docs.streamlit.io)
- **Streamlit Community**: [discuss.streamlit.io](https://discuss.streamlit.io)
- **GitHub Issues**: Create an issue in your repository

---

## ✅ Checklist: Ready for Deployment?

Before pushing to GitHub:

- [ ] Code works perfectly locally
- [ ] All tests pass (if you have tests)
- [ ] No hardcoded secrets or API keys in code
- [ ] Updated `requirements.txt` with new dependencies
- [ ] `.env` file is in `.gitignore`
- [ ] Meaningful commit message written
- [ ] Tested with realistic data/PDFs

---

**Happy Coding! 🚀**
