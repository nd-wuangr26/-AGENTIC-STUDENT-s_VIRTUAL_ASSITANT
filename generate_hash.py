"""
Tạo password hash cho admin
Không cần import app modules
"""

def create_admin_hash():
    try:
        from passlib.context import CryptContext
        
        pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
        password = 'admin123'
        hash_value = pwd_context.hash(password)
        
        print("=" * 50)
        print("PASSWORD HASH GENERATED")
        print("=" * 50)
        print(f"Password: {password}")
        print(f"Hash: {hash_value}")
        print("")
        print("Chạy lệnh SQL sau để update:")
        print("")
        print(f"UPDATE users SET password_hash = '{hash_value}' WHERE username = 'admin';")
        print("")
        
        return hash_value
        
    except ImportError:
        print("❌ Lỗi: passlib chưa được cài đặt")
        print("Chạy: pip install passlib==1.7.4 bcrypt==4.0.1")
        print("")
        print("Hoặc sử dụng hash có sẵn:")
        print("UPDATE users SET password_hash = '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi' WHERE username = 'admin';")
        return None

if __name__ == "__main__":
    create_admin_hash()
