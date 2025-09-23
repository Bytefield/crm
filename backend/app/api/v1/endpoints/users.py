from fastapi import APIRouter

router = APIRouter()

@router.get("/me")
def read_user_me():
    """
    Get current user (simplified for testing).
    """
    return {"message": "This is a test endpoint"}
