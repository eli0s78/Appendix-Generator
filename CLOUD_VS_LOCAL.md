# 🌐 Cloud vs Local Development - Key Differences

Understanding the differences between your local development environment and Streamlit Cloud deployment.

## 🎨 Theme Customization

### On Streamlit Cloud
- Users can change theme via **Settings** → **Theme** in the app menu (☰)
- Available themes: Light, Dark, or Custom
- Your [.streamlit/config.toml](.streamlit/config.toml) has theme settings commented out to allow this flexibility

### On Local Development
You can set a default theme by uncommenting the theme section in [.streamlit/config.toml](.streamlit/config.toml):

```toml
[theme]
primaryColor = "#FF6B6B"
backgroundColor = "#0E1117"
secondaryBackgroundColor = "#262730"
textColor = "#FAFAFA"
font = "sans serif"
```

**Important:** If you uncomment these lines and push to GitHub, users on Streamlit Cloud won't be able to change the theme - it will be locked to your settings.

## 🔑 Environment Variables & Secrets

### Local Development
- Store secrets in [.env](.env) file (never commit this!)
- Load with `python-dotenv`:
  ```python
  from dotenv import load_dotenv
  import os
  load_dotenv()
  api_key = os.getenv("GOOGLE_API_KEY")
  ```

### Streamlit Cloud
- Add secrets in **App Settings** → **Secrets** (TOML format)
- Access with `st.secrets`:
  ```python
  import streamlit as st
  api_key = st.secrets.get("GOOGLE_API_KEY", "")
  ```

### Best Practice (Works in Both)
Your app currently uses direct user input for API keys, which works everywhere:
- Users paste their API key in the sidebar
- No need to manage secrets in config
- Each user brings their own key

## 📦 File Upload Limits

### Local Development
- Controlled by `maxUploadSize` in [.streamlit/config.toml](.streamlit/config.toml)
- Currently set to 200 MB
- Can be increased for local testing

### Streamlit Cloud
- Maximum 200 MB per file (hard limit)
- Cannot be increased
- Keep large test PDFs out of Git repo (they're in [.gitignore](.gitignore))

## 🚀 Performance Differences

### Local Development
- **Faster**: Runs on your machine's resources
- **No cold starts**: App is always running while you test
- **Full CPU/RAM access**: No sharing with other apps

### Streamlit Cloud
- **Shared resources**: Free tier has resource limits
- **Cold starts**: If inactive for 7 days, app sleeps and takes ~30 seconds to wake
- **Resource limits**:
  - 1 GB RAM
  - 1 CPU core
  - Apps may be slower with large PDFs or complex operations

## 📁 File System Access

### Local Development
- Full access to your file system
- Can save/read files anywhere on your computer
- Temporary files persist between runs

### Streamlit Cloud
- **Ephemeral file system**: Files disappear when app restarts
- **Read-only** for most directories
- Use `tempfile` for temporary storage:
  ```python
  import tempfile
  with tempfile.NamedTemporaryFile(delete=False) as tmp:
      tmp.write(data)
      tmp_path = tmp.name
  ```

## 🔄 App Reloading

### Local Development
- Auto-reloads when you save code changes
- Click "Always rerun" for seamless development
- Near-instant reload

### Streamlit Cloud
- Auto-deploys when you push to GitHub
- Takes 2-3 minutes to rebuild
- No hot reload - full app restart

## 🐛 Debugging

### Local Development
- See full Python tracebacks in terminal
- Use `print()` statements
- Set breakpoints with debugger
- Check local logs easily

### Streamlit Cloud
- View logs in **Manage app** → **Logs**
- Limited traceback visibility
- Use `st.write()` or `st.error()` for debugging
- Logs are available for ~7 days

## 🌍 Networking & APIs

### Local Development
- Direct network access
- No rate limiting (except by API provider)
- Can access localhost services

### Streamlit Cloud
- Outbound connections only (can't receive connections)
- Must use HTTPS for external APIs
- Some ports may be blocked
- Rate limits may apply

## 📊 Monitoring Differences

### Local Development
- Monitor in terminal output
- Check system resources with Task Manager/Activity Monitor
- No built-in analytics

### Streamlit Cloud
- View analytics in Streamlit Cloud dashboard:
  - Number of viewers
  - App uptime
  - Resource usage
  - Error rates

## 🔒 Security Considerations

### Local Development
- Runs on localhost only (not publicly accessible)
- No HTTPS required
- Full control over security

### Streamlit Cloud
- **Publicly accessible** by default
- HTTPS automatically enabled
- Consider adding authentication if needed:
  ```python
  # Simple password protection
  import streamlit as st

  password = st.text_input("Enter password:", type="password")
  if password != "your_secure_password":
       st.stop()
  ```

## 📝 Configuration File Differences

### config.toml Settings That Differ

| Setting | Local | Cloud | Notes |
|---------|-------|-------|-------|
| `theme.*` | Customizable | User-controlled | Commented out by default |
| `server.headless` | `false` | `true` | Cloud always runs headless |
| `server.port` | `8501` | Managed by Streamlit | Can't customize on cloud |
| `browser.gatherUsageStats` | `true`/`false` | `false` | Privacy on cloud |
| `maxUploadSize` | 200 MB | 200 MB max | Can't exceed on cloud |

## 🎯 Best Practices

### For Consistent Behavior

1. **Test Locally First**
   - Always test changes locally before pushing
   - Verify file uploads, API calls, and exports work

2. **Use Relative Paths**
   ```python
   # Good (works everywhere)
   with open("prompts/prompt1.py", "r") as f:
       content = f.read()

   # Bad (breaks on cloud)
   with open("C:/Users/name/prompts/prompt1.py", "r") as f:
       content = f.read()
   ```

3. **Handle Missing Dependencies Gracefully**
   ```python
   try:
       import optional_library
   except ImportError:
       st.warning("Optional feature not available")
   ```

4. **Set Reasonable Defaults**
   - Assume limited resources on cloud
   - Add progress indicators for long operations
   - Use `st.cache_data` to avoid recomputation

5. **Plan for Cold Starts**
   - First load after inactivity takes longer
   - Add a loading message
   - Consider a "warmup" endpoint

## 🔧 Troubleshooting Common Differences

### "Works locally but not on cloud"

**Check:**
1. All dependencies in [requirements.txt](requirements.txt)
2. File paths are relative (not absolute)
3. Case sensitivity (cloud is Linux, local might be Windows)
4. File size limits
5. API rate limits

### "Theme looks different"

- Cloud uses user's theme preference
- To force a theme, uncomment settings in [.streamlit/config.toml](.streamlit/config.toml)
- Note: This removes user customization ability

### "App is slower on cloud"

- Expected due to shared resources
- Optimize with:
  - `@st.cache_data` decorator
  - Reduce file sizes
  - Minimize API calls
  - Process data in chunks

### "Files aren't persisting"

- Cloud file system is ephemeral
- Don't rely on saving files between sessions
- Use databases or cloud storage for persistence

## 📚 Additional Resources

- [Streamlit Cloud Docs](https://docs.streamlit.io/streamlit-community-cloud)
- [Resource Limits](https://docs.streamlit.io/streamlit-community-cloud/get-started/limitations-and-known-issues)
- [App Settings](https://docs.streamlit.io/streamlit-community-cloud/manage-your-app)

---

**Summary:** Your app is designed to work well in both environments. The main differences are resources and theme customization. Always test locally, then push to cloud when ready!
