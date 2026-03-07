import logging

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from api.dependencies import get_document_service
from core.config import get_settings
from core.exceptions import ValidationException
from models.response_models import UploadResponse
from services.document_service import DocumentService
from utils.file_utils import save_upload_file, validate_pdf_upload

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/upload", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    document_service: DocumentService = Depends(get_document_service),
) -> UploadResponse:
    settings = get_settings()
    try:
        validate_pdf_upload(file, settings.max_pdf_size_mb)
        saved_path = await save_upload_file(file, settings.upload_dir)
        document_id, chunks_created = await document_service.ingest_pdf(saved_path)
        return UploadResponse(document_id=document_id, chunks_created=chunks_created)
    except ValidationException as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("document_upload_failed")
        raise HTTPException(status_code=500, detail="Document ingestion failed") from exc
