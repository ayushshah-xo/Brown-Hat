"""
voice/song_player.py — Song Player with Jaw Animation
Plays MP3 songs while moving the jaw to the beat.
"""
import os
import time
import logging
import threading
import subprocess
import tempfile
from pathlib import Path
from typing import Optional

logger = logging.getLogger("Robot.SongPlayer")

SONGS_DIR = Path(__file__).parent.parent / "songs"

SONG_MAP = {
    # Wake words that trigger songs
    "school song":   "school_song.mp3",
    "sukuna song":   "school_song.mp3",
    "school anthem": "school_song.mp3",
    "nepali song":   "nepali_song.mp3",
    "sing":          "school_song.mp3",
    "गीत":           "nepali_song.mp3",
    "नेपाली गीत":    "nepali_song.mp3",
    "स्कुल गीत":     "school_song.mp3",
    "school song":   "school_song.mp3",
    "sukuna song":   "school_song.mp3",
    "school anthem": "school_song.mp3",
    "nepali song":   "nepali_song.mp3",
    "sing":          "school_song.mp3",
    "sin ":          "school_song.mp3",
    "son":           "nepali_song.mp3",
    "गीत":           "nepali_song.mp3",
    "नेपाली गीत":    "nepali_song.mp3",
    "स्कुल गीत":     "school_song.mp3",
}

def wants_song(query: str) -> Optional[str]:
    """Check if query is asking for a song. Returns filename or None."""
    q = query.lower()
    for keyword, filename in SONG_MAP.items():
        if keyword in q:
            return str(SONGS_DIR / filename)
    return None

def play_song(song_path: str, jaw=None, tts=None, lang: str = "en"):
    """
    Play an MP3 song with jaw animation.
    jaw: jaw servo object with animate_from_audio method
    tts: TTS object for intro/outro
    """
    if not os.path.exists(song_path):
        logger.error(f"Song not found: {song_path}")
        if tts:
            tts.speak("Sorry, I could not find that song.", lang=lang)
        return

    song_name = Path(song_path).stem.replace("_", " ").title()
    logger.info(f"Playing song: {song_name}")

    # Announce the song
    if tts:
        if "school" in song_path.lower():
            tts.speak(
                "Here is the Sukuna Secondary School anthem!",
                lang="en", jaw=jaw
            )
        else:
            tts.speak(
                "Here is a Nepali song for you!",
                lang="en", jaw=jaw
            )
        time.sleep(0.3)

    # Convert MP3 to WAV for jaw animation
    wav_path = tempfile.mktemp(suffix=".wav")
    try:
        result = subprocess.run(
            ["sox", song_path, "-r", "44100", "-c", "1", wav_path],
            capture_output=True, timeout=30
        )
        if result.returncode != 0:
            # Try ffmpeg as fallback
            subprocess.run(
                ["ffmpeg", "-i", song_path, "-ar", "44100",
                 "-ac", "1", wav_path, "-y"],
                capture_output=True, timeout=30
            )
    except Exception as e:
        logger.warning(f"Audio conversion failed: {e} — playing directly")
        wav_path = None

    play_path = wav_path if wav_path and os.path.exists(wav_path) else song_path

    # Start jaw animation in parallel with playback
    if jaw and wav_path and os.path.exists(wav_path):
        jaw_thread = threading.Thread(
            target=jaw.animate_from_audio,
            args=(wav_path,),
            daemon=True
        )
        jaw_thread.start()

    # Play the song
    try:
        import pygame
        os.environ.setdefault('SDL_AUDIODRIVER', 'alsa')
        if not pygame.mixer.get_init():
            pygame.mixer.init(frequency=44100, size=-16,
                              channels=2, buffer=4096)
        pygame.mixer.music.load(play_path)
        pygame.mixer.music.set_volume(1.0)
        pygame.mixer.music.play()
        logger.info("Song playing...")
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
        logger.info("Song finished")
    except Exception as e:
        logger.error(f"Playback error: {e}")
        try:
            subprocess.run(
                ["aplay", "-D", "plughw:0,0", play_path],
                timeout=300
            )
        except Exception as e2:
            logger.error(f"aplay failed: {e2}")
    finally:
        try:
            if wav_path and os.path.exists(wav_path):
                os.unlink(wav_path)
        except Exception:
            pass

    # Outro
    if tts:
        time.sleep(0.3)
        tts.speak("I hope you enjoyed that!", lang="en", jaw=jaw)
