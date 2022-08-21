from dataclasses import dataclass


@dataclass
class User:
    id: int
    has_photo: bool
    name: str
    photo: str
