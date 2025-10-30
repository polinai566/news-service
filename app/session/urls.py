from fastapi import APIRouter, Depends, Response, Request
from .schemas import SessionRead, SessionRefreshToken
from app.user.schemas import UserLogin
from .service import SessionService
from fastapi.security import OAuth2PasswordBearer

router = APIRouter(tags=["sessions"])

oauth2 = OAuth2PasswordBearer(tokenUrl="/sessions/login")

async def session_service(service: SessionService = Depends()) -> SessionService:
    return service

@router.post("/", response_model=SessionRead | str)
async def login(payload: UserLogin, response: Response, request: Request, service: SessionService = Depends(session_service)):
    return await service.create(payload, response, request)

@router.get("/", response_model=list[SessionRead] | str)
async def get_session(service: SessionService = Depends(session_service), jwt_token: str = Depends(oauth2)):
    return await service.list(jwt_token)

@router.get("/{session_id}", response_model=SessionRead | str)
async def get_session_by_id(session_id: int, service: SessionService = Depends(session_service), jwt_token: str = Depends(oauth2)):
    return await service.get(session_id, jwt_token)

# refresh token -> новый JWT токен
@router.put("/", response_model=SessionRead | str)
async def refresh(payload: SessionRefreshToken, response: Response, request: Request, service: SessionService = Depends(session_service), jwt_token: str = Depends(oauth2)):
    return await service.put(payload, jwt_token, response, request)

@router.delete("/{session_id}", response_model=None | str)
async def logout(session_id: int, service: SessionService = Depends(session_service), jwt_token: str = Depends(oauth2)):
    return await service.delete(session_id, jwt_token)