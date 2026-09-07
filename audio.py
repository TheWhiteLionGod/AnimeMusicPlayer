from typing import Self, Callable, Any
import vlc  # type: ignore

class AudioInstance:
    _instance: Self | None = None

    def __new__(cls) -> Self:
        if cls._instance == None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if hasattr(self, "player"): 
            return

        self.vlc_instance = vlc.Instance(["--no-video", "--quiet", "--network-caching=2000"])  # type: ignore

        self.player = self.vlc_instance.media_player_new()  # type: ignore
        self.player.audio_set_volume(70)  # type: ignore

    @property
    def is_playing(self) -> None:
        return self.player.is_playing() ^ (self.player.get_state() == vlc.State.Paused)  # type: ignore

    def play_from_url(self, url: str) -> None:
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

    type Miliseconds = int
    def get_media_duration(self, *, blocking: bool = False) -> Miliseconds:
        while blocking and self.player.get_length() <= 0:  # type: ignore
            pass
        return self.player.get_length()  # type: ignore

    def move_playhead(self, change: Miliseconds) -> None:
        new_time = self.player.get_time() + change  # type: ignore
        new_time = max(min(new_time, self.get_media_duration(blocking=True)), 0)  # type: ignore
        self.player.set_time(new_time)  # type: ignore

    def toggle_pause(self) -> None:
        self.player.pause()  # type: ignore

    def stop_audio(self) -> None:
        self.player.stop()  # type: ignore
