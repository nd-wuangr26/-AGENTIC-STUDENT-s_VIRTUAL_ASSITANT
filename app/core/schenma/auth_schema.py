from pydantic import BaseModel, Field, validator
from typing import Optional, Literal
from datetime import datetime

class UserRegister(BaseModel):
    """Schema cho đăng ký user"""
    username: str = Field(..., min_length=3, max_length=50, description="Username (phải trùng với MSSV)")
    password: str = Field(..., min_length=6, description="Mật khẩu tối thiểu 6 ký tự")
    mssv: str = Field(..., min_length=3, max_length=20, description="Mã số sinh viên (bất kỳ)")
    
    @validator('username')
    def username_must_be_mssv(cls, v, values):
        """Username phải trùng với MSSV"""
        if 'mssv' in values and v != values['mssv']:
            raise ValueError('Username phải trùng với MSSV')
        return v

class UserLogin(BaseModel):
    """Schema cho đăng nhập"""
    username: str = Field(..., description="Username hoặc MSSV")
    password: str = Field(..., description="Mật khẩu")

class Token(BaseModel):
    """Schema cho JWT token"""
    access_token: str
    token_type: str = "bearer"
    role: str
    username: str

class TokenData(BaseModel):
    """Schema cho dữ liệu trong token"""
    username: Optional[str] = None
    role: Optional[str] = None

class UserResponse(BaseModel):
    """Schema cho response user info"""
    user_id: int
    username: str
    role: Literal['admin', 'user']
    mssv: Optional[str] = None
    created_at: datetime
    last_login: Optional[datetime] = None
    is_active: bool

    class Config:
        from_attributes = True
