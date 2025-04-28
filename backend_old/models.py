from pydantic import BaseModel
from typing import List
from prompts import build_prompt

class TripRequest(BaseModel):
    destination: str
    mbti: str
    interests: List[str]
    dislikes: List[str]

    def to_prompt(self) -> str:
        return build_prompt(
            self.destination,
            self.mbti,
            self.interests,
            self.dislikes
        )
