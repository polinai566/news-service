from fastapi import APIRouter, Depends, Response, Request
from .schemas import SessionCreate, SessionRead, SessionAdminRead, SessionRefreshToken
from app.user.schemas import UserLogin
from .service import SessionService
from app.depends import get_jwt_payload, is_admin, is_same_user

router = APIRouter(tags=["sessions"])

async def session_service(service: SessionService = Depends()) -> SessionService:
    return service

@router.post("/", response_model=SessionCreate | str)
async def login(payload: UserLogin, response: Response, request: Request, service: SessionService = Depends(session_service)):
    return await service.create(payload, response, request)

@router.get("/admin/{user_id}", response_model=list[SessionAdminRead])
async def get_sessions_by_user_id_for_admin(user_id: int, service: SessionService = Depends(session_service), _ = Depends(is_admin)):
    return await service.list(user_id, SessionAdminRead)

@router.get("/{user_id}", response_model=list[SessionRead])
async def get_sessions_by_user_id_for_user(user_id: int, service: SessionService = Depends(session_service), _ = Depends(is_same_user)):
    return await service.list(user_id, SessionRead)

@router.put("/", response_model=SessionCreate | str)
async def refresh(payload: SessionRefreshToken, response: Response, request: Request, service: SessionService = Depends(session_service)):
    return await service.put(payload, response, request)

@router.delete("/", response_model=None | str)
async def logout(request: Request, service: SessionService = Depends(session_service), jwt_payload: str = Depends(get_jwt_payload)):
    return await service.delete(request, jwt_payload)