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
        # Use configured feeds and time window or provided values
        self.feeds = feeds or config.RSS_FEEDS
        self.time_window = time_window_hours or config.TIME_WINDOW
        
        # Set user agent and headers for polite scraping
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0',
            'Accept': 'application/rss+xml, application/atom+xml, application/xml, text/xml'
        }
        
    def fetch_articles(self) -> List[Dict[str, Any]]:
        """
        Fetch articles from all configured RSS feeds within the specified time window
        """
        all_articles = []
        # Calculate cutoff time for article freshness
        cutoff_time = datetime.now() - timedelta(hours=self.time_window)
        
        # Process each feed URL
        for feed_url in self.feeds:
            try:
                # Rate limiting to be polite to servers
                time.sleep(0.5)
                
                # Fetch feed content with proper headers
                response = requests.get(feed_url, headers=self.headers, timeout=15)
                if response.status_code != 200:
                    print(f"Error fetching {feed_url}: HTTP status {response.status_code}")
                    continue
                
                # Parse the feed and extract source name
                feed = feedparser.parse(response.text)
                source_name = feed.feed.title if hasattr(feed.feed, 'title') else feed_url
                
                # Process each article in the feed
                for entry in feed.entries:
                    # Handle various date formats
                    pub_date = None
                    struct = entry.get('published_parsed') or entry.get('updated_parsed')
                    if struct:
                        pub_date = datetime.fromtimestamp(time.mktime(struct))
                    else:
                        raw = entry.get('published') or entry.get('updated')
                        if raw:
                            try:
                                pub_date = parser.parse(raw)
                            except:
                                continue
                        else:
                            continue

                    # Skip older articles outside our time window
                    if pub_date < cutoff_time:
                        continue
                    
                    # Extract and normalize article data
                    article = {
                        'title': entry.title if hasattr(entry, 'title') else 'No Title',
                        'link': entry.link if hasattr(entry, 'link') else '',
                        'published': pub_date,
                        'summary': entry.summary if hasattr(entry, 'summary') else '',
                        'content': entry.content[0].value if hasattr(entry, 'content') and len(entry.content) > 0 else '',
                        'source': source_name
                    }
                    
                    # Use summary as content if no content available
                    if not article['content']:
                        article['content'] = article['summary']
                    
                    all_articles.append(article)
            
            except Exception as e:
                print(f"Error fetching from {feed_url}: {str(e)}")
        
        print(f"Fetched {len(all_articles)} articles")
        return all_articles

if __name__ == "__main__":
    # Test fetcher
    fetcher = RSSFetcher()
    articles = fetcher.fetch_articles()
    print(f"Fetched {len(articles)} articles") 