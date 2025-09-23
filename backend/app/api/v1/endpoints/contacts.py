from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def read_contacts():
    """
    Test endpoint for contacts.
    """
    return {"message": "Contacts endpoint is working"}
