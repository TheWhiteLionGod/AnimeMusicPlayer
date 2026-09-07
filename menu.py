from __future__ import annotations
from typing import NoReturn
from tqdm import tqdm

def create_progress_bar(name: str, duration: int) -> tqdm[NoReturn]:
    return tqdm(
        total=duration, 
        unit="s", 
        desc=name,
        bar_format="{desc}: {percentage:3.0f}%|{bar}| {unit}"
    )
