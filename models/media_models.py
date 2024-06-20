from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

from schemas.media_schemas import MediaRead

Base = declarative_base()


class Meme(Base):
    __tablename__ = "memes"
    id = Column(Integer, primary_key=True)
    meme_url = Column(String, nullable=False, unique=True)
    meme_description = Column(String, nullable=False, unique=True)

    def to_read_model(self):
        return MediaRead(
            id=self.id, meme_url=self.meme_url, meme_description=self.meme_description
        )
