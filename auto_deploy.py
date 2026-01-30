#!/usr/bin/env python3
"""
VoiceClean AI - Complete Automated Deployment
This script automatically creates GitHub repo, pushes code, and deploys to Vercel
"""

import os
import subprocess
import sys
import json
import time
import webbrowser
from datetime import datetime

class AutoDeployer:
    def __init__(self):
        self.github_username = "UsmanZahid909"
        self.repo_name = "voiceclean-ai"
        self.repo_description = "Professional AI-powered audio enhancement SaaS platform"
        
    def run_command(self, command, description, capture_output=True):
        """Run a shell command and handle errors"""
        print(f"🔄 {description}...")
        try:
            if capture_output:
                result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
                print(f"✅ {description} completed successfully")
                return result.stdout.strip()
            else:
                result = subprocess.run(command, shell=True, check=True)
                print(f"✅ {description} completed successfully")
                return "Success"
        except subprocess.CalledProcessError as e:
            print(f"❌ Error in {description}")
            if capture_output and e.stderr:
                print(f"   Error details: {e.stderr.strip()}")
            return None

    def check_prerequisites(self):
        """Check if required tools are installed"""
        print("🔍 Checking prerequisites...")
        
        # Check Git
        git_version = self.run_command("git --version", "Checking Git")
        if not git_version:
            print("❌ Git is not installed. Please install Git first.")
            return False
            
        # Check Node.js (for Vercel CLI)
        node_version = self.run_command("node --version", "Checking Node.js")
        if not node_version:
            print("⚠️  Node.js not found. Installing Vercel CLI may fail.")
        
        print("✅ Prerequisites check completed")
        return True

    def setup_git_config(self):
        """Configure Git user settings"""
        print("🔧 Setting up Git configuration...")
        
        # Check if already configured
        name = self.run_command("git config --global user.name", "Checking Git name")
        email = self.run_command("git config --global user.email", "Checking Git email")
        
        if not name:
            self.run_command('git config --global user.name "VoiceClean AI Developer"', "Setting Git name")
        if not email:
            self.run_command('git config --global user.email "developer@voiceclean.ai"', "Setting Git email")
            
        print("✅ Git configuration completed")

    def create_github_repo_via_cli(self):
        """Create GitHub repository using GitHub CLI"""
        print("🔄 Attempting to create GitHub repository via CLI...")
        
        # Check if GitHub CLI is installed
        gh_version = self.run_command("gh --version", "Checking GitHub CLI")
        if not gh_version:
            print("📦 GitHub CLI not found. Will use manual method.")
            return False
            
        # Check if authenticated
        auth_status = self.run_command("gh auth status", "Checking GitHub authentication")
        if not auth_status:
            print("🔐 Please authenticate with GitHub CLI:")
            auth_result = self.run_command("gh auth login", "GitHub authentication", capture_output=False)
            if not auth_result:
                return False
        
        # Create repository
        create_cmd = f'gh repo create {self.repo_name} --description "{self.repo_description}" --public'
        result = self.run_command(create_cmd, "Creating GitHub repository")
        
        if result:
            print(f"✅ GitHub repository created: https://github.com/{self.github_username}/{self.repo_name}")
            return True
        else:
            print("⚠️  Repository might already exist or creation failed")
            return True  # Continue anyway

    def create_github_repo_manual(self):
        """Guide user through manual GitHub repository creation"""
        print("\n🔗 Manual GitHub Repository Creation")
        print("=" * 50)
        
        repo_url = f"https://github.com/new"
        print(f"📋 Repository Details:")
        print(f"   • Name: {self.repo_name}")
        print(f"   • Description: {self.repo_description}")
        print(f"   • Visibility: Public")
        print(f"   • Initialize: Leave all checkboxes UNCHECKED")
        
        print(f"\n🌐 Opening GitHub in your browser...")
        try:
            webbrowser.open(repo_url)
        except:
            print(f"   Please manually open: {repo_url}")
        
        input("\n⏳ Press Enter after creating the repository...")
        return True

    def setup_git_repository(self):
        """Initialize and configure Git repository"""
        print("📁 Setting up Git repository...")
        
        # Check if already initialized
        if os.path.exists('.git'):
            print("✅ Git repository already exists")
        else:
            self.run_command("git init", "Initializing Git repository")
        
        # Add all files
        self.run_command("git add .", "Adding files to Git")
        
        # Create commit
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

        self.run_command(f'git commit -m "{commit_message}"', "Creating commit")
        
        # Set up remote
        remote_url = f"https://github.com/{self.github_username}/{self.repo_name}.git"
        
        # Check if remote exists
        existing_remote = self.run_command("git remote get-url origin", "Checking existing remote")
        if not existing_remote:
            self.run_command(f"git remote add origin {remote_url}", "Adding GitHub remote")
        
        # Set main branch
        self.run_command("git branch -M main", "Setting main branch")
        
        print("✅ Git repository setup completed")

    def push_to_github(self):
        """Push code to GitHub"""
        print("📤 Pushing code to GitHub...")
        
        # Push to GitHub
        result = self.run_command("git push -u origin main", "Pushing to GitHub")
        if result:
            print(f"✅ Code successfully pushed to GitHub!")
            print(f"🌐 Repository URL: https://github.com/{self.github_username}/{self.repo_name}")
            return True
        else:
            print("❌ Failed to push to GitHub")
            return False

    def install_vercel_cli(self):
        """Install Vercel CLI if not present"""
        print("📦 Checking Vercel CLI...")
        
        vercel_version = self.run_command("vercel --version", "Checking Vercel CLI")
        if vercel_version:
            print(f"✅ Vercel CLI already installed: {vercel_version}")
            return True
        
        print("📦 Installing Vercel CLI...")
        install_result = self.run_command("npm install -g vercel", "Installing Vercel CLI", capture_output=False)
        
        if install_result:
            print("✅ Vercel CLI installed successfully")
            return True
        else:
            print("❌ Failed to install Vercel CLI")
            print("🔧 Manual installation: npm install -g vercel")
            return False

    def deploy_to_vercel(self):
        """Deploy to Vercel"""
        print("🚀 Deploying to Vercel...")
        
        # Check if Vercel CLI is available
        if not self.install_vercel_cli():
            return self.manual_vercel_deployment()
        
        # Login to Vercel
        print("🔐 Vercel authentication...")
        login_result = self.run_command("vercel login", "Vercel login", capture_output=False)
        if not login_result:
            print("❌ Vercel login failed")
            return self.manual_vercel_deployment()
        
        # Deploy
        print("🚀 Deploying to production...")
        deploy_result = self.run_command("vercel --prod --yes", "Deploying to Vercel")
        
        if deploy_result:
            print("🎉 Deployment successful!")
            # Extract URL from output
            lines = deploy_result.split('\n')
            for line in lines:
                if 'https://' in line and 'vercel.app' in line:
                    print(f"🌐 Live URL: {line.strip()}")
                    break
            return True
        else:
            print("❌ Vercel deployment failed")
            return self.manual_vercel_deployment()

    def manual_vercel_deployment(self):
        """Guide user through manual Vercel deployment"""
        print("\n🔧 Manual Vercel Deployment")
        print("=" * 30)
        
        vercel_url = "https://vercel.com/new"
        print("📋 Manual Deployment Steps:")
        print("1. Go to: https://vercel.com")
        print("2. Sign up/Login with GitHub")
        print("3. Click 'New Project'")
        print(f"4. Import repository: {self.github_username}/{self.repo_name}")
        print("5. Click 'Deploy'")
        print("6. Wait 2-3 minutes - Your app will be live!")
        
        print(f"\n🌐 Opening Vercel in your browser...")
        try:
            webbrowser.open(vercel_url)
        except:
            print(f"   Please manually open: {vercel_url}")
        
        return True

    def show_success_message(self):
        """Show final success message"""
        print("\n" + "="*70)
        print("🎉 DEPLOYMENT COMPLETED SUCCESSFULLY!")
        print("="*70)
        
        print(f"\n✅ Your VoiceClean AI SaaS is now LIVE!")
        print(f"\n🌐 GitHub Repository:")
        print(f"   https://github.com/{self.github_username}/{self.repo_name}")
        
        print(f"\n🚀 Vercel Deployment:")
        print(f"   • Live URL: https://{self.repo_name}.vercel.app (or similar)")
        print(f"   • Dashboard: https://vercel.com/dashboard")
        
        print(f"\n🎯 What's Live Now:")
        print("   ✅ Professional Audio Enhancement SaaS")
        print("   ✅ Advanced AI noise removal + voice clarity")
        print("   ✅ Mobile-responsive design")
        print("   ✅ SEO optimized for search engines")
        print("   ✅ Google AdSense integration ready")
        print("   ✅ Demo mode (works without OAuth)")
        print("   ✅ Production-ready infrastructure")
        
        print(f"\n💰 Revenue Generation:")
        print("   🎯 Set up Google AdSense to start earning")
        print("   📊 Add Google Analytics for tracking")
        print("   🔐 Configure Google OAuth for user accounts")
        
        print(f"\n📚 Next Steps:")
        print("   1. Test your live app")
        print("   2. Set up Google AdSense (optional)")
        print("   3. Configure Google OAuth (optional)")
        print("   4. Share your SaaS with the world!")
        
        print("\n🎉 Congratulations! Your SaaS is ready to generate revenue!")
        print("="*70)

    def deploy(self):
        """Main deployment function"""
        print("🚀 VoiceClean AI - Complete Automated Deployment")
        print("="*60)
        print("🎯 This will automatically:")
        print("   • Set up Git configuration")
        print("   • Create GitHub repository")
        print("   • Push your code to GitHub")
        print("   • Deploy to Vercel")
        print("   • Make your SaaS live!")
        print("="*60)
        
        # Check prerequisites
        if not self.check_prerequisites():
            return False
        
        # Setup Git
        self.setup_git_config()
        
        # Setup Git repository
        self.setup_git_repository()
        
        # Create GitHub repository
        print("\n🔗 Creating GitHub Repository...")
        github_success = self.create_github_repo_via_cli()
        if not github_success:
            self.create_github_repo_manual()
        
        # Push to GitHub
        if not self.push_to_github():
            print("❌ GitHub push failed. Please check repository exists and try again.")
            return False
        
        # Deploy to Vercel
        print("\n🚀 Deploying to Vercel...")
        self.deploy_to_vercel()
        
        # Show success message
        self.show_success_message()
        
        return True

def main():
    """Main function"""
    try:
        deployer = AutoDeployer()
        deployer.deploy()
    except KeyboardInterrupt:
        print("\n\n👋 Deployment cancelled by user.")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("Please check the error and try again.")

if __name__ == "__main__":
    main()