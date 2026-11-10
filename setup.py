"""Install SARAB AI STUDIO Python dependencies.

FFmpeg is an operating-system dependency and must be installed separately.
"""
from pathlib import Path
from setuptools import setup

requirements = [
    line.strip()
    for line in Path(__file__).with_name("requirements.txt").read_text().splitlines()
    if line.strip() and not line.lstrip().startswith("#")
]

setup(
    name="sarab-ai-studio",
    version="7.0.0",
    description="Open-source-first school video creation studio",
    packages=["backend", "backend.api", "backend.ai_engine", "backend.video_engine", "backend.social_uploader", "backend.social_uploader.auth"],
    py_modules=["smart_audio", "generate_thumbnail"],
    install_requires=requirements,
    python_requires=">=3.10",
)
