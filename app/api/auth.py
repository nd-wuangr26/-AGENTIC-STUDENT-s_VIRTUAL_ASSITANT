from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from app.core.schenma.auth_schema import UserRegister, UserLogin, Token, UserResponse, TokenData
from app.core.services.auth_service import (
    verify_password, 
    get_password_hash, 
    create_access_token,
    decode_access_token
)
from app.core.services.mysql_service import get_mysql_service, MySQLService
from datetime import timedelta

router = APIRouter()
security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: MySQLService = Depends(get_mysql_service)
) -> dict:
    """Dependency để lấy user hiện tại từ token"""
    token = credentials.credentials
    payload = decode_access_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    username: str = payload.get("sub")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = await db.get_user_by_username(username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

async def get_current_admin_user(
    current_user: dict = Depends(get_current_user)
) -> dict:
    """Dependency để kiểm tra user có quyền admin không"""
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions. Admin access required."
        )
    return current_user

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,
    db: MySQLService = Depends(get_mysql_service)
):
    """
    Đăng ký tài khoản user.
    Username phải là MSSV (có thể là bất kỳ MSSV nào).
    """
    # Kiểm tra username đã tồn tại chưa
    existing_user = await db.get_user_by_username(user_data.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Hash password và tạo user
    password_hash = get_password_hash(user_data.password)
    user_id = await db.create_user(
        username=user_data.username,
        password_hash=password_hash,
        role="user",
        mssv=user_data.mssv
    )
    
    # Lấy thông tin user vừa tạo
    new_user = await db.get_user_by_username(user_data.username)
    return UserResponse(**new_user)

@router.post("/login", response_model=Token)
async def login(
    user_data: UserLogin,
    db: MySQLService = Depends(get_mysql_service)
):
    """
    Đăng nhập cho cả admin và user.
    Admin account chỉ được tạo trực tiếp trong database.
    """
    # Lấy user từ database
    user = await db.get_user_by_username(user_data.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Kiểm tra password
    if not verify_password(user_data.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Kiểm tra tài khoản có active không
    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled"
        )
    
    # Cập nhật last_login
    await db.update_last_login(user_data.username)
    
    # Tạo access token
    access_token = create_access_token(
        data={"sub": user["username"], "role": user["role"]}
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        role=user["role"],
        username=user["username"]
    )

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    """Lấy thông tin user hiện tại"""
    return UserResponse(**current_user)

@router.get("/verify-token")
async def verify_token(current_user: dict = Depends(get_current_user)):
    """Verify token và trả về thông tin user"""
    return {
        "valid": True,
        "username": current_user["username"],
        "role": current_user["role"]
    }
