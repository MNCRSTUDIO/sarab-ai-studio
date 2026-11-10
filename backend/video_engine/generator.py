"""Compatibility wrapper that delegates to the single shared slideshow renderer."""
from .editor import start_render

def generate_video(output_name='SARAB_AI_VIDEO.mp4', duration=30, aspect='vertical', music_name=''):
    return start_render(output_name=output_name, duration=duration, aspect=aspect, music_name=music_name)
