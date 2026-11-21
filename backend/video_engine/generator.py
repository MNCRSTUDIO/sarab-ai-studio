"""Compatibility wrapper around the shared slideshow engine."""
from pathlib import Path
from backend.ai_engine.planner import AIPlanner
from .editor import VideoEditorEngine, _safe_name
def start_render(output_name="SARAB_AI_VIDEO.mp4",duration=30,aspect="vertical",music_name=""):
    root=Path(__file__).resolve().parents[2]; media=root/"media"
    scenes=[str(p) for p in list((media/"input").glob("*"))+list((media/"photos").glob("*")) if p.suffix.lower() in (".jpg",".jpeg",".png",".webp")]
    if not scenes: raise RuntimeError("Add photos to media/input")
    audio=media/"temp"/"compat.m4a"; audio.parent.mkdir(parents=True,exist_ok=True)
    audiofile=AIPlanner(str(root)).resolve_audio(music_name,duration,str(audio))
    fmt="9:16" if str(aspect).lower() in ("vertical","9:16") else "16:9"
    output=media/"output"/_safe_name(output_name); output.parent.mkdir(parents=True,exist_ok=True)
    return VideoEditorEngine(str(root)).compile(scenes,duration,fmt,audiofile,str(output),"compat")
def generate_video(output_name="SARAB_AI_VIDEO.mp4",duration=30,aspect="vertical",music_name=""):
    return start_render(output_name,duration,aspect,music_name)
