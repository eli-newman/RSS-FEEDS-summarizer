"""
Main application for the RSS Feed Summarizer
"""
import os
import time
from datetime import datetime
from fetcher import RSSFetcher
import filter
from summarizer import ArticleSummarizer
from distributor import MarkdownDistributor
import config

def run_pipeline():
    """
    Run the full RSS pipeline:
    1. Fetch articles from feeds
    2. Filter by topics of interest
    3. Categorize articles
    4. Generate AI summaries
    5. Format and save markdown digest
    """
    start_time = time.time()
    print(f"=== Starting RSS Feed Pipeline at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")

    # Step 1: Fetch articles
    print("\n--- Fetching Articles ---")
    fetcher = RSSFetcher()
    articles = fetcher.fetch_articles()
    if not articles:
        print("No articles fetched. Exiting pipeline.")
        return
    
    # Step 2: Filter by topics
    print("\n--- Filtering Articles ---")
    filtered_articles = filter.filter_articles(articles)
    if not filtered_articles:
        print("No articles passed filtering. Exiting pipeline.")
        return
        
    # Step 3: Categorize articles
    print("\n--- Categorizing Articles ---")
    categorized = filter.categorize_articles(filtered_articles)
    
    # Step 4: Generate AI summaries
    all_summarized = []
    try:
        if config.OPENAI_API_KEY:
            print("\n--- Generating AI Summaries ---")
            summarizer = ArticleSummarizer()
            
            # Initialize a list to store all articles with summaries
            all_summarized = []
            
            # Process each category
            for category, category_articles in categorized.items():
                if category_articles:
                    print(f"\nProcessing {len(category_articles)} articles in category {category}")
                    # Summarize all articles in each category
                    summarized = summarizer.batch_summarize(category_articles)
                    all_summarized.extend(summarized)
            
            # Print results summary
            print(f"\n--- AI Summarization Complete ---")
            print(f"Generated summaries for {len(all_summarized)} articles")
            
            # Display a few examples
            print("\n=== Example AI Summaries ===")
            for i, article in enumerate(all_summarized[:3]):
                print(f"\n--- Article {i+1} ---")
                print(f"Title: {article['title']}")
                print(f"Category: {article.get('category', 'Uncategorized')}")
                print(f"AI Summary: {article['ai_summary']}")
                
        else:
            print("\n--- Skipping AI Summarization (No API Key) ---")
            all_summarized = filtered_articles  # Use filtered articles without summaries
    except Exception as e:
        print(f"\nError during summarization: {str(e)}")
        all_summarized = filtered_articles  # Use filtered articles without summaries
    
    # Step 5: Generate markdown digest
    try:
        print("\n--- Generating Markdown Digest ---")
        distributor = MarkdownDistributor()
        filepath = distributor.distribute(all_summarized, categorized)
        print(f"Markdown digest saved to: {filepath}")
    except Exception as e:
        print(f"\nError generating markdown digest: {str(e)}")
    
    # Final summary
    elapsed_time = time.time() - start_time
    print(f"\n=== Pipeline Complete ===")
    print(f"Processed {len(articles)} articles in {elapsed_time:.2f} seconds")
    print(f"Filtered down to {len(filtered_articles)} relevant articles")
    for category, category_articles in categorized.items():
        if category_articles:
            print(f"  - {category}: {len(category_articles)} articles")

if __name__ == "__main__":
    if not config.OPENAI_API_KEY:
        print("WARNING: OpenAI API key not set in config.py")
        print("AI summarization will be skipped")
        print("To enable AI summarization, add your API key to config.py")
        print()
    
    run_pipeline() 