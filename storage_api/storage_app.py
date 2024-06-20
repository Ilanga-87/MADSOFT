import logging
from typing import Annotated, List

from fastapi import Form, FastAPI, Query
from fastapi import UploadFile, File, Depends, HTTPException

from schemas.media_schemas import MediaRead, MediaUpdate
from .dependencies import storage_service
from services.storage_service import StorageService

logging.basicConfig(level=logging.INFO)

storage_app = FastAPI(title="Private service for media")


@storage_app.get("/")
async def root():
    return "service is working"


@storage_app.get("/media", response_model=List[MediaRead])
async def get_all_media(
    media_service: Annotated[StorageService, Depends(storage_service)],
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
):
    try:
        media = await media_service.get_all_media(skip=skip, limit=limit)
        return media
    except HTTPException as e:
        logging.error(f"HTTPException: {e.detail}")
        raise e
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@storage_app.get("/media/{id}", response_model=MediaRead)
async def get_single_media(
    media_service: Annotated[StorageService, Depends(storage_service)], id: int
):
    try:
        media = await media_service.get_single_media(id)
        return media
    except HTTPException as e:
        raise e


@storage_app.post("/media", response_model=MediaRead)
async def upload_single_media(
    media_service: Annotated[StorageService, Depends(storage_service)],
    media_data: UploadFile = File(...),
    media_description: str = Form(...),
):
    try:
        media = await media_service.add_single_media(media_data, media_description)
        return media
    except HTTPException as e:
        logging.error(f"HTTPException: {e.detail}")
        raise e
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@storage_app.put("/media/{id}", response_model=MediaRead)
async def update_single_media(
    id: int,
    media_update: MediaUpdate,
    media_service: Annotated[StorageService, Depends(storage_service)],
):
    try:
        media = await media_service.update_single_media(id, media_update.model_dump())
        return media
    except HTTPException as e:
        raise e


@storage_app.delete("/media/{id}")
async def delete_single_media(
    media_service: Annotated[StorageService, Depends(storage_service)], id: int
):
    try:
        media = await media_service.delete_single_media(id)
        if media:
            return {"message": "Media successfully deleted."}
    except HTTPException as e:
        raise e
