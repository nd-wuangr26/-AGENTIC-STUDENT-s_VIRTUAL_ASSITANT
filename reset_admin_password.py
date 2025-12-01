"""
Script để reset password admin
Chạy: python reset_admin_password.py
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from app.core.services.auth_service import get_password_hash
from app.core.services.mysql_service import get_mysql_service, init_mysql_service

async def reset_admin_password():
    """Reset password cho admin account"""
    print("=" * 50)
    print("RESET ADMIN PASSWORD")
    print("=" * 50)
    
    username = "admin"
    new_password = "admin123"
    
    # Initialize MySQL service
    await init_mysql_service()
    db = get_mysql_service()
    
    try:
        # Check if admin exists
        admin = await db.get_user_by_username(username)
        if not admin:
            print(f"❌ Admin user '{username}' không tồn tại!")
            print("Tạo admin mới...")
            
            # Create new admin
            password_hash = get_password_hash(new_password)
            user_id = await db.create_user(
                username=username,
                password_hash=password_hash,
                role='admin',
                mssv=None
            )
            print(f"✅ Tạo admin mới thành công!")
            print(f"   Username: {username}")
            print(f"   Password: {new_password}")
        else:
            # Update password
            password_hash = get_password_hash(new_password)
            query = "UPDATE users SET password_hash = %s WHERE username = %s"
            await db.execute_update(query, (password_hash, username))
            
            print(f"✅ Reset password thành công!")
            print(f"   Username: {username}")
            print(f"   Password: {new_password}")
            
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await db.close_pool()

if __name__ == "__main__":
    asyncio.run(reset_admin_password())
