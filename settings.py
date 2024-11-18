from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    # Paths
    leaderboard_path: Path = Path("docs/leaderboard.json")
    
    # Twitter/X
    overheard_x_user_id: int = 1853810993891041280
    CT0: str  # Will match X_CT0
    AUTH_TOKEN: str  # Will match X_AUTH_TOKEN
    
    # API Keys
    moni_api_key: str = Field(validation_alias="MONI_API_KEY")
    
    # Scoring weights
    views_weight: float = 0.01
    retweet_multiplier: float = 2.0
    quote_weight: float = 0.03
    reply_weight: float = 0.05

    model_config = {
        "env_prefix": "X_"
    } 