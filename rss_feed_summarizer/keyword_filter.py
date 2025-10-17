"""
Article filter for RSS feeds
"""
from typing import List, Dict, Any
from datetime import datetime
from . import config

# Import categories from config
CATEGORIES = config.CATEGORIES

def filter_articles(articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Filter articles based on relevance to enterprise AI workflows
    """
    filtered_articles = []
    
    for article in articles:
        # Skip articles without content
        if not article.get('title') or not (article.get('content') or article.get('summary')):
            continue
            
        # Combine text fields for matching
        title = article.get('title', '').lower()
        content = article.get('content', '').lower()
        summary = article.get('summary', '').lower()
        url = article.get('link', '').lower()
        text = f"{title} {content} {summary}"
        
        # Count matches across all categories
        total_matches = 0
        category_matches = set()
        
        for category, patterns in CATEGORIES.items():
            # Check keywords
            for keyword in patterns['keywords']:
                if keyword.lower() in text:
                    total_matches += 1
                    category_matches.add(category)
                    
            # Check URL patterns
            for pattern in patterns['url_patterns']:
                if pattern.lower() in url:
                    total_matches += 1
                    category_matches.add(category)
        
        # Relaxed criteria: Keep article if it has matches from at least 1 category OR 2+ total matches
        if len(category_matches) >= 1 or total_matches >= 2:
            article['match_score'] = total_matches
            filtered_articles.append(article)
    
    # Sort by match score - let LLM relevance filtering decide final count
    filtered_articles.sort(key=lambda x: x.get('match_score', 0), reverse=True)
    
    print(f"\nFiltered from {len(articles)} to {len(filtered_articles)} articles based on keywords")
    return filtered_articles

def assign_category(article: Dict[str, Any]) -> str:
    """
    Assign an article to one of the four categories based on content and URL
    """
    title = article.get('title', '').lower()
    content = article.get('content', '').lower()
    summary = article.get('summary', '').lower()
    url = article.get('link', '').lower()
    
    # Combine text for matching
    text = f"{title} {content} {summary}"
    
    # Score for each category
    scores = {category: 0 for category in CATEGORIES.keys()}
    
    for category, patterns in CATEGORIES.items():
        # Check keywords
        for keyword in patterns['keywords']:
            if keyword.lower() in text:
                scores[category] += 1
        
        # Check URL patterns
        for pattern in patterns['url_patterns']:
            if pattern.lower() in url:
                scores[category] += 2
    
    # Return category with highest score, default to INDUSTRY_AND_MARKET
    max_score = max(scores.values())
    if max_score > 0:
        for category, score in scores.items():
            if score == max_score:
                return category
    
    return 'INDUSTRY_AND_MARKET'

def score_relevance(article: Dict[str, Any]) -> int:
    """
    Score article relevance from 1-10 based on enterprise AI workflow value
    """
    title = article.get('title', '').lower()
    content = article.get('content', '').lower()
    summary = article.get('summary', '').lower()
    url = article.get('link', '').lower()
    
    score = 5  # Start with neutral score
    
    # Technical depth indicators
    technical_terms = [
        'architecture', 'implementation', 'performance', 'benchmark',
        'optimization', 'scalability', 'infrastructure', 'technical'
    ]
    
    # Enterprise relevance indicators
    enterprise_terms = [
        'enterprise', 'business', 'production', 'deployment', 'integration',
        'workflow', 'solution', 'roi', 'cost', 'efficiency'
    ]
    
    # LLM/RAG/Agent relevance
    llm_terms = [
        'llm', 'language model', 'rag', 'retrieval', 'augmented', 'agent',
        'automation', 'embedding', 'vector', 'semantic', 'prompt'
    ]
    
    text = f"{title} {content} {summary}"
    
    # Score technical depth
    tech_matches = sum(1 for term in technical_terms if term in text)
    score += min(2, tech_matches)
    
    # Score enterprise applicability
    ent_matches = sum(1 for term in enterprise_terms if term in text)
    score += min(2, ent_matches)
    
    # Score LLM/RAG relevance
    llm_matches = sum(1 for term in llm_terms if term in text)
    score += min(2, llm_matches)
    
    # Bonus for high-quality sources
    quality_sources = [
        'arxiv.org', 'github.com', 'paperswithcode.com',
        'huggingface.co', 'microsoft.com', 'google.com', 'openai.com'
    ]
    if any(source in url for source in quality_sources):
        score += 1
    
    # Ensure score is between 1 and 10
    return max(1, min(10, score))

def categorize_articles(articles: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Categorize articles and assign relevance scores
    """
    categorized = {key: [] for key in CATEGORIES}

    for article in articles:
        category = assign_category(article)
        article['category'] = category
        article['relevance_score'] = score_relevance(article)
        categorized[category].append(article)

    for category, articles_list in categorized.items():
        if articles_list:
            print(f"Category {category}: {len(articles_list)} articles")

    return categorized

if __name__ == "__main__":
    # Test filter
    from fetcher import RSSFetcher
    
    fetcher = RSSFetcher()
    all_articles = fetcher.fetch_articles()
    
    filtered = filter_articles(all_articles)
    categorized = categorize_articles(filtered)
    
    print(f"Filtered {len(filtered)} articles from {len(all_articles)} total")
    for category, articles in categorized.items():
        if articles:
            print(f"{category}: {len(articles)} articles")