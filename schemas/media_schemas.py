from typing import Optional

from pydantic import BaseModel


class MediaCreate(BaseModel):
    meme_data: str
    meme_description: str


class MediaRead(BaseModel):
    id: int
    meme_url: str
    meme_description: str

    class ConfigDict:
        from_attributes = True


class MediaUpdate(BaseModel):
    meme_description: Optional[str] = None

    class ConfigDict:
        from_attributes = True
