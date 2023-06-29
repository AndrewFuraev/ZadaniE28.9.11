from pydantic import BaseModel, constr

class AuthRequestModel(BaseModel):
    username: constr(strict=True)   # Валидное для аутоидендификации username : admin
    password: constr(strict=True)   # Валидный для аутоидендификации password: password123

class AuthResponse(BaseModel):
    token: str