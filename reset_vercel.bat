@echo off
echo ========================================
echo    Resetting Vercel Environment Variables
echo ========================================

echo.
echo 1. Checking Vercel CLI...
vercel --version
if %errorlevel% neq 0 (
    echo Installing Vercel CLI...
    npm install -g vercel
)

echo.
echo 2. Checking Vercel login...
vercel whoami
if %errorlevel% neq 0 (
    echo Please login to Vercel...
    vercel login
)

echo.
echo 3. Linking to project...
vercel link --yes

echo.
echo 4. Removing old environment variables...
vercel env rm SECRET_KEY production --yes
vercel env rm FIREBASE_API_KEY production --yes
vercel env rm FIREBASE_AUTH_DOMAIN production --yes
vercel env rm FIREBASE_PROJECT_ID production --yes
vercel env rm FIREBASE_STORAGE_BUCKET production --yes
vercel env rm FIREBASE_MESSAGING_SENDER_ID production --yes
vercel env rm FIREBASE_APP_ID production --yes
vercel env rm FIREBASE_MEASUREMENT_ID production --yes

echo.
echo 5. Adding environment variables back...
echo voiceclean-ai-secret-key-2024-firebase-complete | vercel env add SECRET_KEY production
echo AIzaSyF29QM3C0pri4z5say9nu4a | vercel env add FIREBASE_API_KEY production
echo voiceclean-ai-say9nu4a.firebaseapp.com | vercel env add FIREBASE_AUTH_DOMAIN production
echo voiceclean-ai-say9nu4a | vercel env add FIREBASE_PROJECT_ID production
echo voiceclean-ai-say9nu4a.appspot.com | vercel env add FIREBASE_STORAGE_BUCKET production
echo 454829723768 | vercel env add FIREBASE_MESSAGING_SENDER_ID production
echo 1:454829723768:web:ec36f24d8df4f882499d8d | vercel env add FIREBASE_APP_ID production
echo G-G35LS3E4P7 | vercel env add FIREBASE_MEASUREMENT_ID production

echo.
echo 6. Triggering redeployment...
vercel --prod

echo.
echo ========================================
echo    Environment Variables Reset Complete!
echo ========================================
echo Wait 2-3 minutes for deployment to complete
pause