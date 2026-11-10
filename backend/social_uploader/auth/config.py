"""Read social platform credentials from environment variables only."""
import os

def get_config():
    return {
        'youtube': {
            'client_id': os.getenv('YOUTUBE_CLIENT_ID', ''),
            'client_secret': os.getenv('YOUTUBE_CLIENT_SECRET', ''),
        },
        'meta': {
            'app_id': os.getenv('META_APP_ID', ''),
            'app_secret': os.getenv('META_APP_SECRET', ''),
        },
    }
