"""
Distributor for formatted article summaries
"""
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
from typing import List, Dict, Any
import config
import re

try:
    import markdown
    MARKDOWN_AVAILABLE = True
except ImportError:
    MARKDOWN_AVAILABLE = False
    print("Warning: markdown module not found. Install with 'pip install markdown' to enable HTML conversion.")

class MarkdownDistributor:
    def __init__(self, output_dir="output"):
        """
        Initialize the distributor for formatted article output
        
        Args:
            output_dir: Directory to save markdown files
        """
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
    
    def format_articles(self, articles: List[Dict[str, Any]], 
                         categorized: Dict[str, List[Dict[str, Any]]], 
                         daily_overview: str = None) -> str:
        """
        Format articles into nice markdown optimized for email
        
        Args:
            articles: List of all summarized articles
            categorized: Dictionary of articles by category
            daily_overview: Daily digest overview from macro summary agent
            
        Returns:
            Formatted markdown string
        """
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Start with the header
        markdown = f"# AI News Digest - {today}\n\n"
        
        # Add daily overview if provided (from Macro Summary Agent)
        if daily_overview:
            markdown += f"## 📊 Daily Overview\n\n"
            markdown += f"{daily_overview}\n\n"
        
        # Add summary stats
        markdown += f"## 📈 Summary\n"
        markdown += f"*{len(articles)} articles from {len(set([a.get('source', 'Unknown') for a in articles]))} sources*\n\n"
        
        # Process special categories first
        # Find Product Hunt tools (in AI_TOOLS category)
        if "AI_TOOLS" in categorized and categorized["AI_TOOLS"]:
            product_hunt_tools = [a for a in categorized["AI_TOOLS"] if "Product Hunt" in a.get('source', '')]
            non_product_hunt = [a for a in categorized["AI_TOOLS"] if "Product Hunt" not in a.get('source', '')]
            
            # Get top 3 Product Hunt tools by score (if available)
            top_tools = []
            if product_hunt_tools:
                # Sort by tool_score if available, otherwise by date
                if 'tool_score' in product_hunt_tools[0]:
                    sorted_tools = sorted(product_hunt_tools, key=lambda x: x.get('tool_score', 0), reverse=True)
                    top_tools = sorted_tools[:3]
                    
                    # Add a special Product Hunt section for top tools
                    emoji = "🔍"  # Special emoji for top tools
                    markdown += f"## {emoji} Top Product Hunt Tools (3 of {len(product_hunt_tools)})\n\n"
                    
                    for i, article in enumerate(top_tools):
                        title = article.get('title', 'No Title')
                        link = article.get('link', '')
                        summary = article.get('ai_summary', article.get('summary', 'No summary available'))
                        source = article.get('source', 'Unknown Source')
                        score = article.get('tool_score', 'N/A')
                        reasoning = article.get('tool_reasoning', '')
                        
                        # Clean up summary text - remove HTML tags
                        summary = self._clean_html(summary)
                        
                        # Bold title with link and ranking
                        markdown += f"**#{i+1}: [{title}]({link})** (Score: {score}/10)\n\n"
                        
                        # Italicize source
                        markdown += f"*Source: {source}*\n\n"
                        
                        # Add summary text
                        markdown += f"{summary}\n\n"
                        
                        # Add reasoning if available
                        if reasoning:
                            markdown += f"*Why we picked it: {reasoning}*\n\n"
                        
                        # Add spacing between articles
                        markdown += "\n"
            
            # Update the AI_TOOLS category to exclude the Product Hunt tools we've already covered
            if top_tools:
                top_tool_titles = [t.get('title') for t in top_tools]
                categorized["AI_TOOLS"] = [a for a in categorized["AI_TOOLS"] 
                                           if a.get('title') not in top_tool_titles]
        
        # Add other categories with emoji from config
        for category, category_articles in categorized.items():
            if not category_articles:
                continue
                
            # Get emoji for category
            emoji = config.CATEGORIES.get(category, {}).get("emoji", "")
            
            # Sort by date if available
            sorted_articles = sorted(
                category_articles, 
                key=lambda x: x.get('published', datetime.now()), 
                reverse=True
            )
            
            # Make category headings larger and more prominent
            markdown += f"## {emoji} {category.replace('_', ' ').title()} ({len(sorted_articles)})\n\n"
            
            # Add each article with improved formatting
            for article in sorted_articles:
                title = article.get('title', 'No Title')
                link = article.get('link', '')
                summary = article.get('ai_summary', article.get('summary', 'No summary available'))
                source = article.get('source', 'Unknown Source')
                
                # Clean up summary text - remove HTML tags
                summary = self._clean_html(summary)
                
                # Bold title with link
                markdown += f"**[{title}]({link})**\n\n"
                
                # Italicize source
                markdown += f"*Source: {source}*\n\n"
                
                # Add summary text
                markdown += f"{summary}\n\n"
                
                # Add spacing between articles
                markdown += "\n"
            
        return markdown
    
    def _clean_html(self, text: str) -> str:
        """
        Clean HTML tags from text for better email display
        
        Args:
            text: Text that may contain HTML tags
            
        Returns:
            Cleaned text
        """
        # Replace common HTML tags with appropriate markdown
        text = text.replace('<p>', '').replace('</p>', '\n\n')
        text = text.replace('<br>', '\n').replace('<br/>', '\n').replace('<br />', '\n')
        text = text.replace('&nbsp;', ' ')
        text = text.replace('&#8230;', '...')
        text = text.replace('&#160;', ' ')
        text = text.replace('&amp;', '&')
        
        # Remove any remaining HTML tags (simple approach)
        text = re.sub(r'<[^>]+>', '', text)
        
        # Normalize multiple newlines
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        return text.strip()
    
    def save_markdown(self, markdown: str, filename=None) -> str:
        """
        Save markdown to file
        
        Args:
            markdown: Formatted markdown string
            filename: Optional custom filename
            
        Returns:
            Path to saved file
        """
        if not filename:
            today = datetime.now().strftime("%Y-%m-%d")
            filename = f"ai_news_{today}.md"
        
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(markdown)
        
        return filepath

    def markdown_to_html(self, markdown_content: str) -> str:
        """
        Convert markdown to HTML
        
        Args:
            markdown_content: Markdown formatted text
            
        Returns:
            HTML formatted text
        """
        if not MARKDOWN_AVAILABLE:
            raise ImportError("markdown module not installed. Install with 'pip install markdown'")
        
        # Convert markdown to HTML with code syntax highlighting
        html = markdown.markdown(
            markdown_content,
            extensions=['fenced_code', 'tables']
        )
        
        # Add basic styling for better email viewing
        styled_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px; }}
                h1 {{ color: #2c3e50; font-size: 24px; margin-top: 20px; margin-bottom: 10px; }}
                h2 {{ color: #3498db; font-size: 20px; margin-top: 20px; margin-bottom: 15px; }}
                h3 {{ color: #2c3e50; font-size: 16px; margin-top: 15px; margin-bottom: 5px; }}
                a {{ color: #3498db; text-decoration: none; }}
                a:hover {{ text-decoration: underline; }}
                p {{ margin-bottom: 10px; }}
                strong {{ font-weight: bold; }}
                em {{ font-style: italic; }}
            </style>
        </head>
        <body>
            {html}
        </body>
        </html>
        """
        
        return styled_html
    
    def send_email_smtp(self, markdown_content: str, html_content: str) -> bool:
        """
        Send individual emails for maximum privacy
        
        Args:
            markdown_content: Plain text markdown content
            html_content: HTML formatted content
            
        Returns:
            True if successful, False otherwise
        """
        email_config = config.DISTRIBUTION.get('email', {})
        if not email_config.get('enabled', False):
            print("Email distribution not enabled in config.")
            return False
        
        sender = email_config.get('sender', '')
        recipients_str = email_config.get('recipient', '')
        subject = email_config.get('subject', 'AI News Digest')
        smtp_server = email_config.get('smtp_server', '')
        smtp_port = email_config.get('smtp_port', 465)
        smtp_user = email_config.get('smtp_user', sender)
        smtp_password = email_config.get('smtp_password', '')
        
        # Parse recipients list
        recipients = [email.strip() for email in recipients_str.split(',') if email.strip()]
        
        # Debug information
        print("\n--- Email Configuration Debug ---")
        print(f"Email enabled: {email_config.get('enabled')}")
        print(f"Sender: {sender}")
        print(f"Recipients: {len(recipients)} individual emails (maximum privacy)")
        print(f"SMTP Server: {smtp_server}")
        print(f"SMTP Port: {smtp_port}")
        print(f"SMTP User: {smtp_user}")
        print(f"SMTP Password: {'*' * (len(smtp_password) if smtp_password else 0)}")
        
        if not (sender and recipients and smtp_server and smtp_password):
            print("Missing email configuration. Check config.py")
            missing = []
            if not sender: missing.append("sender")
            if not recipients: missing.append("recipients")
            if not smtp_server: missing.append("smtp_server")
            if not smtp_password: missing.append("smtp_password")
            print(f"Missing values: {', '.join(missing)}")
            return False
        
        try:
            print(f"\nSending {len(recipients)} individual emails for maximum privacy...")
            
            # Connect once and send individual emails
            with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
                print(f"Connecting to {smtp_server}:{smtp_port} using SSL...")
                print(f"Logging in as {smtp_user}...")
                server.login(smtp_user, smtp_password)
                
                successful_sends = 0
                failed_sends = 0
                
                # Send individual email to each recipient
                for i, recipient in enumerate(recipients, 1):
                    try:
                        # Create individual message for each recipient
                        msg = MIMEMultipart("alternative")
                        msg["Subject"] = subject
                        msg["From"] = sender
                        msg["To"] = recipient
                        
                        # Attach plain text and HTML versions
                        msg.attach(MIMEText(markdown_content, "plain"))
                        msg.attach(MIMEText(html_content, "html"))
                        
                        # Send individual email
                        server.sendmail(sender, [recipient], msg.as_string())
                        print(f"  ✅ {i}/{len(recipients)}: Sent to {recipient}")
                        successful_sends += 1
                        
                    except Exception as e:
                        print(f"  ❌ {i}/{len(recipients)}: Failed to send to {recipient}: {str(e)}")
                        failed_sends += 1
                
            print(f"\n📧 Email Summary:")
            print(f"  • Successful: {successful_sends}")
            print(f"  • Failed: {failed_sends}")
            print(f"  • Total: {len(recipients)}")
            
            return successful_sends > 0
            
        except Exception as e:
            print(f"Error with SMTP connection: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def distribute(self, articles: List[Dict[str, Any]], 
                   categorized: Dict[str, List[Dict[str, Any]]], 
                   daily_overview: str = None) -> str:
        """
        Format articles and distribute as markdown file and optionally email
        
        Args:
            articles: List of all summarized articles
            categorized: Dictionary of articles by category
            daily_overview: Daily digest overview from macro summary agent
            
        Returns:
            Path to saved markdown file
        """
        # Generate markdown
        markdown_content = self.format_articles(articles, categorized, daily_overview)
        
        # Save to file
        filepath = self.save_markdown(markdown_content)
        print(f"Markdown digest saved to {filepath}")
        
        # Email distribution if enabled
        email_config = config.DISTRIBUTION.get('email', {})
        if email_config.get('enabled', False):
            try:
                print("\n--- Starting Email Distribution ---")
                
                # Convert markdown to HTML
                html_content = self.markdown_to_html(markdown_content)
                
                # Send using standard SMTP
                print("Using standard SMTP for email distribution...")
                success = self.send_email_smtp(markdown_content, html_content)
                
                if not success:
                    print("Failed to send email. Check the error messages above.")
                    
            except Exception as e:
                print(f"Error during email distribution: {str(e)}")
                import traceback
                traceback.print_exc()
        else:
            print("\nEmail distribution is disabled in config.")
        
        return filepath

def use_distributor(articles, categorized, daily_overview=None):
    """
    Use the distributor to format and save articles
    """
    distributor = MarkdownDistributor()
    filepath = distributor.distribute(articles, categorized, daily_overview)
    return filepath
