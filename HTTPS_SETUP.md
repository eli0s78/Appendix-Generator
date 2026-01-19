# HTTPS Setup for Local Development

This app is configured to run with HTTPS to ensure downloads work properly in Chrome.

## What Was Done

1. **Self-signed certificate generated** for localhost
2. **Streamlit configured** to use HTTPS
3. **Certificates stored** in `.streamlit/certs/` (git-ignored for security)

## First-Time Setup

The certificates have already been generated. When you run the app, it will automatically use HTTPS.

### If You Need to Regenerate Certificates

```bash
python generate_cert.py
```

This will create:
- `.streamlit/certs/cert.pem` - SSL certificate
- `.streamlit/certs/key.pem` - Private key

## Accessing the App

After running `streamlit run app.py`, the app will be available at:

- **HTTPS URL**: `https://localhost:8502` (use this one)
- **HTTP URL**: `http://localhost:8502` (will not work - redirects to HTTPS)

## Browser Security Warning

**This is normal!** When you first access `https://localhost:8502`, your browser will show a security warning because the certificate is self-signed.

### How to Proceed (Chrome):

1. You'll see: "Your connection is not private"
2. Click **"Advanced"**
3. Click **"Proceed to localhost (unsafe)"**

### How to Proceed (Firefox):

1. You'll see: "Warning: Potential Security Risk Ahead"
2. Click **"Advanced"**
3. Click **"Accept the Risk and Continue"**

### How to Proceed (Edge):

1. You'll see: "Your connection isn't private"
2. Click **"Advanced"**
3. Click **"Continue to localhost (unsafe)"**

## Why HTTPS?

Chrome blocks downloads from non-HTTPS localhost applications for security reasons. By using HTTPS:

✅ Downloads work in Chrome
✅ Downloads work in Firefox
✅ Downloads work in Edge
✅ App is ready for production deployment (Streamlit Cloud uses HTTPS automatically)

## Production Deployment

When deployed to Streamlit Cloud:
- HTTPS is enabled automatically with a real certificate
- No browser warnings
- No additional setup needed

The `.streamlit/certs/` directory is git-ignored and only used for local development.

## Troubleshooting

### "SSL certificate problem" error

Run `python generate_cert.py` to regenerate the certificates.

### Downloads still not working

1. Make sure you're accessing via `https://localhost:8502` (not `http://`)
2. Accept the browser security warning
3. Try the "Test Download" button in the sidebar

### Port already in use

If port 8502 is busy, Streamlit will automatically use the next available port (8503, 8504, etc.). Update the URL accordingly.

## Security Notes

- These certificates are **only for local development**
- They are **self-signed** (not trusted by browsers by default)
- They are **git-ignored** to prevent accidental commits
- Each developer should generate their own certificates
- Production uses proper certificates from Streamlit Cloud

---

**Need help?** Check the main [README.md](README.md) for general app documentation.
