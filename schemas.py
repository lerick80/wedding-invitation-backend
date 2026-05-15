from pydantic import BaseModel

class ConfirmGuest(BaseModel):
    code: str
    guests: int
