import random

def generate_seo_metadata(topic="School Special"):
    titles = [
        f"🌟 Best Moments & Highlights | {topic} #Shorts",
        f"🔥 Amazing Creativity! {topic} Viral Edit #Reels",
        f"✨ Incredible Vibes: {topic} Experience #Trending"
    ]
    descriptions = (
        f"Watch this special highlight of {topic}!\n\n"
        "🔔 Subscribe & Follow for daily creative reels and updates.\n"
        "⚡ Created with Master MNCR AI Editing Studio.\n\n"
        "#viral #reels #shorts #mncr #trending #foryou #explore"
    )
    hashtags = "#shorts #reels #viral #trending #mncr #explorepage #fyp #creator"
    return {
        "title": random.choice(titles),
        "description": descriptions,
        "hashtags": hashtags
    }
