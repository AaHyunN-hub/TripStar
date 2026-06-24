"""身份认证路由 - 注册 / 登录"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...database import get_db
from ...models.user import User
from ...services.auth_service import hash_password, verify_password, create_access_token, require_user

router = APIRouter(prefix="/auth", tags=["身份认证"])


# ============ 请求/响应模型 ============

class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=2, max_length=32, description="用户名")
    password: str = Field(..., min_length=6, max_length=128, description="密码")


class LoginRequest(BaseModel):
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")


class AuthResponse(BaseModel):
    success: bool
    message: str
    token: str = ""
    user: dict = {}


# ============ 注册 ============

@router.post("/register", response_model=AuthResponse)
async def register(req: RegisterRequest, db: AsyncSession = Depends(get_db)):
    # 检查用户名是否已存在
    result = await db.execute(select(User).where(User.username == req.username))
    if result.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="用户名已存在",
        )

    # 创建用户
    user = User(
        username=req.username,
        password_hash=hash_password(req.password),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    # 签发 token
    token = create_access_token(user.id, user.username)

    return AuthResponse(
        success=True,
        message="注册成功",
        token=token,
        user={"id": user.id, "username": user.username},
    )


# ============ 登录 ============

@router.post("/login", response_model=AuthResponse)
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.username == req.username))
    user = result.scalar_one_or_none()

    if user is None or not verify_password(req.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )

    token = create_access_token(user.id, user.username)

    return AuthResponse(
        success=True,
        message="登录成功",
        token=token,
        user={"id": user.id, "username": user.username},
    )


# ============ 获取当前用户信息 ============

@router.get("/me")
async def get_me(user: User = Depends(require_user)):
    return {
        "success": True,
        "user": {
            "id": user.id,
            "username": user.username,
            "created_at": user.created_at.isoformat() if user.created_at else None,
        },
    }
