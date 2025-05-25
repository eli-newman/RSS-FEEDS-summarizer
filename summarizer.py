"""
AI-powered article summarizer
"""
import os
import time
from typing import List, Dict, Any
from openai import OpenAI
from tqdm import tqdm
import config

class ArticleSummarizer:
    def __init__(self, api_key=None, model=None):
        """
        Initialize the summarizer with OpenAI credentials
        
        Args:
            api_key: OpenAI API key (defaults to config.OPENAI_API_KEY)
            model: OpenAI model to use for summarization
        """
        self.api_key = api_key or config.OPENAI_API_KEY
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
        
        self.model = model or config.OPENAI_MODEL
        self.client = OpenAI(api_key=self.api_key)
    
    def summarize_article(self, article: Dict[str, Any]) -> str:
        """
        Generate a concise 2-sentence summary of an article
        
        Args:
            article: Article dictionary containing title, content, etc.
            
        Returns:
            Concise AI-generated summary
        """
        # Combine title and content
        title = article.get('title', '')
        content = article.get('content', article.get('summary', ''))
        
        # Limit content length to avoid excessive token usage
        if len(content) > 8000:
            content = content[:8000] + "..."
        
        try:
            # Create prompt for summarization
            prompt = f"""Summarize the following article in EXACTLY 2 sentences. 
            The first sentence should capture the most important point.
            The second sentence should provide the most critical detail or implication.
            Be direct and informative. less is more. 
            
            Title: {title}
            
            Content: {content}
            
            Two-sentence summary:"""
            
            # Generate summary using OpenAI
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that creates concise, informative summaries of technical articles in exactly 2 sentences."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100,
                temperature=0.3  # Low temperature for more focused summary
            )
            
            summary = response.choices[0].message.content.strip()
            return summary
            
        except Exception as e:
            print(f"Error summarizing article '{title}': {str(e)}")
            # Return original summary if available, otherwise a snippet of content
            return article.get('summary', content[:200] + "...")
    
    def batch_summarize(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Summarize a batch of articles
        
        Args:
            articles: List of article dictionaries
            
        Returns:
            List of articles with added AI summaries
        """
        summarized_articles = []
        
        print(f"Generating AI summaries for {len(articles)} articles...")
        for article in tqdm(articles):
            # Generate summary for all articles
            ai_summary = self.summarize_article(article)
            
            # Add summary to article, replacing the original summary
            article_copy = article.copy()
            article_copy['ai_summary'] = ai_summary
            article_copy['summary'] = ai_summary  # Replace original summary
            summarized_articles.append(article_copy)
            
            # Brief pause to avoid rate limits
            time.sleep(0.5)
            
        return summarized_articles

if __name__ == "__main__":
    # Test the summarizer on a few articles
    from fetcher import RSSFetcher
    import filter
    
    # Fetch and filter articles
    fetcher = RSSFetcher()
    articles = fetcher.fetch_articles()
    filtered_articles = filter.filter_articles(articles)
    
    # Summarize a few articles for testing
    summarizer = ArticleSummarizer()
    summarized = summarizer.batch_summarize(filtered_articles[:3])  # Just test with 3 articles
    
    # Display results
    for i, article in enumerate(summarized):
        print(f"\n--- Article {i+1} ---")
        print(f"Title: {article['title']}")
        print(f"Original length: {len(article.get('content', ''))}")
        print(f"AI Summary: {article['ai_summary']}") 