import logging
import requests
from functools import lru_cache
from models import Tweet, Interaction
from settings import Settings

settings = Settings()

@lru_cache(maxsize=1000)
def get_follower_score(username: str) -> int:
    try:
        response = requests.get(
            f"https://api.discover.getmoni.io/api/v1/twitters/{username}/info/",
            headers={"Api-Key": settings.moni_api_key},
            timeout=5
        )
        return int(response.json().get("followersScore", 1))
    except Exception as e:
        logging.warning(f"Failed to get follower score for {username}: {e}")
        return 1

def calculate_engagement_score(main_tweet: Tweet, interactions: list[Interaction]) -> float:
    return (
        main_tweet.views * settings.views_weight +
        main_tweet.favorite_count +
        main_tweet.retweet_count * settings.retweet_multiplier +
        sum((i.quote_count if i.is_quote_status else i.reply_count) 
            * get_follower_score(i.user_name) 
            * (settings.quote_weight if i.is_quote_status else settings.reply_weight)
            for i in interactions)
    ) 