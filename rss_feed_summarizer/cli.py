#!/usr/bin/env python3
"""
Command Line Interface for RSS Feed Summarizer
"""

import argparse
import sys
import os
from pathlib import Path
from typing import Optional

def create_env_file():
    """Create a .env file from the example template"""
    env_example = Path(".env.example")
    env_file = Path(".env")
    
    if not env_example.exists():
        print("❌ .env.example file not found!")
        return False
    
    if env_file.exists():
        print("⚠️  .env file already exists. Please edit it manually.")
        return True
    
    # Copy the example file
    with open(env_example, 'r') as src, open(env_file, 'w') as dst:
        dst.write(src.read())
    
    print("✅ Created .env file from .env.example")
    print("📝 Please edit .env file with your OpenAI API key and email settings.")
    return True

def validate_config():
    """Validate the configuration"""
    from dotenv import load_dotenv
    
    # Load environment variables
    load_dotenv()
    
    # Check required variables
    api_key = os.getenv('OPENAIAPIKEY')
    if not api_key:
        print("❌ OPENAIAPIKEY is required but not set")
        print("💡 Edit your .env file and add your OpenAI API key")
        return False
    
    # Check email configuration if provided
    email_enabled = bool(os.getenv('SMTP_USER') and os.getenv('GMAIL_APP_PASSWORD') and os.getenv('EMAIL_RECIPIENTS'))
    
    if email_enabled:
        print("✅ Email configuration found")
    else:
        print("ℹ️  Email configuration not found - will only save markdown files")
    
    print("✅ Configuration validation passed!")
    return True

def run_summarizer():
    """Run the RSS feed summarizer"""
    try:
        from .pipeline import run_pipeline
        print("🚀 Starting RSS Feed Summarizer...")
        run_pipeline()
        return True
    except Exception as e:
        print(f"❌ Error running summarizer: {str(e)}")
        return False

def show_status():
    """Show the current status and configuration"""
    from dotenv import load_dotenv
    load_dotenv()
    
    print("📊 RSS Feed Summarizer Status")
    print("=" * 30)
    
    # Check if .env exists
    env_exists = Path(".env").exists()
    print(f"Configuration file: {'✅ Found' if env_exists else '❌ Missing'}")
    
    if not env_exists:
        print("💡 Run 'rss-summarizer setup' to create configuration file.")
        return
    
    # Check OpenAI API key
    api_key = os.getenv('OPENAIAPIKEY')
    print(f"OpenAI API Key: {'✅ Configured' if api_key else '❌ Missing'}")
    
    # Check email configuration
    email_configured = bool(os.getenv('SMTP_USER') and os.getenv('GMAIL_APP_PASSWORD') and os.getenv('EMAIL_RECIPIENTS'))
    print(f"Email: {'✅ Configured' if email_configured else '❌ Not configured'}")
    
    # Check output directory
    output_dir = Path("output")
    if output_dir.exists():
        files = list(output_dir.glob("*.md"))
        print(f"Output files: ✅ {len(files)} found")
    else:
        print("Output files: ❌ None found")

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="RSS Feed Summarizer - Intelligent AI-powered news digest",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  rss-summarizer setup          # Create configuration file
  rss-summarizer run            # Run the summarizer
  rss-summarizer status         # Show current status
  rss-summarizer validate       # Validate configuration
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Setup command
    setup_parser = subparsers.add_parser('setup', help='Create configuration file from template')
    
    # Run command
    run_parser = subparsers.add_parser('run', help='Run the RSS feed summarizer')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Show current status and configuration')
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate configuration')
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Execute commands
    if args.command == 'setup':
        success = create_env_file()
        return 0 if success else 1
    
    elif args.command == 'run':
        if not validate_config():
            return 1
        success = run_summarizer()
        return 0 if success else 1
    
    elif args.command == 'status':
        show_status()
        return 0
    
    elif args.command == 'validate':
        success = validate_config()
        return 0 if success else 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
