import logging
import os

import httpx
from dotenv import load_dotenv
from fastapi import HTTPException, UploadFile

from storage.minio_client import get_minio_client

load_dotenv()

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT")
MINIO_PATH = os.getenv("MINIO_PATH")
MINIO_ROOT_USER = os.getenv("MINIO_ROOT_USER")
MINIO_ROOT_PASSWORD = os.getenv("MINIO_ROOT_PASSWORD")
BUCKET_NAME = os.getenv("MINIO_DEFAULT_BUCKETS")


class MinioService:
    def __init__(self, minio_client):
        self.minio_client = minio_client

    async def upload_file(self, file: UploadFile) -> str:
        # Чтение данных файла
        content = await file.read()
        if not content:
            logging.error("Uploaded file is empty")
            raise HTTPException(status_code=400, detail="Uploaded file is empty")

        logging.info(f"File size: {len(content)} bytes")

        # Получение названия и расширения файла из его имени
        file_name, file_extension = os.path.splitext(file.filename)

        new_file_name = f"{file_name}{file_extension}"
        media_url = f"{MINIO_PATH}/{BUCKET_NAME}/{new_file_name}"
        logging.info(f"Generated url: {media_url}")
        logging.info(f"Generated file name: {new_file_name}")

        # Установка типа содержимого
        content_type = file.content_type or "image/jpeg"
        logging.info(f"Content type: {content_type}")

        # Загрузка файла в MinIO с использованием presigned URL
        try:
            async with self.minio_client as client:
                # Генерируем pre-signed URL для загрузки
                presigned_url = await client.generate_presigned_url(
                    "put_object",
                    Params={
                        "Bucket": BUCKET_NAME,
                        "Key": new_file_name,
                        "ContentType": content_type,
                    },
                    ExpiresIn=3600,
                )

            # Выполняем запрос PUT к presigned URL
            async with httpx.AsyncClient() as http_client:
                headers = {"Content-Type": content_type}
                response = await http_client.put(
                    presigned_url, headers=headers, content=content
                )
                response.raise_for_status()

            logging.info("File uploaded successfully")
            return media_url
        except Exception as e:
            logging.error(f"MinIO upload error: {str(e)}")
            raise HTTPException(
                status_code=504, detail="Failed to upload file to storage"
            )


if __name__ == "__main__":

    async def test_upload(file: UploadFile):
        async for minio_client in get_minio_client():
            minio_service = MinioService(minio_client)
            return await minio_service.upload_file(file)
