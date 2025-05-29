"""
Agent 4: Ranking Agent
Orders articles by priority based on innovation, utility, and strategic impact
"""
from typing import List, Dict, Any
import config
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_community.cache import SQLiteCache
from langchain.globals import set_llm_cache
import os
import json
from cache_utils import CacheTracker

class RankingAgent:
    def __init__(self, api_key=None, model=None):
        """Initialize the Ranking Agent"""
        self.api_key = api_key or config.OPENAI_API_KEY
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
        
        # Set up cache
        self.cache_dir = "cache"
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
        
        set_llm_cache(SQLiteCache(database_path=f"{self.cache_dir}/langchain.db"))
        
        # Initialize cache tracker
        self.cache_tracker = CacheTracker()
        
        # Use GPT-3.5 Turbo for ranking (cost-effective)
        self.model = model or config.MODELS.get("ranking", config.OPENAI_MODEL)
        print(f"📊 RANKING AGENT: Using {self.model} for cost-effective ranking")
        
        # Initialize LangChain components
        self.llm = ChatOpenAI(
            model_name=self.model,
            openai_api_key=self.api_key,
            temperature=0.2,
            request_timeout=30
        )
        
        # Ranking prompt
        self.ranking_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a ranking agent. Order articles by priority based on innovation, utility, and strategic impact for a tech-savvy AI audience."),
            ("user", """Rank the following articles from most to least relevant for a tech-savvy AI audience based on innovation, utility, or strategic impact.

Articles:
{articles}

Return a JSON array of article indices (0-based) in order of importance: [2, 0, 1, 3, 4]""")
        ])

    def rank_articles(self, articles: List[Dict[str, Any]], max_articles: int = 5) -> List[Dict[str, Any]]:
        """Rank articles by importance and return top N"""
        if len(articles) <= max_articles:
            return articles
        
        print(f"\n📊 RANKING AGENT: Ranking {len(articles)} articles, selecting top {max_articles}...")
        
        # Prepare article summaries for ranking
        article_texts = []
        for i, article in enumerate(articles):
            title = article.get('title', 'No Title')
            summary = article.get('summary', article.get('content', ''))[:200]
            source = article.get('source', 'Unknown')
            article_texts.append(f"[{i}] {title} (from {source})\n{summary}")
        
        try:
            response = (self.ranking_prompt | self.llm).invoke({
                "articles": "\n\n".join(article_texts)
            })
            
            # Parse indices from response
            response_text = response.content.strip()
            if response_text.startswith('[') and response_text.endswith(']'):
                indices = json.loads(response_text)
                indices = indices[:max_articles]
                ranked_articles = [articles[i] for i in indices if i < len(articles)]
                print(f"✅ Selected top {len(ranked_articles)} articles")
                
                # Print cache statistics
                stats = self.cache_tracker.get_stats()
                print(f"Cache Stats - Hits: {stats['hits']}, Misses: {stats['misses']}, Hit Rate: {stats['hit_rate']}")
                
                return ranked_articles
            
        except Exception as e:
            print(f"Error in ranking agent: {str(e)}")
        
        # Fallback: return first N articles
        print(f"⚠️ Ranking failed, returning first {max_articles} articles")
        return articles[:max_articles]

# Helper function for easy use
def rank_articles_by_importance(articles: List[Dict[str, Any]], max_articles: int = 5) -> List[Dict[str, Any]]:
    """Helper function for ranking articles"""
    agent = RankingAgent()
    return agent.rank_articles(articles, max_articles)

if __name__ == "__main__":
    # Test the ranking agent
    from fetcher import RSSFetcher
    import keyword_filter
    
    fetcher = RSSFetcher()
    articles = fetcher.fetch_articles()
    filtered_articles = keyword_filter.filter_articles(articles)
    
    agent = RankingAgent()
    ranked = agent.rank_articles(filtered_articles[:10], max_articles=5)
    print(f"\nRanked articles: {len(ranked)}") 