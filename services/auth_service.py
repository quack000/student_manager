import hashlib
import sqlite3
from db.connection import get_connection
from services.log_service import LogService

# Dịch vụ xử lý xác thực người dùng.
class AuthService:
    # Đăng nhập: xác thực username/password, kiểm tra trạng thái và trả về thông tin người dùng.
    def login(self, username, password):
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        conn = get_connection()
        if not conn: return None
            
        try:
            cursor = conn.cursor()
            query = """
                SELECT id, ten_dang_nhap, vai_tro, ma_gv, trang_thai 
                FROM nguoi_dung 
                WHERE ten_dang_nhap = ? AND mat_khau_hash = ?
            """
            cursor.execute(query, (username, password_hash))
            user = cursor.fetchone()
            
            if user:
                if user['trang_thai'] == 0:
                    return {"error": "Tài khoản đã bị khóa"}
                
                LogService().log_action(username, "LOGIN", "nguoi_dung", user['id'], {"vai_tro": user['vai_tro']})
                
                return dict(user) 
            else:
                return None
                
        except sqlite3.Error as e:
            print(f"Lỗi Auth Service: {e}")
            return None
        finally:
            conn.close()