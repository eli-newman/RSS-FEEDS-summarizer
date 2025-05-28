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
    
    # Iterate through each article and check for topic matches
    for article in articles:
        # Extract searchable text fields
        title = article['title'].lower()
        content = (article['content'] or '').lower()
        summary = (article['summary'] or '').lower()
        
        # Check each topic against all text fields
        for topic in topics:
            topic_lower = topic.lower()
            # If any topic matches in any field, keep the article
            if (topic_lower in title or 
                topic_lower in content or 
                topic_lower in summary):
                filtered_articles.append(article)
                break  # Article matched, no need to check other topics
    
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
    # Initialize category buckets from config
    categorized = {}
    for category in config.CATEGORIES.keys():
        categorized[category] = []
    
    # Add default "OTHER" category if not in config
    if "OTHER" not in categorized:
        categorized["OTHER"] = []
    
    # Categorize each article based on keyword matching
    for article in articles:
        # Extract searchable text fields
        title = article['title'].lower()
        content = (article['content'] or '').lower()
        summary = (article['summary'] or '').lower()
        
        # Research category: Academic/scientific content
        if any(term in title or term in content or term in summary 
               for term in ['research', 'study', 'paper', 'published']):
            categorized['RESEARCH'].append(article)
            
        # AI Tools category: Products and applications
        elif any(term in title or term in content or term in summary 
                for term in ['tool', 'app', 'application', 'platform', 'launch']):
            categorized['AI_TOOLS'].append(article)
            
        # Industry News category: Business and market updates
        elif any(term in title or term in content or term in summary 
                for term in ['industry', 'company', 'business', 'market', 'startup']):
            categorized['INDUSTRY_NEWS'].append(article)
            
        # Product Ideas category: Conceptual and innovative content
        elif any(term in title or term in content or term in summary 
                for term in ['idea', 'concept', 'innovation', 'potential']):
            categorized['PRODUCT_IDEAS'].append(article)
            
        # Default category for unmatched articles
        else:
            categorized['OTHER'].append(article)
    
    # Print distribution of articles across categories
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