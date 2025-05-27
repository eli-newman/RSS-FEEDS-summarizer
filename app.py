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
    4. Pre-select top Product Hunt tools
    5. Generate AI summaries only for selected articles
    6. Format and save markdown digest
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
    
    # Step 4: Pre-select top Product Hunt tools to reduce summarization costs
    summarizer = ArticleSummarizer()
    articles_to_summarize = []
    product_hunt_tools = []
    
    # Find Product Hunt tools in AI_TOOLS category
    if "AI_TOOLS" in categorized and categorized["AI_TOOLS"]:
        print("\n--- Pre-selecting Top Product Hunt Tools ---")
        # Extract all Product Hunt tools
        product_hunt_tools = [a for a in categorized["AI_TOOLS"] if "Product Hunt" in a.get('source', '')]
        non_product_hunt = [a for a in categorized["AI_TOOLS"] if "Product Hunt" not in a.get('source', '')]
        
        if product_hunt_tools:
            # Pre-select just the top 3 tools based on title and description
            top_tools = summarizer.preselect_product_hunt_tools(product_hunt_tools, max_tools=3)
            print(f"Pre-selected {len(top_tools)} of {len(product_hunt_tools)} Product Hunt tools")
            
            # Add only the pre-selected tools to the summarization list
            articles_to_summarize.extend(top_tools)
            
            # Add non-Product Hunt tools to summarization list
            articles_to_summarize.extend(non_product_hunt)
            
            # Update the AI_TOOLS category to only include the selected tools
            categorized["AI_TOOLS"] = non_product_hunt + top_tools
        else:
            # No Product Hunt tools, just add all AI_TOOLS
            articles_to_summarize.extend(categorized["AI_TOOLS"])
    else:
        # No AI_TOOLS category, do nothing special
        pass
    
    # Add articles from other categories to summarization list
    for category, category_articles in categorized.items():
        if category != "AI_TOOLS" and category_articles:
            articles_to_summarize.extend(category_articles)
    
    # Step 5: Generate AI summaries (only for selected articles)
    all_summarized = []
    try:
        if config.OPENAI_API_KEY and articles_to_summarize:
            print(f"\n--- Generating AI Summaries for {len(articles_to_summarize)} articles ---")
            all_summarized = summarizer.batch_summarize(articles_to_summarize)
            
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
            print("\n--- Skipping AI Summarization (No API Key or No Articles) ---")
            all_summarized = filtered_articles  # Use filtered articles without summaries
    except Exception as e:
        print(f"\nError during summarization: {str(e)}")
        all_summarized = filtered_articles  # Use filtered articles without summaries
    
    # Step 6: Generate markdown digest
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
    print(f"Summarized {len(all_summarized)} articles")
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