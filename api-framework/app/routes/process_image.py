from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.inference_service import infer_with_cache

router = APIRouter(prefix="/process", tags=["Processing"])

@router.post("/image")
async def process_image(
    file: UploadFile = File(...),
    confidence_threshold: float = 0.5,
):
    if file.content_type not in {"image/jpeg", "image/png"}:
        raise HTTPException(status_code=415, detail="Unsupported image type")

    data = await file.read()
    params = {"confidence_threshold": confidence_threshold}
    result = await infer_with_cache(data, params)
    return {
        "file_name": file.filename,
        "result": result,
    }
