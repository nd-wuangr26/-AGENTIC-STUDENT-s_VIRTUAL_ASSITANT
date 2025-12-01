"""
Script để tạo admin account mới
Chạy: python create_admin.py
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from app.core.services.auth_service import get_password_hash
from app.core.services.mysql_service import get_mysql_service, init_mysql_service
import getpass

async def create_admin():
    """Tạo admin account mới"""
    print("=" * 50)
    print("TẠO ADMIN ACCOUNT MỚI")
    print("=" * 50)
    
    # Get admin info
    username = input("Nhập username cho admin: ").strip()
    if not username:
        print("❌ Username không được để trống!")
        return
    
    password = getpass.getpass("Nhập password: ")
    confirm_password = getpass.getpass("Xác nhận password: ")
    
    if password != confirm_password:
        print("❌ Password không khớp!")
        return
    
    if len(password) < 6:
        print("❌ Password phải có ít nhất 6 ký tự!")
        return
    
    # Initialize MySQL service
    await init_mysql_service()
    db = get_mysql_service()
    
    # Check if username exists
    existing_user = await db.get_user_by_username(username)
    if existing_user:
        print(f"❌ Username '{username}' đã tồn tại!")
        return
    
    # Hash password
    password_hash = get_password_hash(password)
    
    # Create admin user
    try:
        user_id = await db.create_user(
            username=username,
            password_hash=password_hash,
            role='admin',
            mssv=None
        )
        
        print(f"\n✅ Tạo admin account thành công!")
        print(f"   User ID: {user_id}")
        print(f"   Username: {username}")
        print(f"   Role: admin")
        print(f"\nBạn có thể đăng nhập với:")
        print(f"   Username: {username}")
        print(f"   Password: {password}")
        
    except Exception as e:
        print(f"❌ Lỗi khi tạo admin: {e}")
    finally:
        await db.close_pool()

if __name__ == "__main__":
    asyncio.run(create_admin())
