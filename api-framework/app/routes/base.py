from fastapi import APIRouter

router = APIRouter(prefix="/api", tags=["Health"])

@router.get("/health")
def health_check():
    return {"status": "ok"}

@router.get("/test-error")
def test_error():
    # Force an exception (division by zero)
    return 1 / 0