import io

import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.exc import OperationalError

from ..config import configs
from ..database.db import Database
from ..storage_api.storage_app import storage_app as app

pytestmark = pytest.mark.asyncio


async def test_database_connection():
    database = Database(configs.DATABASE_URI)

    try:
        async with database._engine.connect():
            assert True
    except OperationalError:
        assert False


async def test_root():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get("/")
    assert response.status_code == 200
    assert response.json() == "service is working"


async def test_get_all():
    expected_response = [
        {
            "id": 1,
            "meme_url": "http://minio:9000/media-storage/images.jpg",
            "meme_description": "Котомем_1",
        },
        {
            "id": 2,
            "meme_url": "http://minio:9000/media-storage/images2.jpg",
            "meme_description": "Котомем_2",
        },
        {
            "id": 3,
            "meme_url": "http://minio:9000/media-storage/cat-guys-have-bad-news-theronswag-woke-up-again.png",
            "meme_description": "Котомем_3",
        },
    ]
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get("/media")
    json_response = response.json()
    len_response = len(json_response)
    assert response.status_code == 200
    assert len_response == 3
    assert response.json() == expected_response


async def test_get_single_media_standard():
    single_media = {
        "id": 1,
        "meme_url": "http://minio:9000/media-storage/images.jpg",
        "meme_description": "Котомем_1",
    }
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get("/media/1")
    assert response.status_code == 200
    assert response.json() == single_media


async def test_get_single_media_non_existing_id():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get("/media/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Object not found."}


async def test_add_single_media_standard():
    media_data = b"test file content"
    media_description = "Test Media Description"
    file_name = "testfile.txt"
    expected_response = {
        "meme_url": f"http://minio:9000/media-storage/{file_name}",
        "meme_description": f"{media_description}",
    }

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(
            "/media",
            files={"media_data": (file_name, io.BytesIO(media_data), "images/jpeg")},
            data={"media_description": media_description},
        )
    assert response.status_code == 200

    response_json = response.json()
    assert response_json["meme_url"] == expected_response["meme_url"]
    assert response_json["meme_description"] == expected_response["meme_description"]


async def test_add_single_media_duplicate_file():
    media_data = b"test file content"
    media_description = "Test Media Description 2"
    file_name = "testfile.txt"

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(
            "/media",
            files={"media_data": (file_name, io.BytesIO(media_data), "images/jpeg")},
            data={"media_description": media_description},
        )
    assert response.status_code == 409
    assert response.json() == {
        "detail": "Unique constraint violated: data already exists."
    }


async def test_add_single_media_duplicate_description():
    media_data = b"test file content"
    media_description = "Test Media Description"
    file_name = "testfile_02.txt"

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(
            "/media",
            files={"media_data": (file_name, io.BytesIO(media_data), "images/jpeg")},
            data={"media_description": media_description},
        )
    assert response.status_code == 409
    assert response.json() == {
        "detail": "Unique constraint violated: data already exists."
    }


async def test_update_single_media_standard():
    single_media = {
        "id": 1,
        "meme_url": "http://minio:9000/media-storage/images.jpg",
        "meme_description": "Котомем_01",
    }
    description = {"meme_description": "Котомем_01"}
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.put("/media/1", json=description)
    assert response.status_code == 200
    assert response.json() == single_media


async def test_update_single_media_non_existing_id():
    description = {"meme_description": "Котомем_01"}
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.put(f"/media/999", json=description)
    assert response.status_code == 404
    assert response.json() == {"detail": "This entry does not exist"}


async def test_delete_single_media_standard():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.delete("/media/1")
    assert response.status_code == 200
    assert response.json() == {"message": "Media successfully deleted."}


async def test_delete_single_media_non_existing_fish():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.delete("/media/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Entry not found."}
