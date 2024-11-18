import json
import logging
from client import TwitterClient
from models import TweetRanking
from settings import Settings
from scoring import calculate_engagement_score

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def update_leaderboard(settings: Settings) -> None:
    """Updates the leaderboard with latest tweet rankings"""
    client = TwitterClient(settings.CT0, settings.AUTH_TOKEN)
    
    # Fetch tweets
    tweets = client.get_tweets(settings.overheard_x_user_id)
    logging.info(f"Fetched {len(tweets)} tweets")
    
    # Process tweets and calculate scores
    rankings = []
    for i, tweet in enumerate(tweets, 1):
        logging.info(f"Processing tweet {i}/{len(tweets)}")
        try:
            interactions = client.get_interactions(tweet.id)
            score = calculate_engagement_score(tweet, interactions)
            rankings.append(
                TweetRanking(
                    content=tweet.full_text,
                    tweet_id=tweet.id,
                    engagement_score=round(score, 2)
                )
            )
        except Exception as e:
            logging.error(f"Failed to process tweet {tweet.id}: {e}")
            continue
    
    # Sort and save
    rankings.sort(key=lambda x: x.engagement_score, reverse=True)
    save_rankings(rankings, settings.leaderboard_path)
    logging.info(f"Leaderboard updated with {len(rankings)} tweets")

def save_rankings(rankings: list[TweetRanking], path) -> None:
    """Saves rankings to the specified file path"""
    path.parent.mkdir(exist_ok=True)
    with path.open('w', encoding='utf-8') as f:
        json.dump([r.model_dump() for r in rankings], f, indent=2, ensure_ascii=False)

def main():
    logging.info("Starting leaderboard update")
    settings = Settings()
    logging.info(f"Settings: {settings.model_dump_json(indent=2)}")
    
    try:
        update_leaderboard(settings)
    except Exception as e:
        logging.error(f"Failed to update leaderboard: {e}")
        raise

if __name__ == "__main__":
    main()

