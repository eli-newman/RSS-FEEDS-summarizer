"""
Agent 3: Macro Summary Agent (Daily Digest Insight Generator)
Creates high-level daily digest overviews
"""
from typing import List, Dict, Any
from . import config
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_community.cache import SQLiteCache
from langchain.globals import set_llm_cache
import sqlite3
import os
import hashlib
from datetime import datetime
from .cache_utils import CacheTracker

class MacroSummaryAgent:
    def __init__(self, api_key=None, model=None):
        """Initialize the Macro Summary Agent"""
        self.api_key = api_key or config.OPENAI_API_KEY
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
        
        # Set up cache
        self.cache_dir = "cache"
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
        
        self.cache_db = f"{self.cache_dir}/langchain.db"
        set_llm_cache(SQLiteCache(database_path=self.cache_db))
        
        # Initialize cache tracker
        self.cache_tracker = CacheTracker(cost_per_call=0.03)
        
        # Use GPT-3.5 Turbo for macro summary (cost-effective)
        self.model = model or config.MODELS.get("macro_summary", config.OPENAI_MODEL)
        print(f"📄 MACRO SUMMARY AGENT: Using {self.model} for cost-effective daily overview")
        
        # Initialize LangChain components
        self.llm = ChatOpenAI(
            model_name=self.model,
            openai_api_key=self.api_key,
            temperature=0.3,
            request_timeout=30
        )
        
        # Macro summary prompt
        self.macro_summary_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a macro summary agent that creates high-level newsletter introductions summarizing daily AI trends."),
            ("user", """Analyze the following list of article titles and summaries. Generate a 3–5 sentence newsletter introduction summarizing the biggest trends or common themes for the day.

Articles:
{articles}

Example Output:
"Today's AI news was dominated by multi-agent collaboration (MCP), with Amazon Bedrock leading the charge. We also saw major investments into chat-based AI, such as xAI's $300M deal with Telegram. Additionally, new AI-powered productivity tools and browsers are emerging fast."

Newsletter Introduction:""")
        ])
    
    def _get_cache_key(self, content: str) -> str:
        """Generate a cache key for content"""
        text = f"macro_summary:{content}"
        return hashlib.md5(text.encode()).hexdigest()
    
    def _check_cache(self, cache_key: str) -> str:
        """Check if summary is cached"""
        conn = sqlite3.connect(self.cache_db)
        cursor = conn.cursor()
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS macro_summaries
        (cache_key TEXT PRIMARY KEY, summary TEXT, timestamp TEXT)
        """)
        
        cursor.execute("SELECT summary FROM macro_summaries WHERE cache_key = ?", (cache_key,))
        result = cursor.fetchone()
        
        conn.close()
        return result[0] if result else None
    
    def _save_cache(self, cache_key: str, summary: str):
        """Save summary result to cache"""
        conn = sqlite3.connect(self.cache_db)
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT OR REPLACE INTO macro_summaries (cache_key, summary, timestamp) VALUES (?, ?, ?)",
            (cache_key, summary, datetime.now().isoformat())
        )
        
        conn.commit()
        conn.close()

    def generate_overview(self, articles: List[Dict[str, Any]]) -> str:
        """Generate a high-level daily digest introduction"""
        if not articles:
            return "No articles to analyze today."
        
        print(f"\n📄 MACRO SUMMARY AGENT: Generating daily digest overview from {len(articles)} articles...")
        
        # Prepare article list for analysis
        article_texts = []
        for i, article in enumerate(articles, 1):
            title = article.get('title', 'No Title')
            summary = article.get('summary', article.get('content', ''))[:300]
            source = article.get('source', 'Unknown')
            article_texts.append(f"{i}. Title: {title}\n   Source: {source}\n   Summary: {summary}")
        
        combined_articles = "\n\n".join(article_texts)
        
        # Create cache key based on all article titles and sources
        cache_input = "".join(sorted([f"{a.get('title','')}{a.get('source','')}" for a in articles]))
        cache_key = self._get_cache_key(cache_input)
        
        cached_summary = self._check_cache(cache_key)
        if cached_summary:
            self.cache_tracker.record_hit()
            print("✅ Macro summary retrieved from cache")
            return cached_summary
        
        self.cache_tracker.record_miss()
        
        try:
            response = (self.macro_summary_prompt | self.llm).invoke({
                "articles": combined_articles
            })
            
            summary = response.content.strip()
            self._save_cache(cache_key, summary)
            print("✅ Macro summary generated")
            
            # Print cache statistics
            stats = self.cache_tracker.get_stats()
            print(f"Cache Stats - Hits: {stats['hits']}, Misses: {stats['misses']}, Hit Rate: {stats['hit_rate']}")
            
            return summary
            
        except Exception as e:
            print(f"Error in macro summary agent: {str(e)}")
            return "Error generating daily digest overview."

# Helper function for easy use
def generate_daily_overview(articles: List[Dict[str, Any]]) -> str:
    """Helper function for macro summary generation"""
    agent = MacroSummaryAgent()
    return agent.generate_overview(articles)

if __name__ == "__main__":
    # Test the macro summary agent
    from fetcher import RSSFetcher
    import keyword_filter
    
    fetcher = RSSFetcher()
    articles = fetcher.fetch_articles()
    filtered_articles = keyword_filter.filter_articles(articles)
    
    agent = MacroSummaryAgent()
    overview = agent.generate_overview(filtered_articles[:10])
    print(f"\nDaily Overview: {overview}") 