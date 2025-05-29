"""
Main pipeline orchestrating 6 AI agents for RSS feed processing

Agent Flow:
1. Ingestion Agent (fetcher.py) - Pulls articles from RSS feeds
2. Relevance Agent (relevance.py) - Filters for relevant articles
3. Macro Summary Agent (overall_summary.py) - Creates daily digest overview  
4. Categorization Agent (categorization.py) - Tags articles with categories
5. Ranking Agent (ranking.py) - Orders articles by priority PER CATEGORY (only if >5 articles)
6. Micro Summary Agent (summaries.py) - Creates 2-3 sentence summaries
"""
from fetcher import RSSFetcher  # Agent 1: Ingestion
from keyword_filter import filter_articles  # Keyword pre-filter
from relevance import filter_relevant_articles  # Agent 2: Relevance
from overall_summary import generate_daily_overview  # Agent 3: Macro Summary
from categorization import categorize_by_topic  # Agent 4: Categorization
from ranking import rank_articles_by_importance  # Agent 5: Ranking
from summaries import generate_article_summaries  # Agent 6: Micro Summary
from distributor import use_distributor
import config
from collections import defaultdict

def run_pipeline():
    """Run the complete 6-agent RSS feed processing pipeline"""
    print("\n🤖 ===  6-AGENT AI PIPELINE STARTING ===")
    
    # AGENT 1: Ingestion Agent
    print("\n📡 AGENT 1 - INGESTION: Fetching articles from RSS feeds...")
    fetcher = RSSFetcher()
    articles = fetcher.fetch_articles()
    print(f"✅ Ingested {len(articles)} articles")
    
    if not articles:
        print("❌ No articles fetched. Exiting pipeline.")
        return
    
    # Pre-filter with keywords (not an LLM agent, just efficiency)
    print("\n🔍 PRE-FILTER: Applying keyword filters...")
    keyword_filtered_articles = filter_articles(articles)
    print(f"✅ {len(keyword_filtered_articles)} articles passed keyword filter")
    
    if not keyword_filtered_articles:
        print("❌ No articles passed keyword filtering. Exiting pipeline.")
        return
    
    # AGENT 2: Relevance Agent
    print("\n🎯 AGENT 2 - RELEVANCE: Filtering for AI-relevant articles...")
    relevant_articles = filter_relevant_articles(keyword_filtered_articles)
    
    if not relevant_articles:
        print("❌ No relevant articles found. Exiting pipeline.")
        return
    
    # AGENT 3: Macro Summary Agent (Daily Digest Insight Generator)  
    print("\n📊 AGENT 3 - MACRO SUMMARY: Generating daily digest overview...")
    daily_overview = generate_daily_overview(relevant_articles)
    print(f"✅ Daily Overview: {daily_overview}")
    
    # AGENT 4: Categorization Agent - Categorize ALL relevant articles first
    print("\n🏷️ AGENT 4 - CATEGORIZATION: Categorizing all relevant articles...")
    categorized_articles = categorize_by_topic(relevant_articles)
    
    # Group categorized articles by category
    articles_by_category = defaultdict(list)
    for article in categorized_articles:
        category = article.get('category', 'UNCATEGORIZED')
        articles_by_category[category].append(article)
    
    # AGENT 5: Ranking Agent - Rank PER CATEGORY only if more than 5 articles
    print("\n🏆 AGENT 5 - RANKING: Ranking categories with >5 articles...")
    final_articles_by_category = {}
    total_final_articles = 0
    ranking_calls_saved = 0
    
    for category, cat_articles in articles_by_category.items():
        if len(cat_articles) > 5:
            print(f"📊 Ranking {len(cat_articles)} articles in {category} (>5 articles)...")
            # Rank to get top 5 in this category
            ranked_articles = rank_articles_by_importance(cat_articles, max_articles=5)
            final_articles_by_category[category] = ranked_articles
            total_final_articles += len(ranked_articles)
            print(f"✅ {category}: Selected top {len(ranked_articles)} from {len(cat_articles)} articles")
        else:
            # Keep all articles if 5 or fewer
            final_articles_by_category[category] = cat_articles
            total_final_articles += len(cat_articles)
            ranking_calls_saved += 1
            print(f"✅ {category}: Kept all {len(cat_articles)} articles (≤5, no ranking needed)")
    
    print(f"✅ Ranking complete - saved {ranking_calls_saved} LLM calls by skipping categories with ≤5 articles")
    print(f"✅ Total articles for summarization: {total_final_articles}")
    
    # AGENT 6: Micro Summary Agent - Generate 2-3 sentence summaries
    print("\n✏️ AGENT 6 - MICRO SUMMARY: Generating article summaries...")
    summarized_by_category = {}
    
    for category, cat_articles in final_articles_by_category.items():
        if cat_articles:
            print(f"Summarizing {len(cat_articles)} articles in {category}...")
            summarized_by_category[category] = generate_article_summaries(cat_articles)
    
    # Distribution
    print("\n📧 DISTRIBUTION: Generating digest...")
    # Flatten all articles for count purposes
    all_final_articles = []
    for category_articles in summarized_by_category.values():
        all_final_articles.extend(category_articles)
    
    use_distributor(all_final_articles, summarized_by_category, daily_overview)
    
    print("\n🎉 === 6-AGENT PIPELINE COMPLETE ===")
    print(f"📊 Final Stats:")
    print(f"   • Started with: {len(articles)} articles")
    print(f"   • Keyword filtered: {len(keyword_filtered_articles)} articles")
    print(f"   • Relevant articles: {len(relevant_articles)}")
    print(f"   • Categories found: {len(articles_by_category)}")
    print(f"   • Ranking calls saved: {ranking_calls_saved}")
    print(f"   • Final summarized: {len(all_final_articles)}")

if __name__ == "__main__":
    run_pipeline() 