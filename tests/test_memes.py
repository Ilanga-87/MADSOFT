import io

import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.exc import OperationalError

from ..config import configs
from ..database.db import Database
from ..memes_api.memes_app import memes_app as app

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
            "meme_url": "http://127.0.0.1:9000/media-storage/images.jpg",
            "meme_description": "Котомем_1",
        },
        {
            "id": 2,
            "meme_url": "http://127.0.0.1:9000/media-storage/images2.jpg",
            "meme_description": "Котомем_2",
        },
        {
            "id": 3,
            "meme_url": "http://127.0.0.1:9000/media-storage/cat-guys-have-bad-news-theronswag-woke-up-again.png",
            "meme_description": "Котомем_3",
        },
    ]
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get("/memes")
    json_response = response.json()
    len_response = len(json_response)
    assert response.status_code == 200
    assert len_response == 3
    assert response.json() == expected_response


async def test_get_single_memes_standard():
    single_memes = {
        "id": 1,
        "meme_url": "http://127.0.0.1:9000/media-storage/images.jpg",
        "meme_description": "Котомем_1",
    }
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get("/memes/1")
    assert response.status_code == 200
    assert response.json() == single_memes


async def test_get_single_memes_non_existing_id():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get("/memes/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Object not found."}


async def test_add_single_memes_standard():
    memes_data = b"test file content"
    memes_description = "Test Media Description"
    file_name = "testfile.txt"
    expected_response = {
        "meme_url": f"http://127.0.0.1:9000/media-storage/{file_name}",
        "meme_description": f"{memes_description}",
    }

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(
            "/memes",
            files={"meme_data": (file_name, io.BytesIO(memes_data), "images/jpeg")},
            data={"meme_description": memes_description},
        )
    assert response.status_code == 200

    response_json = response.json()
    assert response_json["meme_url"] == expected_response["meme_url"]
    assert response_json["meme_description"] == expected_response["meme_description"]


async def test_add_single_memes_duplicate_file():
    memes_data = b"test file content"
    memes_description = "Test Media Description 2"
    file_name = "testfile.txt"

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(
            "/memes",
            files={"meme_data": (file_name, io.BytesIO(memes_data), "images/jpeg")},
            data={"meme_description": memes_description},
        )
    assert response.status_code == 409
    assert response.json() == {
        "detail": "Unique constraint violated: data already exists."
    }


async def test_add_single_memes_duplicate_description():
    memes_data = b"test file content"
    memes_description = "Test Media Description"
    file_name = "testfile_02.txt"

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(
            "/memes",
            files={"meme_data": (file_name, io.BytesIO(memes_data), "images/jpeg")},
            data={"meme_description": memes_description},
        )
    assert response.status_code == 409
    assert response.json() == {
        "detail": "Unique constraint violated: data already exists."
    }


async def test_update_single_memes_standard():
    single_memes = {
        "id": 1,
        "meme_url": "http://127.0.0.1:9000/media-storage/images.jpg",
        "meme_description": "Котомем_01",
    }
    description = {"meme_description": "Котомем_01"}
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.put("/memes/1", json=description)
    assert response.status_code == 200
    assert response.json() == single_memes


async def test_update_single_memes_non_existing_id():
    description = {"meme_description": "Котомем_01"}
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.put(f"/memes/999", json=description)
    assert response.status_code == 404
    assert response.json() == {'detail': 'This entry does not exist'}


async def test_delete_single_memes_standard():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.delete("/memes/1")
    assert response.status_code == 200
    assert response.json() == {"message": "Media successfully deleted."}


async def test_delete_single_memes_non_existing_fish():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.delete("/memes/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Entry not found."}
