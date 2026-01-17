import sqlite3
from db.connection import get_connection, remove_accents
from services.log_service import LogService

class SubjectService:
    # Dịch vụ quản lý môn học: truy vấn, thêm, sửa, xóa và kiểm tra tồn tại.
    def get_subjects(self, page=1, page_size=20, search_text=""):
        # Lấy danh sách môn học có phân trang và tìm kiếm theo tên hoặc mã.
        conn = get_connection()
        if not conn: return [], 0
        try:
            cursor = conn.cursor()
            offset = (page - 1) * page_size
            
            conditions = []
            params = []

            if search_text:
                search_no_accent = remove_accents(search_text)
                conditions.append("(no_accent(ten_mon) LIKE ? OR ma_mon LIKE ?)")
                params.extend([f"%{search_no_accent}%", f"%{search_text}%"])
            
            where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""

            cursor.execute(f"SELECT COUNT(*) FROM mon_hoc {where_clause}", params)
            total_records = cursor.fetchone()[0]

            query = f"""
                SELECT * FROM mon_hoc
                {where_clause}
                ORDER BY ma_mon
                LIMIT ? OFFSET ?
            """
            cursor.execute(query, params + [page_size, offset])
            subjects = [dict(row) for row in cursor.fetchall()]
            
            return subjects, total_records

        except sqlite3.Error as e:
            print(f"Lỗi SubjectService: {e}")
            return [], 0
        finally:
            conn.close()

    def check_exists(self, ma_mon):
        # Kiểm tra mã môn học có trong DB không.
        conn = get_connection()
        if not conn: return False
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM mon_hoc WHERE ma_mon = ?", (ma_mon,))
            return cursor.fetchone() is not None
        finally:
            conn.close()

    def add_subject(self, data, current_user="system"):
        # Thêm môn học mới (kiểm tra tổng trọng số trước) và ghi log.
        conn = get_connection()
        if not conn: return False, "Lỗi DB"
        try:
            total_weight = data['ty_le_qt'] + data['ty_le_gk'] + data['ty_le_ck']
            if abs(total_weight - 1.0) > 0.001:
                return False, f"Tổng trọng số phải bằng 1.0 (Hiện tại: {total_weight})"

            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO mon_hoc (ma_mon, ten_mon, so_tin_chi, ty_le_qt, ty_le_gk, ty_le_ck)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (data['ma_mon'], data['ten_mon'], data['so_tin_chi'], 
                  data['ty_le_qt'], data['ty_le_gk'], data['ty_le_ck']))
            conn.commit()
            
            LogService().log_action(current_user, "INSERT", "mon_hoc", data['ma_mon'], data)
            
            return True, "Thêm môn học thành công"
        except sqlite3.Error as e:
            return False, str(e)
        finally:
            conn.close()

    def update_subject(self, data, current_user="system"):
        # Cập nhật thông tin môn học với kiểm tra trọng số và ghi log.
        conn = get_connection()
        if not conn: return False, "Lỗi DB"
        try:
            total_weight = data['ty_le_qt'] + data['ty_le_gk'] + data['ty_le_ck']
            if abs(total_weight - 1.0) > 0.001:
                return False, f"Tổng trọng số phải bằng 1.0 (Hiện tại: {total_weight})"

            cursor = conn.cursor()
            cursor.execute("""
                UPDATE mon_hoc 
                SET ten_mon=?, so_tin_chi=?, ty_le_qt=?, ty_le_gk=?, ty_le_ck=?
                WHERE ma_mon=?
            """, (data['ten_mon'], data['so_tin_chi'], 
                  data['ty_le_qt'], data['ty_le_gk'], data['ty_le_ck'], data['ma_mon']))
            conn.commit()
            
            LogService().log_action(current_user, "UPDATE", "mon_hoc", data['ma_mon'], data)
            
            return True, "Cập nhật thành công"
        except sqlite3.Error as e:
            return False, str(e)
        finally:
            conn.close()

    def delete_subject(self, ma_mon, current_user="system"):
        # Xóa môn học nếu chưa có sinh viên đăng ký, đồng thời ghi log.
        conn = get_connection()
        if not conn: return False, "Lỗi DB"
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM dang_ky_hoc WHERE ma_mon = ?", (ma_mon,))
            if cursor.fetchone()[0] > 0:
                return False, "Không thể xóa môn học đã có sinh viên đăng ký."
            
            cursor.execute("DELETE FROM mon_hoc WHERE ma_mon = ?", (ma_mon,))
            conn.commit()
            
            LogService().log_action(current_user, "DELETE", "mon_hoc", ma_mon, {})
            
            return True, "Đã xóa môn học."
        except sqlite3.Error as e:
            return False, str(e)
        finally:
            conn.close()