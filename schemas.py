from pydantic import BaseModel

class RegisterRequest(BaseModel):
    email: str
    password: str


class CreateLinkRequest(BaseModel):
    original_url: str