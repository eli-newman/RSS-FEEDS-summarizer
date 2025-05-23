"""
Main orchestration script for RSS Feed Summarizer
"""
import os
import sys
from dotenv import load_dotenv
import schedule
import time
from typing import List, Dict, Any

# Load environment variables
load_dotenv()

# Make sure OpenAI API key is set
if not os.environ.get("OPENAI_API_KEY"):
    print("Error: OPENAI_API_KEY environment variable not set")
    print("Please create a .env file based on .env.example and add your API key")
    sys.exit(1)

# Import project modules
from fetcher import RSSFetcher
from filter import ArticleFilter
from categorizer import ArticleCategorizer
from summarizer import ArticleSummarizer
from distributor import ContentDistributor

def process_feeds():
    """
    Main function to process RSS feeds
    """
    print("Starting RSS feed processing...")
    
    # Step 1: Fetch articles
    fetcher = RSSFetcher()
    articles = fetcher.fetch_articles()
    print(f"Fetched {len(articles)} articles")
    
    if not articles:
        print("No articles found. Exiting.")
        return
    
    # Step 2: Filter for relevance
    article_filter = ArticleFilter()
    relevant_articles = article_filter.filter_articles(articles)
    print(f"Found {len(relevant_articles)} relevant articles")
    
    if not relevant_articles:
        print("No relevant articles found. Exiting.")
        return
    
    # Step 3: Categorize articles
    categorizer = ArticleCategorizer()
    categorized_articles = categorizer.categorize_articles(relevant_articles)
    
    # Step 4: Summarize articles
    summarizer = ArticleSummarizer()
    summarized_articles = summarizer.summarize_articles(categorized_articles)
    
    # Step 5: Distribute content
    distributor = ContentDistributor()
    distributor.distribute_articles(summarized_articles)
    
    print("RSS feed processing completed!")

def run_scheduler():
    """
    Set up scheduled runs
    """
    # Schedule daily run at 8:00 AM
    schedule.every().day.at("08:00").do(process_feeds)
    
    print("Scheduler started. Will process feeds daily at 8:00 AM.")
    print("Press Ctrl+C to exit.")
    
    # Keep the script running
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    # Check if we should run immediately or schedule
    if len(sys.argv) > 1 and sys.argv[1] == "--now":
        process_feeds()
    else:
        run_scheduler() 