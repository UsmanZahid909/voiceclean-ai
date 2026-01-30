# 🔐 Google OAuth Setup Guide for VoiceClean AI

## 🚀 **Quick Setup (5 Minutes)**

Follow these steps to enable Google Sign-In for your VoiceClean AI SaaS:

---

## **Step 1: Create Google Cloud Project**

1. **Go to Google Cloud Console**: [console.cloud.google.com](https://console.cloud.google.com)
2. **Click "New Project"** (top-left dropdown)
3. **Project Name**: `VoiceClean AI`
4. **Click "Create"**

---

## **Step 2: Enable Google+ API**

1. **Go to "APIs & Services" > "Library"**
2. **Search for**: `Google+ API`
3. **Click on it** and press **"Enable"**

---

## **Step 3: Configure OAuth Consent Screen**

1. **Go to "APIs & Services" > "OAuth consent screen"**
2. **Choose "External"** user type
3. **Fill in required fields**:
   - **App name**: `VoiceClean AI`
   - **User support email**: Your email
   - **Developer contact**: Your email
4. **Add scopes**: `email`, `profile`, `openid`
5. **Add test users**: Your email address
6. **Click "Save and Continue"**

---

## **Step 4: Create OAuth 2.0 Credentials**

1. **Go to "APIs & Services" > "Credentials"**
2. **Click "Create Credentials" > "OAuth 2.0 Client IDs"**
3. **Application type**: `Web application`
4. **Name**: `VoiceClean AI Web Client`
5. **Authorized redirect URIs**:
   ```
   http://localhost:3000/auth/callback
   http://localhost:5000/auth/callback
   http://localhost:8000/auth/callback
   ```
   
   **For production, also add**:
   ```
   https://your-domain.vercel.app/auth/callback
   https://your-custom-domain.com/auth/callback
   ```

6. **Click "Create"**
7. **Copy the Client ID and Client Secret**

---

## **Step 5: Update Your .env File**

Replace the placeholder values in your `.env` file:

```env
# Replace these with your actual Google OAuth credentials
GOOGLE_CLIENT_ID=123456789-abcdefghijklmnop.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-abcdefghijklmnopqrstuvwxyz

# Generate a secure secret key
FLASK_SECRET_KEY=your-super-secure-secret-key-here
```

### **Generate Secure Secret Key**:
```python
import secrets
print(secrets.token_hex(32))
```

---

## **Step 6: Test Google OAuth**

1. **Restart your app**: Stop and run `python app.py`
2. **Visit**: `http://localhost:3000`
3. **Click**: "Sign in with Google to Start"
4. **Complete OAuth flow**
5. **You should be redirected to the dashboard**

---

## **🔧 Troubleshooting**

### **Common Issues:**

#### **1. "redirect_uri_mismatch" Error**
- **Solution**: Make sure your redirect URI in Google Cloud Console exactly matches:
  ```
  http://localhost:3000/auth/callback
  ```

#### **2. "invalid_client" Error**
- **Solution**: Double-check your Client ID and Client Secret in `.env`

#### **3. "access_denied" Error**
- **Solution**: Add your email as a test user in OAuth consent screen

#### **4. App still in demo mode**
- **Solution**: Make sure your `.env` file has the correct Google credentials and restart the app

---

## **🌐 Production Deployment**

### **For Vercel:**
1. **Add environment variables** in Vercel dashboard:
   ```
   GOOGLE_CLIENT_ID=your-client-id
   GOOGLE_CLIENT_SECRET=your-client-secret
   FLASK_SECRET_KEY=your-secret-key
   ```

2. **Update redirect URIs** in Google Cloud Console:
   ```
   https://your-app.vercel.app/auth/callback
   ```

### **For Custom Domain:**
```
https://voiceclean.ai/auth/callback
```

---

## **✅ Verification Checklist**

- [ ] Google Cloud project created
- [ ] Google+ API enabled
- [ ] OAuth consent screen configured
- [ ] OAuth 2.0 credentials created
- [ ] Redirect URIs added (localhost + production)
- [ ] `.env` file updated with real credentials
- [ ] App restarted
- [ ] Google sign-in tested successfully

---

## **🎯 What Happens After Setup**

Once configured, your app will:

1. **Show "Sign in with Google"** button on landing page
2. **Redirect to Google** for authentication
3. **Create user accounts** automatically
4. **Track daily usage limits** (3 enhancements per day)
5. **Store user data** in database
6. **Enable full SaaS functionality**

---

## **🔒 Security Notes**

- **Never commit** `.env` file to version control
- **Use environment variables** in production
- **Regularly rotate** secret keys
- **Enable HTTPS** in production (required for OAuth)

---

## **📞 Need Help?**

If you encounter issues:
1. Check the browser console for errors
2. Verify all URLs match exactly
3. Ensure your email is added as a test user
4. Try incognito mode to clear cookies

**Your Google OAuth setup is now complete!** 🎉