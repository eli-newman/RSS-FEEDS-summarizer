"""
Configuration settings for RSS Feed Summarizer
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# RSS Feed URLs - Focused on AI automation and tools
RSS_FEEDS = [
    "https://huggingface.co/blog/feed.xml", # Hugging Face Blog → Cutting-edge AI models, LLMs, and open-source tools.	
    "https://thesequence.substack.com/feed",
    "https://thegradient.pub/rss/",
    "https://blog.google/technology/ai/rss/",
    "https://www.microsoft.com/en-us/research/blog/feed/",
    "https://openai.com/blog/rss.xml",
    "https://aws.amazon.com/blogs/machine-learning/feed/",
    "https://www.kdnuggets.com/feed", # Covers model comparisons, benchmarks, and AI trends.
    "https://blog.langchain.dev/rss/", # LangChain Blog → Building AI applications with LangChain.
    
    # Enterprise AI & Business Applications
    "https://venturebeat.com/ai/feed/",  # VentureBeat AI - Enterprise AI news
    "https://techcrunch.com/category/artificial-intelligence/feed/",  # TechCrunch AI
    "https://developer.nvidia.com/blog/feed/",  # NVIDIA Developer Blog
    "https://pytorch.org/blog/feed.xml",  # PyTorch Blog
    "https://www.artificialintelligence-news.com/feed/",  # AI News
    
    # Additional Quality Sources
    "https://www.theregister.com/headlines.atom",  # The Register - Tech news
    "https://www.infoworld.com/category/artificial-intelligence/rss",  # InfoWorld AI
    "https://www.zdnet.com/topic/artificial-intelligence/rss.xml",  # ZDNet AI
]

# Time window for fetching articles (in hours)
# Set to 24 for daily or 168 for weekly (7 days)
TIME_WINDOW = 14 #hours

# Topics of interest - Focused on automation and tools
TOPICS_OF_INTEREST = [
    "Automation",
    "AI Tool",
    "Artificial Intelligence",
    "Large Language Model",
    "API",
    "Integration",
    "Workflow",
    "Developer Tools",
    "Productivity",
    "Code Generation",
    "Cloud Computing",
    "Enterprise AI",
]

# Categories for article classification
CATEGORIES = {
    "TOOLS_AND_FRAMEWORKS": {
        "emoji": "🛠️",
        "keywords": [
            "agent", "mcp", "framework", "sdk", "platform", "tool", "api",
            "langchain", "autogen", "crewai", "bedrock", "workflow engine"
        ],
        "url_patterns": ["langchain.dev", "mistral", "bedrock", "huggingface", "github"]
    },
    "MODELS_AND_INFRASTRUCTURE": {
        "emoji": "⚡",
        "keywords": [
            "llm", "language model", "gpt", "transformer", "training",
            "fine-tuning", "infrastructure", "scaling", "deployment",
            "embedding", "vector", "inference", "optimization"
        ],
        "url_patterns": ["openai", "huggingface", "anthropic", "arxiv", "microsoft", "aws"]
    },
    "ENTERPRISE_USE_CASES": {
        "emoji": "📈",
        "keywords": [
            "enterprise", "production", "deployment", "integration", "solution",
            "business case", "case study", "roi", "customer", "automation"
        ],
        "url_patterns": ["aws.amazon.com", "cloud.google.com", "case-study", "blog"]
    },
    "INDUSTRY_AND_MARKET": {
        "emoji": "📚",
        "keywords": [
            "market", "startup", "funding", "ipo", "partnership", "acquisition",
            "industry", "trend", "valuation", "launch"
        ],
        "url_patterns": ["venturebeat", "techcrunch", "forbes", "businessinsider"]
    }
}

# Distribution channels
DISTRIBUTION = {
    "email": {
        "enabled": True,  # Set to True to enable email distribution
        "recipient": os.getenv("EMAIL_RECIPIENTS", ""),  # Comma-separated list of recipients from .env file
        "sender": os.getenv("SMTP_USER", ""),     # Add sender email (e.g., your-email@gmail.com)
        "subject": "Your Daily AI News Digest",
        # Standard SMTP settings
        "smtp_server": "smtp.gmail.com",  # For Gmail
        "smtp_port": 465,  # For SSL
        "smtp_user": os.getenv("SMTP_USER"),  # Usually same as sender
        "smtp_password": os.getenv("GMAIL_APP_PASSWORD"),  # For Gmail, use an App Password: https://myaccount.google.com/apppasswords
    }
}

# OpenAI API configuration
OPENAI_API_KEY = os.getenv("OPENAIAPIKEY")

# Model configuration - use GPT-4 for relevance (most important), GPT-3.5-turbo for others
MODELS = {
    "relevance": "gpt-4",
    "categorization": "gpt-3.5-turbo",
    "ranking": "gpt-3.5-turbo",
    "macro_summary": "gpt-3.5-turbo",
    "micro_summary": "gpt-3.5-turbo",
}

# Default model (kept for backward compatibility)
OPENAI_MODEL = "gpt-3.5-turbo" 