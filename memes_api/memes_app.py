import logging
import os
from typing import List

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Query

from memes_schemas.memes_schemas import MemeUpdate, MemeRead

logging.basicConfig(level=logging.INFO)

memes_app = FastAPI(title="Public service for memes")

load_dotenv()

STORAGE_API_URL = os.getenv("STORAGE_API_URL")


@memes_app.get("/")
async def root():
    return "service is working"


@memes_app.get("/memes", response_model=List[MemeRead])
async def get_memes(skip: int = Query(0, ge=0), limit: int = Query(10, ge=1)):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{STORAGE_API_URL}/media", params={"skip": skip, "limit": limit}
            )
            response.raise_for_status()
            media = response.json()
            logging.info(f"Received media: {media}")

            return media
    except httpx.HTTPStatusError as e:
        logging.error(f"HTTP error occurred: {str(e)}")
        raise HTTPException(status_code=e.response.status_code)
    except httpx.RequestError as e:
        logging.error(f"Request error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail="Service is unavailable")


@memes_app.get("/memes/{id}", response_model=MemeRead)
async def get_single_meme(id: int):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{STORAGE_API_URL}/media/{id}")
            response.raise_for_status()
            media = response.json()
            return media
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code, detail="Object not found."
        )
    except httpx.RequestError as e:
        logging.error(f"Request error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail="Service is unavailable")


@memes_app.post("/memes", response_model=MemeRead)
async def upload_meme(
    meme_data: UploadFile = File(...),
    meme_description: str = Form(...),
):
    form_data = {
        "media_description": meme_description,
    }
    files = {
        "media_data": (meme_data.filename, meme_data.file, meme_data.content_type),
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{STORAGE_API_URL}/media",
                data=form_data,
                files=files,
            )
            response.raise_for_status()
            media = response.json()
            return media
    except httpx.HTTPStatusError as e:
        # Логирование статуса и ответа сервера
        logging.error(
            f"HTTP error occurred: {e.response.status_code} - {e.response.text}"
        )
        if e.response.status_code == 409:
            raise HTTPException(
                status_code=409, detail=e.response.json().get("detail", "Conflict")
            )
        try:
            detail = e.response.json().get("detail", "Internal Server Error")
        except ValueError:
            detail = "Internal Server Error"
        raise HTTPException(status_code=e.response.status_code, detail=detail)
    except httpx.RequestError:
        raise HTTPException(status_code=504, detail="Failed to upload file to storage")
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@memes_app.put("/memes/{id}", response_model=MemeRead)
async def update_meme(id: int, meme_update: MemeUpdate):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{STORAGE_API_URL}/media/{id}",
                json=meme_update.dict(),
            )
            response.raise_for_status()
            media = response.json()
            return media
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 409:
            raise HTTPException(
                status_code=409, detail=e.response.json().get("detail", "Conflict")
            )
        if e.response.status_code == 404:
            raise HTTPException(
                status_code=404, detail=e.response.json().get("detail", "This entry does not exist")
            )
        else:
            raise HTTPException(
                status_code=e.response.status_code, detail=e.response.json()
            )
    except httpx.RequestError as e:
        logging.error(f"Request error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail="Service is unavailable")


@memes_app.delete("/memes/{id}")
async def delete_single_meme(id: int):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.delete(f"{STORAGE_API_URL}/media/{id}")
            response.raise_for_status()
            return {"message": "Media successfully deleted."}
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise HTTPException(
                status_code=e.response.status_code, detail="Entry not found."
            )
        else:
            raise HTTPException(
                status_code=e.response.status_code, detail=e.response.json()
            )
    except httpx.RequestError as e:
        logging.error(f"Request error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail="Service is unavailable")
