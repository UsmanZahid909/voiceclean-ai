#!/usr/bin/env python3
"""
VoiceClean AI - Automated Deployment Script
This script helps you deploy your SaaS to GitHub and Vercel
"""

import os
import subprocess
import sys
from datetime import datetime

def run_command(command, description):
    """Run a shell command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ Error in {description}: {e.stderr}")
        return None

def check_git_installed():
    """Check if git is installed"""
    result = run_command("git --version", "Checking Git installation")
    return result is not None

def check_vercel_cli():
    """Check if Vercel CLI is installed"""
    result = run_command("vercel --version", "Checking Vercel CLI")
    if result is None:
        print("📦 Vercel CLI not found. Install with: npm i -g vercel")
        return False
    return True

def initialize_git():
    """Initialize git repository"""
    if os.path.exists('.git'):
        print("📁 Git repository already exists")
        return True
    
    return run_command("git init", "Initializing Git repository") is not None

def create_commit():
    """Create initial commit"""
    # Add all files
    if run_command("git add .", "Adding files to Git") is None:
        return False
    
    # Create commit message
    commit_message = f"""🎵 VoiceClean AI - Complete SaaS Audio Enhancement Platform

✨ Features:
- Advanced AI audio enhancement (noise removal + voice clarity)
- Google OAuth authentication with demo fallback
- Daily usage limits (3 enhancements per day)
- Professional UI/UX with mobile responsiveness
- SEO optimized with structured data
- Google AdSense integration ready
- Production-ready with database integration
- Multiple audio format support (MP3, WAV, M4A, FLAC, OGG, AAC)
- Real-time processing with progress tracking
- Secure file handling and validation

🚀 Ready for production deployment!
Deployed on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""

    return run_command(f'git commit -m "{commit_message}"', "Creating initial commit") is not None

def setup_github_remote():
    """Setup GitHub remote"""
    print("\n🔗 GitHub Repository Setup")
    print("-" * 30)
    
    github_username = input("Enter your GitHub username: ").strip()
    if not github_username:
        print("❌ GitHub username is required")
        return False
    
    repo_name = input("Repository name (default: voiceclean-ai): ").strip() or "voiceclean-ai"
    
    # Check if remote already exists
    result = subprocess.run("git remote get-url origin", shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"📁 Remote origin already exists: {result.stdout.strip()}")
        return True
    
    # Add remote
    remote_url = f"https://github.com/{github_username}/{repo_name}.git"
    if run_command(f"git remote add origin {remote_url}", "Adding GitHub remote") is None:
        return False
    
    print(f"\n📋 Next steps:")
    print(f"1. Create repository at: https://github.com/new")
    print(f"2. Repository name: {repo_name}")
    print(f"3. Description: Professional AI-powered audio enhancement SaaS platform")
    print(f"4. Make it Public (for free Vercel deployment)")
    
    input("\nPress Enter after creating the GitHub repository...")
    return True

def push_to_github():
    """Push code to GitHub"""
    # Set main branch
    if run_command("git branch -M main", "Setting main branch") is None:
        return False
    
    # Push to GitHub
    return run_command("git push -u origin main", "Pushing to GitHub") is not None

def deploy_to_vercel():
    """Deploy to Vercel"""
    print("\n🚀 Vercel Deployment")
    print("-" * 20)
    
    if not check_vercel_cli():
        print("\n📦 Install Vercel CLI first:")
        print("npm install -g vercel")
        print("\nThen run this script again or deploy manually:")
        print("1. Go to https://vercel.com")
        print("2. Sign up with GitHub")
        print("3. Import your repository")
        print("4. Deploy!")
        return False
    
    # Login to Vercel
    print("🔐 Please login to Vercel...")
    if run_command("vercel login", "Logging into Vercel") is None:
        return False
    
    # Deploy
    print("🚀 Deploying to Vercel...")
    result = run_command("vercel --prod", "Deploying to production")
    if result:
        print(f"\n🎉 Deployment successful!")
        print(f"📱 Your app is live!")
        return True
    
    return False

def show_success_message():
    """Show success message with next steps"""
    print("\n" + "="*60)
    print("🎉 DEPLOYMENT SUCCESSFUL!")
    print("="*60)
    
    print("\n✅ Your VoiceClean AI SaaS is now LIVE!")
    print("\n🌐 Access your app at:")
    print("   • Vercel URL: https://your-app-name.vercel.app")
    print("   • GitHub: https://github.com/yourusername/voiceclean-ai")
    
    print("\n🔧 Next Steps:")
    print("   1. Set up Google OAuth (optional)")
    print("   2. Configure Google AdSense")
    print("   3. Add Google Analytics")
    print("   4. Set up custom domain")
    
    print("\n📚 Documentation:")
    print("   • Setup Guide: GOOGLE_OAUTH_SETUP.md")
    print("   • Deployment: LIVE_DEPLOYMENT.md")
    print("   • README: README.md")
    
    print("\n💰 Start earning revenue with your SaaS!")
    print("="*60)

def main():
    """Main deployment function"""
    print("🚀 VoiceClean AI - Automated Deployment")
    print("="*50)
    
    # Check prerequisites
    if not check_git_installed():
        print("❌ Git is required for deployment")
        sys.exit(1)
    
    # Initialize git
    if not initialize_git():
        print("❌ Failed to initialize Git repository")
        sys.exit(1)
    
    # Create commit
    if not create_commit():
        print("❌ Failed to create initial commit")
        sys.exit(1)
    
    # Setup GitHub
    if not setup_github_remote():
        print("❌ Failed to setup GitHub remote")
        sys.exit(1)
    
    # Push to GitHub
    if not push_to_github():
        print("❌ Failed to push to GitHub")
        print("\n🔧 Manual steps:")
        print("1. Create repository at https://github.com/new")
        print("2. Run: git push -u origin main")
        sys.exit(1)
    
    print("\n✅ Code successfully pushed to GitHub!")
    
    # Deploy to Vercel
    deploy_choice = input("\n🚀 Deploy to Vercel now? (y/n): ").strip().lower()
    if deploy_choice == 'y':
        if deploy_to_vercel():
            show_success_message()
        else:
            print("\n🔧 Manual Vercel deployment:")
            print("1. Go to https://vercel.com")
            print("2. Sign up with GitHub")
            print("3. Import your repository")
            print("4. Deploy!")
    else:
        print("\n🔧 Manual Vercel deployment:")
        print("1. Go to https://vercel.com")
        print("2. Sign up with GitHub")
        print("3. Import your repository")
        print("4. Deploy!")
        
        show_success_message()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Deployment cancelled. Run again when ready!")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("Please check the error and try again.")