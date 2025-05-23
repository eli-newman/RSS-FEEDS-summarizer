"""
Configuration settings for RSS Feed Summarizer
"""

# RSS Feed URLs - Add your preferred sources
RSS_FEEDS = [
    "https://www.producthunt.com/feed",  #Product Hunt - Latest AI-powered apps, tools, and startups launching daily.
    "https://huggingface.co/blog/feed.xml", #Hugging Face Blog → Cutting-edge AI models, LLMs, and open-source tools.	
    "https://venturebeat.com/category/ai/feed/",
    "https://www.technologyreview.com/feed/", #MIT Technology Review - AI → Deep insights into AI’s impact on society & industry.
    "https://thesequence.substack.com/feed",
    "https://thegradient.pub/rss/",
    "https://aisnakeoil.substack.com/feed",
    # Add more feeds here
]

# Time window for fetching articles (in hours)
# Set to 24 for daily or 168 for weekly (7 days)
TIME_WINDOW = 48 #hours

# Topics of interest for filtering
TOPICS_OF_INTEREST = [
    "AI",
    "Machine Learning",
    "LLMs",
    "Startups",
    "Technology",
    # Add more topics here
]

# Categories for article classification
CATEGORIES = {
    "RESEARCH": "📚",
    "AI_TOOLS": "🧠",
    "INDUSTRY_NEWS": "📈",
    "PRODUCT_IDEAS": "💡",
}

# Distribution channels
DISTRIBUTION = {
    "slack": {
        "enabled": False,
        "webhook_url": "",  # Add your Slack webhook URL
        "channel": "#ai-news",
    },
    "email": {
        "enabled": False,
        "recipient": "",  # Add recipient email
        "sender": "",     # Add sender email
        "subject": "Your Daily AI News Digest",
    },
    "notion": {
        "enabled": False,
        "token": "",      # Add your Notion API token
        "database_id": "", # Add your Notion database ID
    }
}

# OpenAI API configuration
OPENAI_MODEL = "gpt-4"  # Or another model like "gpt-3.5-turbo"

# Logging configuration
LOGGING = {
    "level": "INFO",
    "file": "rss_summarizer.log",
} 