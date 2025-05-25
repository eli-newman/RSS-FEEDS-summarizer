"""
Article filter for RSS feeds
"""
from typing import List, Dict, Any
import config

def filter_articles(articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Filter articles based on topics of interest from config.py
    
    Args:
        articles: List of article dictionaries from the fetcher
        
    Returns:
        Filtered list of articles
    """
    filtered_articles = []
    topics = config.TOPICS_OF_INTEREST
    
    for article in articles:
        # Check if any topic appears in the article title or content
        title = article['title'].lower()
        content = (article['content'] or '').lower()
        summary = (article['summary'] or '').lower()
        
        for topic in topics:
            topic_lower = topic.lower()
            if (topic_lower in title or 
                topic_lower in content or 
                topic_lower in summary):
                filtered_articles.append(article)
                break  # No need to check other topics once we find a match
    
    print(f"Filtered from {len(articles)} to {len(filtered_articles)} articles")
    return filtered_articles

def categorize_articles(articles: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Categorize articles based on predefined categories in config.py
    
    Args:
        articles: List of article dictionaries
        
    Returns:
        Dictionary mapping category names to lists of articles
    """
    categorized = {}
    
    # Initialize categories from config
    for category in config.CATEGORIES.keys():
        categorized[category] = []
    
    # Add a default "OTHER" category if not in config
    if "OTHER" not in categorized:
        categorized["OTHER"] = []
    
    # Simple categorization based on keywords
    # This could be enhanced with ML-based classification in the future
    for article in articles:
        title = article['title'].lower()
        content = (article['content'] or '').lower()
        summary = (article['summary'] or '').lower()
        
        # For now, using a simple rule-based categorization
        if any(term in title or term in content or term in summary 
               for term in ['research', 'study', 'paper', 'published']):
            categorized['RESEARCH'].append(article)
        elif any(term in title or term in content or term in summary 
                for term in ['tool', 'app', 'application', 'platform', 'launch']):
            categorized['AI_TOOLS'].append(article)
        elif any(term in title or term in content or term in summary 
                for term in ['industry', 'company', 'business', 'market', 'startup']):
            categorized['INDUSTRY_NEWS'].append(article)
        elif any(term in title or term in content or term in summary 
                for term in ['idea', 'concept', 'innovation', 'potential']):
            categorized['PRODUCT_IDEAS'].append(article)
        else:
            categorized['OTHER'].append(article)
    
    # Print categorization summary
    for category, articles_list in categorized.items():
        if articles_list:  # Only print non-empty categories
            print(f"Category {category}: {len(articles_list)} articles")
    
    return categorized

if __name__ == "__main__":
    # For testing purposes
    from fetcher import RSSFetcher
    
    # Fetch articles
    fetcher = RSSFetcher()
    all_articles = fetcher.fetch_articles()
    
    # Filter and categorize
    filtered = filter_articles(all_articles)
    categorized = categorize_articles(filtered) 