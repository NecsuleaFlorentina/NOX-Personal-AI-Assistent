import yt_dlp
import vlc
import threading
import time
import json
import os
import re

PLAYLIST_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "playlist.json")
DOWNLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "music")
FFMPEG_PATH = r"C:\ffmpeg\bin"


def load_playlist():
    if os.path.exists(PLAYLIST_FILE):
        with open(PLAYLIST_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_playlist(playlist):
    os.makedirs(os.path.dirname(PLAYLIST_FILE), exist_ok=True)
    with open(PLAYLIST_FILE, "w", encoding="utf-8") as f:
        json.dump(playlist, f, ensure_ascii=False, indent=2)


def is_valid_youtube_url(url):
    pattern = r"(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+"
    return re.match(pattern, url) is not None


def get_video_info(url):
    ydl_opts = {
        "format": "bestaudio/best",
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        title = info.get("title", "Melodie necunoscuta")
        stream_url = info["url"]
        duration = info.get("duration", 0)
        thumbnail = info.get("thumbnail", "")
        return title, stream_url, duration, thumbnail


def download_song(url, title, progress_callback=None, done_callback=None, error_callback=None):
    """
    Descarca melodia ca MP3 in data/music/.
    progress_callback(percent: float)
    done_callback(filepath: str)
    error_callback(err: str)
    """
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    # Nume fisier sigur
    safe_title = re.sub(r'[\\/*?:"<>|]', "_", title)
    out_template = os.path.join(DOWNLOAD_DIR, f"{safe_title}.%(ext)s")

    def _hook(d):
        if d["status"] == "downloading" and progress_callback:
            total = d.get("total_bytes") or d.get("total_bytes_estimate", 0)
            downloaded = d.get("downloaded_bytes", 0)
            if total > 0:
                progress_callback(downloaded / total * 100)
        elif d["status"] == "finished":
            if progress_callback:
                progress_callback(100)

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": out_template,
        "quiet": True,
        "no_warnings": True,
        "progress_hooks": [_hook],
        "ffmpeg_location": FFMPEG_PATH,
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
    }

    def _task():
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            filepath = os.path.join(DOWNLOAD_DIR, f"{safe_title}.mp3")
            if done_callback:
                done_callback(filepath)
        except Exception as e:
            if error_callback:
                error_callback(str(e))

    threading.Thread(target=_task, daemon=True).start()


def get_local_path(title):
    """Returneaza calea MP3 locala daca exista, altfel None."""
    safe_title = re.sub(r'[\\/*?:"<>|]', "_", title)
    path = os.path.join(DOWNLOAD_DIR, f"{safe_title}.mp3")
    return path if os.path.exists(path) else None


class MusicPlayer:
    def __init__(self):
        self.instance = vlc.Instance("--no-xlib")
        self.player = self.instance.media_player_new()
        self.playlist = load_playlist()
        self.current_index = -1
        self.is_playing = False
        self.duration = 0
        self._progress_callback = None
        self._status_callback = None
        self._title_callback = None
        self._monitor_thread = None
        self._stop_monitor = False

    def set_progress_callback(self, cb):
        self._progress_callback = cb

    def set_status_callback(self, cb):
        self._status_callback = cb

    def set_title_callback(self, cb):
        self._title_callback = cb

    def add_to_playlist(self, url):
        if not is_valid_youtube_url(url):
            raise ValueError("URL invalid. Introdu un link YouTube valid.")
        title, stream_url, duration, thumbnail = get_video_info(url)
        entry = {"title": title, "url": url}
        self.playlist.append(entry)
        save_playlist(self.playlist)
        return title

    def remove_from_playlist(self, index):
        if 0 <= index < len(self.playlist):
            self.playlist.pop(index)
            save_playlist(self.playlist)
            if self.current_index >= len(self.playlist):
                self.current_index = len(self.playlist) - 1

    def get_playlist(self):
        return [entry["title"] for entry in self.playlist]

    def _load_and_play(self, index):
        if not (0 <= index < len(self.playlist)):
            return
        self.current_index = index
        entry = self.playlist[index]
        if self._status_callback:
            self._status_callback("Se incarca...")
        if self._title_callback:
            self._title_callback(entry["title"])

        def _task():
            try:
                # Verifica daca exista fisier local
                local_path = get_local_path(entry["title"])
                if local_path:
                    stream_url = local_path
                    duration = 0  # VLC va detecta durata
                else:
                    title, stream_url, duration, thumbnail = get_video_info(entry["url"])
                    self.duration = duration

                media = self.instance.media_new(stream_url)
                self.player.set_media(media)
                self.player.play()
                self.is_playing = True
                if self._status_callback:
                    local_icon = "💾 " if local_path else ""
                    self._status_callback(f"{local_icon}Se reda")
                self._start_monitor()
            except Exception as e:
                if self._status_callback:
                    self._status_callback(f"Eroare: {e}")

        threading.Thread(target=_task, daemon=True).start()

    def play(self, index=None):
        if index is not None:
            self._load_and_play(index)
        elif self.current_index == -1 and self.playlist:
            self._load_and_play(0)
        else:
            self.player.play()
            self.is_playing = True
            if self._status_callback:
                self._status_callback("Se reda")

    def pause(self):
        self.player.pause()
        self.is_playing = not self.is_playing
        if self._status_callback:
            self._status_callback("Se reda" if self.is_playing else "Pauza")

    def stop(self):
        self._stop_monitor = True
        self.player.stop()
        self.is_playing = False
        if self._status_callback:
            self._status_callback("Oprit")
        if self._progress_callback:
            self._progress_callback(0)

    def next_track(self):
        if self.playlist:
            next_idx = (self.current_index + 1) % len(self.playlist)
            self._load_and_play(next_idx)

    def prev_track(self):
        if self.playlist:
            prev_idx = (self.current_index - 1) % len(self.playlist)
            self._load_and_play(prev_idx)

    def set_volume(self, value):
        self.player.audio_set_volume(int(value))

    def seek(self, percent):
        self.player.set_position(percent)

    def get_position(self):
        return self.player.get_position()

    def get_time(self):
        elapsed = self.player.get_time() // 1000
        return elapsed, self.duration

    def _start_monitor(self):
        self._stop_monitor = False
        if self._monitor_thread and self._monitor_thread.is_alive():
            return
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()

    def _monitor_loop(self):
        while not self._stop_monitor:
            time.sleep(0.5)
            if not self.is_playing:
                continue
            pos = self.get_position()
            if self._progress_callback:
                self._progress_callback(pos)
            state = self.player.get_state()
            if state == vlc.State.Ended:
                self.next_track()
                break