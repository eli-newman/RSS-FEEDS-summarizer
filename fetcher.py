"""
Article fetcher for RSS feeds
"""
import feedparser
from datetime import datetime, timedelta
import time
from typing import List, Dict, Any
import config
from dateutil import parser
import requests

class RSSFetcher:
    def __init__(self, feeds: List[str] = None, time_window_hours: int = None):
        self.feeds = feeds or config.RSS_FEEDS
        self.time_window = time_window_hours or config.TIME_WINDOW
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0',
            'Accept': 'application/rss+xml, application/atom+xml, application/xml, text/xml'
        }
        
    def fetch_articles(self) -> List[Dict[str, Any]]:
        """
        Fetch articles from all configured RSS feeds within the specified time window
        """
        all_articles = []
        cutoff_time = datetime.now() - timedelta(hours=self.time_window)
        
        for feed_url in self.feeds:
            try:
                # Add a small delay to avoid stressing servers
                time.sleep(0.5)
                
                # First download the feed content with requests to ensure proper headers
                response = requests.get(feed_url, headers=self.headers, timeout=15)
                if response.status_code != 200:
                    print(f"Error fetching {feed_url}: HTTP status {response.status_code}")
                    continue
                
                # Parse the feed content with feedparser
                feed = feedparser.parse(response.text)
                print(f"[DEBUG] Parsing {feed_url} — {len(feed.entries)} entries")
                
                # If no entries were found, try direct parsing
                if len(feed.entries) == 0:
                    print(f"[DEBUG] Retrying {feed_url} with direct feedparser.parse(url)")
                    feed = feedparser.parse(feed_url)
                    print(f"[DEBUG] After retry: {len(feed.entries)} entries")
                
                source_name = feed.feed.title if hasattr(feed.feed, 'title') else feed_url
                
                for entry in feed.entries:
                    # Try structured parse first
                    struct = entry.get('published_parsed') or entry.get('updated_parsed')
                    if struct:
                        pub_date = datetime.fromtimestamp(time.mktime(struct))
                    else:
                        # Fall back to parsing the raw string
                        raw = entry.get('published') or entry.get('updated')
                        print(f"[DEBUG]   Raw date for \"{entry.get('title', '–no title–')}\": {raw}")
                        if not raw:
                            continue
                        try:
                            pub_date = parser.parse(raw)
                        except:
                            continue

                    print(f"[DEBUG]   → {entry.get('title', '–no title–')} @ {pub_date.isoformat()}")
                    
                    # Skip if article is older than our time window
                    if pub_date < cutoff_time:
                        print(f"[DEBUG]     Skipping: older than cutoff ({cutoff_time.isoformat()})")
                        continue
                    
                    # Extract article data
                    article = {
                        'title': entry.title if hasattr(entry, 'title') else 'No Title',
                        'link': entry.link if hasattr(entry, 'link') else '',
                        'published': pub_date,
                        'summary': entry.summary if hasattr(entry, 'summary') else '',
                        'content': entry.content[0].value if hasattr(entry, 'content') and len(entry.content) > 0 else '',
                        'source': source_name
                    }
                    
                    # If no content available, use summary as content
                    if not article['content']:
                        article['content'] = article['summary']
                    
                    all_articles.append(article)
            
            except Exception as e:
                print(f"Error fetching from {feed_url}: {str(e)}")
        
        return all_articles

if __name__ == "__main__":
    # Simple test
    fetcher = RSSFetcher(time_window_hours=168)  # Temporarily set to 7 days for debugging
    articles = fetcher.fetch_articles()
    print(f"Fetched {len(articles)} articles")
    for i, article in enumerate(articles[:3]):  # Print first 3 for testing
        print(f"\n--- Article {i+1} ---")
        print(f"Title: {article['title']}")
        print(f"Source: {article['source']}")
        print(f"Published: {article['published']}")
        print(f"Link: {article['link']}")
        print(f"Summary: {article['summary'][:100]}...") 