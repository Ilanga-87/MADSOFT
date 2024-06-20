import os

from aiobotocore.session import get_session
from dotenv import load_dotenv

load_dotenv()

MINIO_HOST = os.getenv("MINIO_HOST")
MINIO_PORT = os.getenv("MINIO_PORT")
MINIO_ENDPOINT = f"{MINIO_HOST}:{MINIO_PORT}"
MINIO_ROOT_USER = os.getenv("MINIO_ROOT_USER")
MINIO_ROOT_PASSWORD = os.getenv("MINIO_ROOT_PASSWORD")
BUCKET_NAME = os.getenv("MINIO_DEFAULT_BUCKETS")

session = get_session()


async def get_minio_client():
    async with session.create_client(
        "s3",
        endpoint_url=MINIO_ENDPOINT,
        aws_access_key_id=MINIO_ROOT_USER,
        aws_secret_access_key=MINIO_ROOT_PASSWORD,
    ) as client:
        yield client
