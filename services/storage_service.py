from fastapi import UploadFile, HTTPException

from schemas.media_schemas import MediaRead
from utils.repository import AbstractRepository
from .minio_service import MinioService


class StorageService:
    def __init__(self, storage_repo: AbstractRepository, minio_service: MinioService):
        self.storage_repo: AbstractRepository = storage_repo()
        self.minio_service = minio_service

    async def add_single_media(
        self, media_data: UploadFile, media_description: str
    ) -> MediaRead:
        media_url = await self.minio_service.upload_file(media_data)
        media = await self.storage_repo.add_one(
            {"meme_url": media_url, "meme_description": media_description}
        )
        return MediaRead(
            id=media.id, meme_url=media.meme_url, meme_description=media.meme_description
        )

    async def get_all_media(self, skip: int = 0, limit: int = 10):
        all_media = await self.storage_repo.get_all(skip=skip, limit=limit)
        return all_media

    async def get_single_media(self, id: int):
        media = await self.storage_repo.get_one_by_id(id)
        if not media:
            raise HTTPException(status_code=404, detail="Object not found.")
        return media

    async def update_single_media(self, id: int, data: dict):
        media = await self.storage_repo.update_one(id, **data)
        if not media:
            raise HTTPException(status_code=404, detail="Object not found.")
        return media

    async def delete_single_media(self, id):
        media = await self.storage_repo.delete_one(id)
        return media
