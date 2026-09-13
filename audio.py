from typing import Self, Callable, Any
import time
import vlc  # type: ignore

class AudioInstance:
    _instance: Self | None = None

    def __new__(cls) -> Self:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if hasattr(self, "player"): 
            return

        self.vlc_instance = vlc.Instance(["--no-video", "--quiet", "--network-caching=2000"])  # type: ignore

        self.player = self.vlc_instance.media_player_new()  # type: ignore
        self.player.audio_set_volume(70)  # type: ignore

    @property
    def is_playing(self) -> bool:
        state = self.player.get_state()  # type: ignore
        return state in (vlc.State.Playing, vlc.State.Buffering, vlc.State.Opening, vlc.State.Paused)  # type: ignore

    def wait_until_playing(self, timeout: float = 10.0) -> bool:
        start_time = time.time()
        while time.time() - start_time < timeout:
            state = self.player.get_state()  # type: ignore
            if state in (vlc.State.Playing, vlc.State.Paused):  # type: ignore
                return True
            if state in (vlc.State.Ended, vlc.State.Stopped, vlc.State.Error):  # type: ignore
                return False
            time.sleep(0.05)
        return False

    def play_from_url(self, url: str) -> None:
        self.stop_audio()

        media = self.vlc_instance.media_new(url)  # type: ignore
        self.player.set_media(media)  # type: ignore
        self.player.play()  # type: ignore

    def attach_callback_to_event(
            self, 
            event_type: vlc.EventType,  # type: ignore
            func: Callable[..., Any], 
            *args: tuple[Any, ...]
        ) -> None:
        self.player.event_manager().event_attach(event_type, func, *args)  # type: ignore

    def detach_callback_from_event(
            self, 
            event_type: vlc.EventType  # type: ignore
        ) -> None:
        self.player.event_manager().event_detach(event_type)  # type: ignore

    type Miliseconds = int
    def get_media_duration(self, *, blocking: bool = False, timeout: float = 10.0) -> Miliseconds:
        if not blocking:
            return max(self.player.get_length(), 0)  # type: ignore

        if not self.wait_until_playing(timeout=timeout / 2):
            return 0

        start_time = time.time()
        while self.player.get_length() <= 0 and time.time() - start_time < timeout / 2:  # type: ignore
            time.sleep(0.05)

        return max(self.player.get_length(), 0)  # type: ignore

    def move_playhead(self, change: Miliseconds) -> None:
        new_time = self.player.get_time() + change  # type: ignore
        self.set_playhead(new_time)  # type: ignore

    def set_playhead(self, timestamp: Miliseconds) -> None:
        duration = self.get_media_duration(blocking=False)
        if duration <= 0:
            return

        timestamp = max(min(timestamp, duration), 0)
        self.player.set_time(timestamp)  # type: ignore

    def toggle_pause(self) -> None:
        self.player.pause()  # type: ignore

    def stop_audio(self) -> None:
        self.player.stop()  # type: ignore
