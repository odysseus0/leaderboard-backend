import json
import subprocess
from dataclasses import dataclass
from twitter.scraper import Scraper
from models import Tweet, Interaction

@dataclass
class TwitterClient:
    """Simple wrapper around Twitter operations"""
    scraper: Scraper
    
    def __init__(self, ct0: str, auth_token: str):
        self.scraper = Scraper(cookies={
            "ct0": ct0,
            "auth_token": auth_token
        }, save=False)

    def get_tweets(self, user_id: int) -> list[Tweet]:
        response = self.scraper.tweets([user_id])
        return self._parse_tweets(response)
    
    def get_interactions(self, tweet_id: str) -> list[Interaction]:
        details = self.scraper.tweets_details([tweet_id])
        return self._parse_interactions(details)

    def _jq(self, json_data: dict, query: str) -> dict:
        result = subprocess.run(
            ['jq', query], 
            input=json.dumps(json_data), 
            capture_output=True, 
            text=True
        )
        return json.loads(result.stdout)

    def _parse_tweets(self, tweets_response: dict) -> list[Tweet]:
        jq_query = """
        [
            ..
            | objects
            | select(.__typename == "Tweet")
            | {
                full_text: (.legacy.full_text // ""),
                id: .rest_id,
                views: (.views.count // 0),
                favorite_count: (.legacy.favorite_count // 0),
                retweet_count: (.legacy.retweet_count // 0),
                quote_count: (.legacy.quote_count // 0),
                reply_count: (.legacy.reply_count // 0)
            }
        ]
        """
        tweets_data = self._jq(tweets_response, jq_query)
        return [Tweet.model_validate(tweet) for tweet in tweets_data]

    def _parse_interactions(self, tweet_details: dict) -> list[Interaction]:
        jq_query = '''
        .[0]
        | [ ..
            | select(.entryId? | strings | test("conversationthread-.*-tweet-.*"))
            | ..  | select(.__typename? == "Tweet")
            | .legacy as $tweet | .core.user_results.result as $user
            | {
                tweet_id: .rest_id,
                user_id: $user.rest_id,
                user_name: $user.legacy.screen_name,
                text: $tweet.full_text,
                timestamp: $tweet.created_at,
                is_quote_status: $tweet.is_quote_status,
                favorite_count: $tweet.favorite_count,
                retweet_count: $tweet.retweet_count,
                quote_count: $tweet.quote_count,
                reply_count: $tweet.reply_count
            }
        ]
        '''
        interactions_data = self._jq(tweet_details, jq_query)
        return [Interaction.model_validate(i) for i in interactions_data] 