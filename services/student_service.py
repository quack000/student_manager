import sqlite3
from db.connection import get_connection, remove_accents
from services.log_service import LogService

class StudentService:
    # Dịch vụ quản lý sinh viên: truy vấn, thêm, sửa, xóa và sinh mã sinh viên.
    def get_students(self, page=1, page_size=20, search_text="", class_filter="", status_filter=""):
        # Lấy danh sách sinh viên với phân trang và bộ lọc (lớp, trạng thái, tìm kiếm).
        conn = get_connection()
        if not conn: return [], 0
        try:
            cursor = conn.cursor()
            offset = (page - 1) * page_size
            
            conditions = []
            params = []

            if search_text:
                search_normalized = remove_accents(search_text)
                conditions.append("(no_accent(ho_ten) LIKE ? OR ma_sinh_vien LIKE ?)")
                params.extend([f"%{search_normalized}%", f"%{search_text}%"])
            
            if class_filter and class_filter != "Tất cả":
                conditions.append("ma_lop = ?")
                params.append(class_filter)
                
            if status_filter and status_filter != "Tất cả":
                conditions.append("trang_thai = ?")
                params.append(status_filter)

            where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""

            cursor.execute(f"SELECT COUNT(*) FROM sinh_vien {where_clause}", params)
            total_records = cursor.fetchone()[0]

            data_query = f"""
                SELECT ma_sinh_vien, ho_ten, gioi_tinh, ngay_sinh, ma_lop, email, sdt, dia_chi, trang_thai 
                FROM sinh_vien 
                {where_clause}
                ORDER BY ma_lop, ma_sinh_vien 
                LIMIT ? OFFSET ?
            """
            cursor.execute(data_query, params + [page_size, offset])
            students = [dict(row) for row in cursor.fetchall()]
            
            return students, total_records

        except sqlite3.Error as e:
            print(f"Lỗi Student Service: {e}")
            return [], 0
        finally:
            conn.close()

    def get_all_classes(self):
        # Lấy danh sách tất cả mã lớp (dùng cho dropdown).
        conn = get_connection()
        if not conn: return []
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT ma_lop FROM lop ORDER BY ma_lop DESC")
            return [row[0] for row in cursor.fetchall()]
        except sqlite3.Error:
            return []
        finally:
            conn.close()

    def check_exists(self, msv):
        # Kiểm tra xem mã sinh viên đã tồn tại chưa.
        conn = get_connection()
        if not conn: return False
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM sinh_vien WHERE ma_sinh_vien = ?", (msv,))
            return cursor.fetchone() is not None
        finally:
            conn.close()

    def generate_student_id(self, ma_lop):
        # Sinh mã sinh viên mới theo mã lớp (tự tăng suffix 3 chữ số).
        conn = get_connection()
        if not conn: return ""
        try:
            cursor = conn.cursor()
            query = "SELECT ma_sinh_vien FROM sinh_vien WHERE ma_lop = ? ORDER BY ma_sinh_vien DESC LIMIT 1"
            cursor.execute(query, (ma_lop,))
            result = cursor.fetchone()
            if result:
                last_msv = result[0]
                try:
                    prefix_len = len(ma_lop)
                    suffix = last_msv[prefix_len:]
                    next_seq = int(suffix) + 1
                except ValueError:
                    next_seq = 1
            else:
                next_seq = 1
            return f"{ma_lop}{next_seq:03d}"
        except sqlite3.Error:
            return ""
        finally:
            conn.close()

    def add_student(self, data, current_user="system"):
        # Thêm sinh viên mới và ghi log hành động.
        conn = get_connection()
        if not conn: return False, "Lỗi DB"
        try:
            cursor = conn.cursor()
            query = """
                INSERT INTO sinh_vien (ma_sinh_vien, ho_ten, gioi_tinh, ngay_sinh, ma_lop, email, sdt, dia_chi, trang_thai)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            params = (
                data['ma_sinh_vien'], data['ho_ten'], data['gioi_tinh'], 
                data['ngay_sinh'], data['ma_lop'], data['email'], 
                data.get('sdt', ''), data.get('dia_chi', ''), data['trang_thai']
            )
            cursor.execute(query, params)
            conn.commit()
            
            LogService().log_action(current_user, "INSERT", "sinh_vien", data['ma_sinh_vien'], data)
            return True, "Thêm thành công"
        except sqlite3.Error as e:
            return False, str(e)
        finally:
            conn.close()

    def update_student(self, data, current_user="system"):
        # Cập nhật thông tin sinh viên và ghi log.
        conn = get_connection()
        if not conn: return False, "Lỗi DB"
        try:
            cursor = conn.cursor()
            query = """
                UPDATE sinh_vien 
                SET ho_ten=?, gioi_tinh=?, ngay_sinh=?, ma_lop=?, email=?, sdt=?, dia_chi=?, trang_thai=?
                WHERE ma_sinh_vien=?
            """
            params = (
                data['ho_ten'], data['gioi_tinh'], data['ngay_sinh'], 
                data['ma_lop'], data['email'], data.get('sdt', ''), 
                data.get('dia_chi', ''), data['trang_thai'], data['ma_sinh_vien']
            )
            cursor.execute(query, params)
            conn.commit()
            
            LogService().log_action(current_user, "UPDATE", "sinh_vien", data['ma_sinh_vien'], data)
            return True, "Cập nhật thành công"
        except sqlite3.Error as e:
            return False, str(e)
        finally:
            conn.close()

    def delete_student(self, msv, user_role, current_user="system"):
        # Xóa sinh viên (chỉ quyền admin/dao_tao) và ghi log nếu thành công.
        if user_role not in ['admin', 'dao_tao']:
            return False, "Bạn không có quyền xóa sinh viên."

        conn = get_connection()
        if not conn: return False, "Lỗi DB"
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM dang_ky_hoc WHERE ma_sinh_vien = ?", (msv,))
            cursor.execute("DELETE FROM sinh_vien WHERE ma_sinh_vien = ?", (msv,))
            conn.commit()
            
            if cursor.rowcount > 0:
                LogService().log_action(current_user, "DELETE", "sinh_vien", msv, {"ly_do": "Xóa thủ công"})
                return True, "Đã xóa thành công."
            return False, "Không tìm thấy sinh viên."
        except sqlite3.Error as e:
            return False, str(e)
        finally:
            conn.close()