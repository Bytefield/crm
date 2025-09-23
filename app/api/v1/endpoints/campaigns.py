from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def read_campaigns():
    """
    Test endpoint for campaigns.
    """
    return {"message": "Campaigns endpoint is working"}
