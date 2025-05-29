"""
Agent 6: Micro Summary Agent (2-Sentence Summarizer)
Creates concise 2-3 sentence summaries for professional newsletters
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
from datetime import datetime
from cache_utils import CacheTracker

class MicroSummaryAgent:
    def __init__(self, api_key=None, model=None):
        """Initialize the Micro Summary Agent"""
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
        self.cache_tracker = CacheTracker(cost_per_call=0.03)  # Higher cost for summarization
        
        # Use GPT-3.5 Turbo for micro summaries (cost-effective)
        self.model = model or config.MODELS.get("micro_summary", config.OPENAI_MODEL)
        print(f"✏️ MICRO SUMMARY AGENT: Using {self.model} for cost-effective article summaries")
        
        # Initialize LangChain components
        self.llm = ChatOpenAI(
            model_name=self.model,
            openai_api_key=self.api_key,
            temperature=0.3,
            request_timeout=30
        )
        
        # Micro summary prompt
        self.micro_summary_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a micro summary agent that creates concise 2-3 sentence summaries for professional newsletters."),
            ("user", """Summarize the following article in 2–3 sentences for a professional newsletter. Emphasize what's new, why it matters, and who should care.

Title: {title}
Source: {source}
Full Text: {content}

2-3 Sentence Summary:""")
        ])
    
    def _get_cache_key(self, content: str) -> str:
        """Generate a cache key for content"""
        text = f"micro_summary:{content}"
        return hashlib.md5(text.encode()).hexdigest()
    
    def _check_cache(self, cache_key: str) -> str:
        """Check if summary is cached"""
        conn = sqlite3.connect(self.cache_db)
        cursor = conn.cursor()
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS micro_summaries
        (cache_key TEXT PRIMARY KEY, summary TEXT, timestamp TEXT)
        """)
        
        cursor.execute("SELECT summary FROM micro_summaries WHERE cache_key = ?", (cache_key,))
        result = cursor.fetchone()
        
        conn.close()
        return result[0] if result else None
    
    def _save_cache(self, cache_key: str, summary: str):
        """Save summary result to cache"""
        conn = sqlite3.connect(self.cache_db)
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT OR REPLACE INTO micro_summaries (cache_key, summary, timestamp) VALUES (?, ?, ?)",
            (cache_key, summary, datetime.now().isoformat())
        )
        
        conn.commit()
        conn.close()

    def summarize_article(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a 2-3 sentence summary for a single article"""
        title = article.get('title', '')
        content = article.get('content', article.get('summary', ''))
        source = article.get('source', 'Unknown')
        
        cache_key = self._get_cache_key(f"{title}:{content}")
        cached_summary = self._check_cache(cache_key)
        
        if cached_summary:
            self.cache_tracker.record_hit()
            article['summary'] = cached_summary
            return article
        
        self.cache_tracker.record_miss()
        
        try:
            response = (self.micro_summary_prompt | self.llm).invoke({
                "title": title,
                "source": source,
                "content": content
            })
            
            summary = response.content.strip()
            self._save_cache(cache_key, summary)
            
            article['summary'] = summary
            return article
            
        except Exception as e:
            print(f"Error in micro summary agent for '{title}': {str(e)}")
            article['summary'] = "Error generating summary"
            return article
    
    def summarize_articles(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate micro summaries for a list of articles"""
        print(f"\n✏️ MICRO SUMMARY AGENT: Generating summaries for {len(articles)} articles...")
        
        summarized = []
        for article in articles:
            summarized.append(self.summarize_article(article))
        
        # Print cache statistics
        stats = self.cache_tracker.get_stats()
        print("✅ Micro summaries complete")
        print(f"Cache Stats - Hits: {stats['hits']}, Misses: {stats['misses']}, Hit Rate: {stats['hit_rate']}")
        
        return summarized

# Helper function for easy use
def generate_article_summaries(articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Helper function for micro summary generation"""
    agent = MicroSummaryAgent()
    return agent.summarize_articles(articles)

# Legacy helper function for backward compatibility
def summarize_articles(articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Helper function to summarize articles using micro summary agent"""
    return generate_article_summaries(articles)

if __name__ == "__main__":
    # Test the micro summary agent
    from fetcher import RSSFetcher
    import keyword_filter
    
    fetcher = RSSFetcher()
    articles = fetcher.fetch_articles()
    filtered_articles = keyword_filter.filter_articles(articles)
    
    agent = MicroSummaryAgent()
    summarized = agent.summarize_articles(filtered_articles[:3])
    
    for i, article in enumerate(summarized):
        print(f"\n--- Article {i+1} ---")
        print(f"Title: {article['title']}")
        print(f"Summary: {article['summary']}") 