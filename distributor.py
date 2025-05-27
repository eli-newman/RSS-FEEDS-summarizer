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

try:
    import markdown
    MARKDOWN_AVAILABLE = True
except ImportError:
    MARKDOWN_AVAILABLE = False
    print("Warning: markdown module not found. Install with 'pip install markdown' to enable HTML conversion.")

try:
    import yagmail
    YAGMAIL_AVAILABLE = True
except ImportError:
    YAGMAIL_AVAILABLE = False
    print("Warning: yagmail module not found. Install with 'pip install yagmail' for Gmail support.")

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("Warning: requests module not found. Install with 'pip install requests' for Notion support.")

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
                         categorized: Dict[str, List[Dict[str, Any]]]) -> str:
        """
        Format articles into nice markdown
        
        Args:
            articles: List of all summarized articles
            categorized: Dictionary of articles by category
            
        Returns:
            Formatted markdown string
        """
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Start with the header
        markdown = f"# AI News Digest - {today}\n\n"
        markdown += f"## Summary\n"
        markdown += f"*{len(articles)} articles from {len(set([a.get('source', 'Unknown') for a in articles]))} sources*\n\n"
        
        # Add categories with emoji from config
        for category, category_articles in categorized.items():
            if not category_articles:
                continue
                
            # Get emoji for category
            emoji = config.CATEGORIES.get(category, "")
            
            markdown += f"## {emoji} {category.replace('_', ' ').title()} ({len(category_articles)})\n\n"
            
            # Sort by date if available
            sorted_articles = sorted(
                category_articles, 
                key=lambda x: x.get('published', datetime.now()), 
                reverse=True
            )
            
            # Add each article
            for article in sorted_articles:
                title = article.get('title', 'No Title')
                link = article.get('link', '')
                summary = article.get('ai_summary', article.get('summary', 'No summary available'))
                source = article.get('source', 'Unknown Source')
                
                markdown += f"### [{title}]({link})\n"
                markdown += f"*Source: {source}*\n\n"
                markdown += f"{summary}\n\n"
                markdown += "---\n\n"
        
        return markdown
    
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
                h1 {{ color: #2c3e50; }}
                h2 {{ color: #3498db; border-bottom: 1px solid #eee; padding-bottom: 5px; }}
                h3 {{ color: #2c3e50; }}
                a {{ color: #3498db; text-decoration: none; }}
                a:hover {{ text-decoration: underline; }}
                code {{ background: #f8f8f8; padding: 2px 5px; border-radius: 3px; font-family: monospace; }}
                pre {{ background: #f8f8f8; padding: 10px; border-radius: 5px; overflow-x: auto; }}
                hr {{ border: 0; border-top: 1px solid #eee; margin: 20px 0; }}
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
        Send email using standard SMTP library
        
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
        recipient = email_config.get('recipient', '')
        subject = email_config.get('subject', 'AI News Digest')
        smtp_server = email_config.get('smtp_server', '')
        smtp_port = email_config.get('smtp_port', 465)
        smtp_user = email_config.get('smtp_user', sender)
        smtp_password = email_config.get('smtp_password', '')
        
        if not (sender and recipient and smtp_server and smtp_password):
            print("Missing email configuration. Check config.py")
            return False
        
        try:
            # Create message
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = sender
            msg["To"] = recipient
            
            # Attach plain text and HTML versions
            msg.attach(MIMEText(markdown_content, "plain"))
            msg.attach(MIMEText(html_content, "html"))
            
            # Send email
            with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
                server.login(smtp_user, smtp_password)
                server.sendmail(sender, recipient, msg.as_string())
                
            print(f"Email sent to {recipient}")
            return True
            
        except Exception as e:
            print(f"Error sending email: {str(e)}")
            return False
    
    def send_email_yagmail(self, markdown_content: str, html_content: str) -> bool:
        """
        Send email using yagmail (Gmail)
        
        Args:
            markdown_content: Plain text markdown content
            html_content: HTML formatted content
            
        Returns:
            True if successful, False otherwise
        """
        if not YAGMAIL_AVAILABLE:
            print("yagmail not installed. Install with 'pip install yagmail'")
            return False
            
        email_config = config.DISTRIBUTION.get('email', {})
        if not email_config.get('enabled', False):
            print("Email distribution not enabled in config.")
            return False
        
        sender = email_config.get('sender', '')
        recipient = email_config.get('recipient', '')
        subject = email_config.get('subject', 'AI News Digest')
        smtp_password = email_config.get('smtp_password', '')
        
        if not (sender and recipient and smtp_password):
            print("Missing email configuration. Check config.py")
            return False
        
        try:
            # Initialize yagmail
            yag = yagmail.SMTP(sender, smtp_password)
            
            # Send email
            yag.send(
                to=recipient,
                subject=subject,
                contents=[markdown_content, html_content]
            )
            
            print(f"Email sent to {recipient} using yagmail")
            return True
            
        except Exception as e:
            print(f"Error sending email with yagmail: {str(e)}")
            return False
    
    def distribute(self, articles: List[Dict[str, Any]], 
                   categorized: Dict[str, List[Dict[str, Any]]]) -> str:
        """
        Format articles and distribute as markdown file and optionally email
        
        Args:
            articles: List of all summarized articles
            categorized: Dictionary of articles by category
            
        Returns:
            Path to saved markdown file
        """
        # Generate markdown
        markdown_content = self.format_articles(articles, categorized)
        
        # Save to file
        filepath = self.save_markdown(markdown_content)
        print(f"Markdown digest saved to {filepath}")
        
        # Email distribution if enabled
        email_config = config.DISTRIBUTION.get('email', {})
        if email_config.get('enabled', False):
            try:
                # Convert markdown to HTML
                html_content = self.markdown_to_html(markdown_content)
                
                # Determine which email method to use
                use_yagmail = email_config.get('use_yagmail', False)
                
                if use_yagmail and YAGMAIL_AVAILABLE:
                    self.send_email_yagmail(markdown_content, html_content)
                else:
                    self.send_email_smtp(markdown_content, html_content)
                    
            except Exception as e:
                print(f"Error during email distribution: {str(e)}")
        
        return filepath

class NotionDistributor:
    def __init__(self):
        """
        Initialize the Notion distributor for sending digests to Notion
        """
        self.notion_config = config.DISTRIBUTION.get('notion', {})
        self.enabled = self.notion_config.get('enabled', False)
        self.token = self.notion_config.get('token', '')
        self.database_id = self.notion_config.get('database_id', '')
        
        if not REQUESTS_AVAILABLE:
            print("Notion distribution requires the requests module. Install with 'pip install requests'")
            self.enabled = False
    
    def create_notion_page(self, title: str, markdown_content: str) -> str:
        """
        Create a page in Notion with the digest content
        
        Args:
            title: Title for the Notion page
            markdown_content: Markdown content to add to the page
            
        Returns:
            URL of the created page or empty string if failed
        """
        if not self.enabled or not (self.token and self.database_id):
            print("Notion distribution not enabled or missing configuration.")
            return ""
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }
        
        # Create a new page in the database
        url = "https://api.notion.com/v1/pages"
        
        # Simplified page creation with title and markdown content
        data = {
            "parent": {"database_id": self.database_id},
            "properties": {
                "title": {
                    "title": [{"text": {"content": title}}]
                }
            },
            "children": [
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": "See below for the digest content."}}]
                    }
                },
                {
                    "object": "block",
                    "type": "code",
                    "code": {
                        "language": "markdown",
                        "rich_text": [{"type": "text", "text": {"content": markdown_content}}]
                    }
                }
            ]
        }
        
        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            
            result = response.json()
            page_id = result.get("id", "").replace("-", "")
            
            # Return the URL to the created page
            page_url = f"https://notion.so/{page_id}"
            print(f"Digest added to Notion: {page_url}")
            return page_url
            
        except Exception as e:
            print(f"Error creating Notion page: {str(e)}")
            return ""
    
    def distribute(self, articles: List[Dict[str, Any]], 
                   categorized: Dict[str, List[Dict[str, Any]]]) -> str:
        """
        Format articles and distribute to Notion
        
        Args:
            articles: List of all summarized articles
            categorized: Dictionary of articles by category
            
        Returns:
            URL of the Notion page or empty string if failed
        """
        if not self.enabled:
            return ""
            
        # Create a distributor to format the content
        md_distributor = MarkdownDistributor()
        
        # Generate markdown
        markdown_content = md_distributor.format_articles(articles, categorized)
        
        # Create the Notion page title
        today = datetime.now().strftime("%Y-%m-%d")
        title = f"AI News Digest - {today}"
        
        # Send to Notion
        return self.create_notion_page(title, markdown_content)

# Add this function to app.py to use the distributor
def use_distributor(articles, categorized):
    """
    Use the distributor to format and save articles
    """
    distributor = MarkdownDistributor()
    filepath = distributor.distribute(articles, categorized)
    
    # Add Notion distribution if enabled
    notion_config = config.DISTRIBUTION.get('notion', {})
    if notion_config.get('enabled', False):
        notion_distributor = NotionDistributor()
        notion_url = notion_distributor.distribute(articles, categorized)
        if notion_url:
            print(f"Also shared to Notion: {notion_url}")
    
    return filepath
