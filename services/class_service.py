import sqlite3
from db.connection import get_connection, remove_accents
from services.log_service import LogService

# Dịch vụ quản lý lớp: truy vấn, thêm, sửa, xóa và gợi ý mã lớp.
class ClassService:
    def get_classes(self, page=1, page_size=20, search_text=""):
        # Lấy danh sách lớp có phân trang và tìm kiếm theo tên hoặc mã.
        conn = get_connection()
        if not conn: return [], 0
        try:
            cursor = conn.cursor()
            offset = (page - 1) * page_size
            
            conditions = []
            params = []

            if search_text:
                search_no_accent = remove_accents(search_text)
                conditions.append("(no_accent(l.ten_lop) LIKE ? OR l.ma_lop LIKE ?)")
                params.extend([f"%{search_no_accent}%", f"%{search_text}%"])
            
            where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""

            cursor.execute(f"SELECT COUNT(*) FROM lop l {where_clause}", params)
            total_records = cursor.fetchone()[0]

            query = f"""
                SELECT 
                    l.ma_lop, l.ten_lop, l.nam_nhap_hoc, l.nganh_hoc, 
                    l.ma_gv_co_van, gv.ho_ten as ten_cvht,
                    k.ten_khoa
                FROM lop l
                LEFT JOIN giang_vien gv ON l.ma_gv_co_van = gv.ma_gv
                LEFT JOIN khoa k ON l.nganh_hoc = k.ma_khoa
                {where_clause}
                ORDER BY l.nam_nhap_hoc DESC, l.ma_lop
                LIMIT ? OFFSET ?
            """
            cursor.execute(query, params + [page_size, offset])
            classes = [dict(row) for row in cursor.fetchall()]
            
            return classes, total_records

        except sqlite3.Error as e:
            print(f"Lỗi ClassService: {e}")
            return [], 0
        finally:
            conn.close()

    def get_lecturers(self):
        # Lấy danh sách giảng viên (mã và họ tên).
        conn = get_connection()
        if not conn: return []
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT ma_gv, ho_ten FROM giang_vien ORDER BY ho_ten")
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def get_majors(self):
        # Lấy danh sách khoa/ngành (mã và tên).
        conn = get_connection()
        if not conn: return []
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT ma_khoa, ten_khoa FROM khoa ORDER BY ten_khoa")
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def suggest_class_info(self, ma_khoa, nam_hoc):
        # Gợi ý `ma_lop` và `ten_lop` mới dựa trên khoa và năm nhập học.
        PREFIX_MAP = {'SE': 'KTPM', 'CS': 'KHMT', 'IS': 'HTTT', 'SEC': 'ATTT', 'NET': 'MMT'}
        try:
            nam = int(nam_hoc)
            khoa_so = nam - 2006
            if khoa_so < 1: khoa_so = 1
        except:
            return None, None

        prefix = PREFIX_MAP.get(ma_khoa, ma_khoa)
        base_code = f"{prefix}{khoa_so:02d}"

        conn = get_connection()
        if not conn: return None, None
        try:
            cursor = conn.cursor()
            query = f"SELECT COUNT(*) FROM lop WHERE ma_lop LIKE '{base_code}%'"
            cursor.execute(query)
            count = cursor.fetchone()[0]
            
            next_seq = count + 1
            
            ma_lop_new = f"{base_code}{next_seq:02d}"
            ten_lop_new = f"Lớp {prefix} {next_seq:02d} - Khóa {khoa_so}"
            return ma_lop_new, ten_lop_new
        finally:
            conn.close()

    def check_exists(self, ma_lop):
        # Kiểm tra xem mã lớp đã tồn tại trong DB hay chưa.
        conn = get_connection()
        if not conn: return False
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM lop WHERE ma_lop = ?", (ma_lop,))
            return cursor.fetchone() is not None
        finally:
            conn.close()

    def add_class(self, data, current_user="system"):
        # Thêm lớp mới và ghi log hành động.
        conn = get_connection()
        if not conn: return False, "Lỗi DB"
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO lop (ma_lop, ten_lop, nam_nhap_hoc, nganh_hoc, ma_gv_co_van)
                VALUES (?, ?, ?, ?, ?)
            """, (data['ma_lop'], data['ten_lop'], data['nam_nhap_hoc'], data['nganh_hoc'], data['ma_gv_co_van']))
            conn.commit()
            
            LogService().log_action(current_user, "INSERT", "lop", data['ma_lop'], data)
            
            return True, "Thêm lớp thành công"
        except sqlite3.Error as e:
            return False, str(e)
        finally:
            conn.close()

    def update_class(self, data, current_user="system"):
        # Cập nhật thông tin lớp và ghi log hành động.
        conn = get_connection()
        if not conn: return False, "Lỗi DB"
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE lop 
                SET ten_lop=?, nam_nhap_hoc=?, nganh_hoc=?, ma_gv_co_van=?
                WHERE ma_lop=?
            """, (data['ten_lop'], data['nam_nhap_hoc'], data['nganh_hoc'], data['ma_gv_co_van'], data['ma_lop']))
            conn.commit()
            
            LogService().log_action(current_user, "UPDATE", "lop", data['ma_lop'], data)
            
            return True, "Cập nhật thành công"
        except sqlite3.Error as e:
            return False, str(e)
        finally:
            conn.close()

    def delete_class(self, ma_lop, current_user="system"):
        # Xóa lớp nếu không có sinh viên, đồng thời ghi log.
        conn = get_connection()
        if not conn: return False, "Lỗi DB"
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM sinh_vien WHERE ma_lop = ?", (ma_lop,))
            if cursor.fetchone()[0] > 0:
                return False, "Không thể xóa lớp đang có sinh viên."
            
            cursor.execute("DELETE FROM lop WHERE ma_lop = ?", (ma_lop,))
            conn.commit()
            
            LogService().log_action(current_user, "DELETE", "lop", ma_lop, {})
            
            return True, "Đã xóa lớp học."
        except sqlite3.Error as e:
            return False, str(e)
        finally:
            conn.close()