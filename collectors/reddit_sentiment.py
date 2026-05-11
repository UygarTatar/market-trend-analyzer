import feedparser
import pandas as pd
from datetime import datetime
import time

def scrape_reddit_rss(subreddit: str, limit: int = 25) -> pd.DataFrame:
    """
    Scrapes the latest posts from a subreddit using its public RSS feed.
    No API key required.
    """
    url = f"https://www.reddit.com/r/{subreddit}/.rss"
    print(f"[Reddit RSS] Fetching r/{subreddit}...")
    
    # User-agent is required even for RSS to avoid 429 errors
    feed = feedparser.parse(url, agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) ONYX/1.0")
    
    posts = []
    for entry in feed.entries[:limit]:
        posts.append({
            'title': entry.title,
            'subreddit': subreddit,
            'author': entry.author if 'author' in entry else 'unknown',
            'link': entry.link,
            'published': entry.published if 'published' in entry else datetime.now().isoformat(),
            'fetched_at': datetime.now().isoformat()
        })
    
    return pd.DataFrame(posts)

def collect_gaming_sentiment():
    """
    Aggregates sentiment from major gaming subreddits.
    """
    subreddits = ['pcgaming', 'androidgaming', 'iosgaming', 'Games']
    all_posts = []
    
    for sub in subreddits:
        try:
            df = scrape_reddit_rss(sub)
            all_posts.append(df)
            # Be polite to Reddit
            time.sleep(1)
        except Exception as e:
            print(f"[Error] Failed to fetch r/{sub}: {e}")
            
    if not all_posts:
        return pd.DataFrame()
        
    return pd.concat(all_posts, ignore_index=True)

if __name__ == "__main__":
    print("--- Testing Reddit RSS Scraper ---")
    results = collect_gaming_sentiment()
    print(f"Total posts collected: {len(results)}")
    if not results.empty:
        print("\nTop 5 posts:")
        print(results[['title', 'subreddit']].head())
