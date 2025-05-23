"""
Feed tester for RSS Feeds
"""
import requests
import config
import xml.etree.ElementTree as ET
import time

def test_feeds():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0',
        'Accept': 'application/rss+xml, application/atom+xml, application/xml, text/xml'
    }
    
    print("\n=== RSS Feed Testing Results ===\n")
    
    for feed_url in config.RSS_FEEDS:
        print(f"Testing: {feed_url}")
        try:
            # Add a small delay to avoid stressing servers
            time.sleep(0.5)
            
            response = requests.get(feed_url, headers=headers, timeout=15)
            print(f"  Status code: {response.status_code}")
            print(f"  Content type: {response.headers.get('Content-Type')}")
            
            if response.status_code == 200:
                content_length = len(response.text)
                print(f"  Content length: {content_length} characters")
                
                if content_length > 0:
                    print("  Content preview:")
                    print(f"    {response.text[:100].strip().replace('\n', ' ')}...")
                    
                    # Try to parse as XML
                    try:
                        # For Atom feeds
                        if '<feed' in response.text:
                            print("  Appears to be Atom feed format")
                            # Count entries
                            entries = response.text.count('<entry')
                            print(f"  Estimated entries: {entries}")
                        # For RSS feeds
                        elif '<rss' in response.text or '<channel' in response.text:
                            print("  Appears to be RSS feed format")
                            # Count items
                            items = response.text.count('<item')
                            print(f"  Estimated items: {items}")
                        else:
                            print("  Unknown feed format")
                    except Exception as e:
                        print(f"  XML parsing error: {str(e)}")
                else:
                    print("  Empty content")
            else:
                print(f"  Error: Received status code {response.status_code}")
                
        except Exception as e:
            print(f"  Connection error: {str(e)}")
        
        print()  # Empty line between feeds
    
    print("=== Testing complete ===")

if __name__ == "__main__":
    test_feeds() 