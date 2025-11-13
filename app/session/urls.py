from fastapi import APIRouter, Depends, Response, Request
from .schemas import SessionCreate, SessionRead, SessionAdminRead, SessionRefreshToken
from app.user.schemas import UserLogin
from .service import SessionService
from fastapi.security import OAuth2PasswordBearer

router = APIRouter(tags=["sessions"])

oauth2 = OAuth2PasswordBearer(tokenUrl="/sessions/login")

async def session_service(service: SessionService = Depends()) -> SessionService:
    return service

@router.post("/", response_model=SessionCreate | str)
async def login(payload: UserLogin, response: Response, request: Request, service: SessionService = Depends(session_service)):
    return await service.create(payload, response, request)

@router.get("/{user_id}", response_model=list[SessionAdminRead] | list[SessionRead] | str)
async def get_sessions_by_user_id(user_id: int, service: SessionService = Depends(session_service), jwt_token: str = Depends(oauth2)):
    return await service.list(user_id, jwt_token)

@router.put("/", response_model=SessionCreate | str)
async def refresh(payload: SessionRefreshToken, response: Response, request: Request, service: SessionService = Depends(session_service)):
    return await service.put(payload, response, request)

@router.delete("/", response_model=None | str)
async def logout(request: Request, service: SessionService = Depends(session_service), jwt_token: str = Depends(oauth2)):
    return await service.delete(request, jwt_token)

@router.get("/auth/login")
async def github_auth_init(service: SessionService = Depends(session_service)):
    return await service.auth_init()

@router.get("/auth/callback", response_model=SessionRead | str)
async def github_auth_callback(response: Response, request: Request, service: SessionService = Depends(session_service)):
    return await service.auth_callback(response, request)