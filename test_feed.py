import requests

feed_url = "https://www.producthunt.com/feed"
print(f"Testing feed with requests: {feed_url}")

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0'}

try:
    response = requests.get(feed_url, headers=headers, timeout=10)
    print(f"Status code: {response.status_code}")
    print(f"Content type: {response.headers.get('Content-Type')}")
    print(f"Content length: {len(response.text)} characters")
    print("\nFirst 200 characters of content:")
    print(response.text[:200])
except Exception as e:
    print(f"Error: {e}") 