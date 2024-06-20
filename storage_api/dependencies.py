from aiobotocore.session import get_session
from fastapi import Depends

from repositories.storage_repository import StorageRepository
from services.minio_service import (
    MinioService,
    MINIO_ENDPOINT,
    MINIO_ROOT_USER,
    MINIO_ROOT_PASSWORD,
)
from services.storage_service import StorageService


async def get_minio_client():
    session = get_session()
    async with session.create_client(
        "s3",
        endpoint_url=MINIO_ENDPOINT,
        aws_access_key_id=MINIO_ROOT_USER,
        aws_secret_access_key=MINIO_ROOT_PASSWORD,
    ) as client:
        yield client


def get_storage_repository() -> StorageRepository:
    return StorageRepository()


def storage_service(
    storage_repo=Depends(get_storage_repository),
    minio_client=Depends(get_minio_client),
):
    minio_service = MinioService(minio_client)
    return StorageService(storage_repo, minio_service)
