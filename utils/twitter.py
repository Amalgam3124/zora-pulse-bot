import os
import tweepy
import datetime
import time

def get_twitter_count(symbol: str) -> int:
    """
    Query the number of tweets containing the symbol in the past week. Supports TWITTER_BEARER_TOKEN or TWITTER_TOKEN (Bearer Token) in environment.
    If the API rate limit wait time exceeds 60 seconds, raises a RuntimeError with a user-friendly message.
    """
    bearer_token = os.getenv("TWITTER_BEARER_TOKEN")
    if not bearer_token:
        bearer_token = os.getenv("TWITTER_TOKEN")
    if not bearer_token:
        raise RuntimeError("Missing TWITTER_BEARER_TOKEN or TWITTER_TOKEN (Bearer Token) in environment.")
    client = tweepy.Client(bearer_token=bearer_token, wait_on_rate_limit=False)
    # Ensure end_time is at least 10 seconds before now, and both times are whole seconds (no microseconds)
    now = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(seconds=10)
    now = now.replace(microsecond=0)
    last_week = now - datetime.timedelta(days=5) + datetime.timedelta(seconds=1)
    last_week = last_week.replace(microsecond=0)
    start_time = last_week.strftime("%Y-%m-%dT%H:%M:%SZ")
    end_time = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    # Remove $ cashtag operator for free API tier compatibility
    query = f"{symbol} -is:retweet lang:en"
    try:
        count = 0
        for resp in tweepy.Paginator(
            client.search_recent_tweets,
            query=query,
            start_time=start_time,
            end_time=end_time,
            max_results=100,
            tweet_fields=["id"]
        ):
            if hasattr(resp, 'data') and resp.data:
                count += len(resp.data)
        return count
    except tweepy.TooManyRequests as e:
        reset_time = int(e.response.headers.get("x-rate-limit-reset", 0))
        now_time = int(time.time())
        wait_seconds = max(reset_time - now_time, 60)
        if wait_seconds > 60:
            raise RuntimeError(f"Twitter API rate limit exceeded. Please try again in {wait_seconds} seconds.")
        else:
            time.sleep(wait_seconds)
            return get_twitter_count(symbol)
    except Exception as e:
        print(f"[Twitter API] Error: {e}")
        return -1 