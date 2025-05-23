"""
Content distributor for sending summarized articles to different platforms
"""
from typing import List, Dict, Any
import requests
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import config
from datetime import datetime

class ContentDistributor:
    def __init__(self, distribution_config=None):
        self.config = distribution_config or config.DISTRIBUTION
    
    def distribute_articles(self, articles: List[Dict[str, Any]]) -> None:
        """
        Distribute articles to configured platforms
        """
        if not articles:
            print("No articles to distribute")
            return
        
        # Group articles by category
        categorized = {}
        for article in articles:
            category = article.get('category', 'OTHER')
            if category not in categorized:
                categorized[category] = []
            categorized[category].append(article)
        
        # Send to enabled distribution channels
        if self.config.get('slack', {}).get('enabled'):
            self.send_to_slack(articles, categorized)
        
        if self.config.get('email', {}).get('enabled'):
            self.send_email(articles, categorized)
        
        if self.config.get('notion', {}).get('enabled'):
            self.send_to_notion(articles)
    
    def send_to_slack(self, articles: List[Dict[str, Any]], categorized: Dict[str, List]) -> None:
        """
        Send articles to Slack channel
        """
        try:
            webhook_url = self.config.get('slack', {}).get('webhook_url')
            if not webhook_url:
                print("Slack webhook URL not configured")
                return
            
            # Create message
            today = datetime.now().strftime("%Y-%m-%d")
            message = f"*RSS Feed Summary for {today}*\n\n"
            
            # Add articles by category
            for category, category_articles in categorized.items():
                if category_articles:
                    emoji = category_articles[0].get('category_emoji', '')
                    message += f"\n*{emoji} {category}*\n"
                    
                    for article in category_articles:
                        title = article.get('title', 'Untitled')
                        link = article.get('link', '')
                        summary = article.get('ai_summary', '')
                        
                        message += f"• <{link}|{title}>\n"
                        message += f"_{summary}_\n\n"
            
            # Send to Slack
            payload = {
                "text": message
            }
            
            response = requests.post(webhook_url, json=payload)
            if response.status_code == 200:
                print("Successfully sent to Slack")
            else:
                print(f"Failed to send to Slack. Status code: {response.status_code}")
        
        except Exception as e:
            print(f"Error sending to Slack: {str(e)}")
    
    def send_email(self, articles: List[Dict[str, Any]], categorized: Dict[str, List]) -> None:
        """
        Send articles via email
        """
        try:
            email_config = self.config.get('email', {})
            recipient = email_config.get('recipient')
            sender = email_config.get('sender')
            subject = email_config.get('subject')
            
            if not all([recipient, sender, subject]):
                print("Email configuration incomplete")
                return
            
            # Get email server settings from environment variables
            smtp_server = os.environ.get('EMAIL_SERVER')
            smtp_port = int(os.environ.get('EMAIL_PORT', 587))
            smtp_username = os.environ.get('EMAIL_USERNAME')
            smtp_password = os.environ.get('EMAIL_PASSWORD')
            
            if not all([smtp_server, smtp_username, smtp_password]):
                print("Email server configuration incomplete")
                return
            
            # Create email
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = sender
            msg['To'] = recipient
            
            # Create email content
            today = datetime.now().strftime("%Y-%m-%d")
            html_content = f"""
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; color: #333; }}
                    h1 {{ color: #2c3e50; }}
                    h2 {{ color: #3498db; margin-top: 30px; }}
                    .article {{ margin-bottom: 20px; border-left: 4px solid #3498db; padding-left: 15px; }}
                    .title {{ font-weight: bold; margin-bottom: 5px; }}
                    .summary {{ color: #555; margin-bottom: 10px; }}
                    a {{ color: #3498db; text-decoration: none; }}
                    a:hover {{ text-decoration: underline; }}
                </style>
            </head>
            <body>
                <h1>RSS Feed Summary for {today}</h1>
            """
            
            # Add articles by category
            for category, category_articles in categorized.items():
                if category_articles:
                    emoji = category_articles[0].get('category_emoji', '')
                    html_content += f"<h2>{emoji} {category}</h2>"
                    
                    for article in category_articles:
                        title = article.get('title', 'Untitled')
                        link = article.get('link', '')
                        summary = article.get('ai_summary', '')
                        source = article.get('source', '')
                        
                        html_content += f"""
                        <div class="article">
                            <div class="title"><a href="{link}">{title}</a></div>
                            <div class="source">From: {source}</div>
                            <div class="summary">{summary}</div>
                        </div>
                        """
            
            html_content += """
            </body>
            </html>
            """
            
            # Attach HTML content
            part = MIMEText(html_content, 'html')
            msg.attach(part)
            
            # Send email
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(smtp_username, smtp_password)
                server.send_message(msg)
            
            print("Successfully sent email")
            
        except Exception as e:
            print(f"Error sending email: {str(e)}")
    
    def send_to_notion(self, articles: List[Dict[str, Any]]) -> None:
        """
        Add articles to Notion database
        """
        try:
            notion_config = self.config.get('notion', {})
            token = notion_config.get('token')
            database_id = notion_config.get('database_id')
            
            if not all([token, database_id]):
                print("Notion configuration incomplete")
                return
            
            # Import notion client here to avoid dependency if not used
            from notion_client import Client
            
            # Initialize Notion client
            notion = Client(auth=token)
            
            # Add each article to Notion
            for article in articles:
                title = article.get('title', 'Untitled')
                link = article.get('link', '')
                summary = article.get('ai_summary', '')
                category = article.get('category', 'OTHER')
                emoji = article.get('category_emoji', '')
                source = article.get('source', '')
                pub_date = article.get('published', datetime.now())
                
                # Format date for Notion
                if isinstance(pub_date, datetime):
                    pub_date_str = pub_date.strftime("%Y-%m-%d")
                else:
                    pub_date_str = datetime.now().strftime("%Y-%m-%d")
                
                # Create Notion page
                new_page = {
                    "parent": {"database_id": database_id},
                    "properties": {
                        "Title": {
                            "title": [
                                {
                                    "text": {
                                        "content": title
                                    }
                                }
                            ]
                        },
                        "Category": {
                            "select": {
                                "name": category
                            }
                        },
                        "Source": {
                            "rich_text": [
                                {
                                    "text": {
                                        "content": source
                                    }
                                }
                            ]
                        },
                        "URL": {
                            "url": link
                        },
                        "Date": {
                            "date": {
                                "start": pub_date_str
                            }
                        }
                    },
                    "children": [
                        {
                            "object": "block",
                            "type": "paragraph",
                            "paragraph": {
                                "rich_text": [
                                    {
                                        "type": "text",
                                        "text": {
                                            "content": summary
                                        }
                                    }
                                ]
                            }
                        }
                    ]
                }
                
                # Add to Notion
                notion.pages.create(**new_page)
                print(f"Added '{title}' to Notion")
                
        except Exception as e:
            print(f"Error sending to Notion: {str(e)}")

if __name__ == "__main__":
    # Simple test
    import os
    from fetcher import RSSFetcher
    from filter import ArticleFilter
    from categorizer import ArticleCategorizer
    from summarizer import ArticleSummarizer
    
    # Test with dummy article if necessary
    test_article = {
        'title': 'Test Article',
        'link': 'https://example.com',
        'ai_summary': 'This is a test summary for distribution testing.',
        'category': 'AI_TOOLS',
        'category_emoji': '🧠',
        'source': 'Test Source',
        'published': datetime.now()
    }
    
    # Create distributor
    distributor = ContentDistributor()
    
    # Enable test endpoints if needed for testing
    if os.environ.get("SLACK_WEBHOOK_URL"):
        distributor.config['slack']['enabled'] = True
        distributor.config['slack']['webhook_url'] = os.environ.get("SLACK_WEBHOOK_URL")
    
    # Distribute test article
    distributor.distribute_articles([test_article])
    
    print("Distribution test completed") 