import sqlite3
import json
from datetime import datetime
from db.connection import get_connection

class LogService:
    # Dịch vụ ghi nhật ký hệ thống: lưu hành động người dùng vào bảng `nhat_ky_he_thong`.
    def log_action(self, user, action, table, object_id, detail_dict=None):
        # Ghi log chi tiết (timestamp, user, action, table, object id, JSON detail).
        conn = get_connection()
        if not conn: return False
        try:
            cursor = conn.cursor()
            
            detail_json = json.dumps(detail_dict, ensure_ascii=False) if detail_dict else ""
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            cursor.execute("""
                INSERT INTO nhat_ky_he_thong (thoi_gian, nguoi_thuc_hien, hanh_dong, ten_bang, doi_tuong_id, noi_dung_chi_tiet)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (now, user, action, table, str(object_id), detail_json))
            
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"❌ Lỗi ghi log: {e}")
            return False
        finally:
            conn.close()

    def get_logs(self, page=1, page_size=20, search_text=""):
        # Lấy danh sách log có phân trang và hỗ trợ tìm kiếm theo user/hành động/bảng.
        conn = get_connection()
        if not conn: return [], 0
        try:
            cursor = conn.cursor()
            offset = (page - 1) * page_size
            
            conditions = []
            params = []

            if search_text:
                search_pattern = f"%{search_text}%"
                conditions.append("(nguoi_thuc_hien LIKE ? OR hanh_dong LIKE ? OR ten_bang LIKE ?)")
                params.extend([search_pattern, search_pattern, search_pattern])
            
            where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""

            cursor.execute(f"SELECT COUNT(*) FROM nhat_ky_he_thong {where_clause}", params)
            total_records = cursor.fetchone()[0]

            query = f"""
                SELECT id, thoi_gian, nguoi_thuc_hien, hanh_dong, ten_bang, doi_tuong_id, noi_dung_chi_tiet
                FROM nhat_ky_he_thong
                {where_clause}
                ORDER BY thoi_gian DESC
                LIMIT ? OFFSET ?
            """
            cursor.execute(query, params + [page_size, offset])
            logs = [dict(row) for row in cursor.fetchall()]
            
            return logs, total_records

        except sqlite3.Error as e:
            print(f"Lỗi lấy log: {e}")
            return [], 0
        finally:
            conn.close()