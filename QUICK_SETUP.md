# 🚀 Quick Google OAuth Setup

## **Option 1: Interactive Setup (Recommended)**

Run the setup helper:
```bash
python setup_oauth.py
```

This will guide you through:
- Entering Google OAuth credentials
- Generating secure secret keys
- Testing your configuration

## **Option 2: Manual Setup**

1. **Get Google OAuth Credentials**:
   - Go to [Google Cloud Console](https://console.cloud.google.com)
   - Create project: "VoiceClean AI"
   - Enable Google+ API
   - Create OAuth 2.0 credentials
   - Add redirect URI: `http://localhost:3000/auth/callback`

2. **Update .env file**:
   ```env
   GOOGLE_CLIENT_ID=your-actual-client-id.apps.googleusercontent.com
   GOOGLE_CLIENT_SECRET=GOCSPX-your-actual-client-secret
   FLASK_SECRET_KEY=your-secure-secret-key
   ```

3. **Restart the app**:
   ```bash
   python app.py
   ```

## **Current Status**

Visit: **http://localhost:3000**

- **Demo Mode**: Currently active (no OAuth setup needed)
- **Google OAuth**: Not configured (shows demo button)
- **Full Features**: Available in both modes

## **After OAuth Setup**

Once configured, users will see:
- "Sign in with Google" button
- Real user accounts and tracking
- Daily usage limits (3 enhancements per day)
- User dashboard with statistics

## **Need Help?**

See detailed guide: `GOOGLE_OAUTH_SETUP.md`