"""
Agent 5: Categorization Agent
Tags articles with categories (TOOLS_AND_FRAMEWORKS, MODELS_AND_INFRASTRUCTURE, etc.)
"""
from typing import List, Dict, Any
import config
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_community.cache import SQLiteCache
from langchain.globals import set_llm_cache
import sqlite3
import os
import hashlib
import json
from datetime import datetime
from cache_utils import CacheTracker
from collections import Counter

# Import categories from config
CATEGORIES = config.CATEGORIES

class CategorizationAgent:
    def __init__(self, api_key=None, model=None):
        """Initialize the Categorization Agent"""
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
        self.cache_tracker = CacheTracker()
        
        # Use GPT-3.5 Turbo for categorization (cost-effective)
        self.model = model or config.MODELS.get("categorization", config.OPENAI_MODEL)
        self.categories = list(CATEGORIES.keys())
        print(f"🏷️ CATEGORIZATION AGENT: Using {self.model} for cost-effective categorization")
        
        # Initialize LangChain components
        self.llm = ChatOpenAI(
            model_name=self.model,
            openai_api_key=self.api_key,
            temperature=0.2,
            request_timeout=30
        )
        
        # Categorization prompt
        self.categorization_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a categorization agent. Classify articles into predefined categories."),
            ("user", """Classify the article into one of the following categories:
- TOOLS_AND_FRAMEWORKS
- MODELS_AND_INFRASTRUCTURE  
- ENTERPRISE_USE_CASES
- INDUSTRY_AND_MARKET

Title: {title}
Summary: {summary}

Respond with:
{{
  "category": "...",
  "justification": "..."
}}""")
        ])
    
    def _get_cache_key(self, title: str, content: str) -> str:
        """Generate a cache key for an article"""
        text = f"category:{title}:{content}"
        return hashlib.md5(text.encode()).hexdigest()
    
    def _check_cache(self, cache_key: str) -> tuple:
        """Check if article categorization is cached"""
        conn = sqlite3.connect(self.cache_db)
        cursor = conn.cursor()
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS article_categories
        (cache_key TEXT PRIMARY KEY, category TEXT, justification TEXT, timestamp TEXT)
        """)
        
        cursor.execute("SELECT category, justification FROM article_categories WHERE cache_key = ?", (cache_key,))
        result = cursor.fetchone()
        
        conn.close()
        return result if result else (None, None)
    
    def _save_cache(self, cache_key: str, category: str, justification: str):
        """Save categorization to cache"""
        conn = sqlite3.connect(self.cache_db)
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT OR REPLACE INTO article_categories (cache_key, category, justification, timestamp) VALUES (?, ?, ?, ?)",
            (cache_key, category, justification, datetime.now().isoformat())
        )
        
        conn.commit()
        conn.close()

    def categorize_articles(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Categorize articles into predefined categories"""
        print(f"\n🏷️ CATEGORIZATION AGENT: Categorizing {len(articles)} articles...")
        
        categorized_articles = []
        for article in articles:
            title = article.get('title', '')
            summary = article.get('summary', article.get('content', ''))[:500]
            
            cache_key = self._get_cache_key(title, summary)
            cached_category, cached_justification = self._check_cache(cache_key)
            
            if cached_category is not None:
                self.cache_tracker.record_hit()
                article['category'] = cached_category
                article['category_justification'] = cached_justification
            else:
                self.cache_tracker.record_miss()
                
                try:
                    response = (self.categorization_prompt | self.llm).invoke({
                        "title": title,
                        "summary": summary
                    })
                    
                    result = json.loads(response.content.strip())
                    category = result.get('category', 'INDUSTRY_AND_MARKET')
                    justification = result.get('justification', 'No justification provided')
                    
                    # Validate category
                    if category not in self.categories:
                        category = 'INDUSTRY_AND_MARKET'
                    
                    self._save_cache(cache_key, category, justification)
                    
                    article['category'] = category
                    article['category_justification'] = justification
                    
                except Exception as e:
                    print(f"Error in categorization agent for '{title}': {str(e)}")
                    article['category'] = 'INDUSTRY_AND_MARKET'
                    article['category_justification'] = 'Error in categorization'
            
            categorized_articles.append(article)
        
        # Print category distribution
        categories = [a.get('category', 'UNKNOWN') for a in categorized_articles]
        category_counts = Counter(categories)
        print("✅ Category distribution:")
        for cat, count in category_counts.items():
            print(f"  {cat}: {count} articles")
        
        # Print cache statistics
        stats = self.cache_tracker.get_stats()
        print(f"Cache Stats - Hits: {stats['hits']}, Misses: {stats['misses']}, Hit Rate: {stats['hit_rate']}")
        
        return categorized_articles

# Helper function for easy use
def categorize_by_topic(articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Helper function for categorizing articles"""
    agent = CategorizationAgent()
    return agent.categorize_articles(articles)

if __name__ == "__main__":
    # Test the categorization agent
    from fetcher import RSSFetcher
    import keyword_filter
    
    fetcher = RSSFetcher()
    articles = fetcher.fetch_articles()
    filtered_articles = keyword_filter.filter_articles(articles)
    
    agent = CategorizationAgent()
    categorized = agent.categorize_articles(filtered_articles[:10])
    print(f"\nCategorized articles: {len(categorized)}") 