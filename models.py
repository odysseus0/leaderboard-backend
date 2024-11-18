from pydantic import BaseModel

class Tweet(BaseModel):
    full_text: str
    id: str
    views: int
    favorite_count: int
    retweet_count: int
    quote_count: int
    reply_count: int

class Interaction(BaseModel):
    tweet_id: str
    user_id: str
    user_name: str
    text: str
    timestamp: str
    is_quote_status: bool
    favorite_count: int
    retweet_count: int
    quote_count: int
    reply_count: int

class TweetRanking(BaseModel):
    content: str
    tweet_id: str
    engagement_score: float 