from models.media_models import Meme
from utils.repository import SQLAlchemyRepository


class StorageRepository(SQLAlchemyRepository):
    model = Meme
