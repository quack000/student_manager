import sqlite3
import csv
from db.connection import get_connection, remove_accents
from services.log_service import LogService

class GradeService:
    # Dịch vụ quản lý điểm: truy vấn, cập nhật, nhập/xuất CSV.
    def get_grades(self, page=1, page_size=20, search_text="", ma_lop="", ten_mon="", hoc_ky=""):
        # Truy vấn bảng điểm với phân trang và bộ lọc (lớp, môn, học kỳ).
        conn = get_connection()
        if not conn: return [], 0
        try:
            cursor = conn.cursor()
            offset = (page - 1) * page_size
            
            conditions = []
            params = []

            if search_text:
                search_no_accent = remove_accents(search_text)
                conditions.append("(no_accent(sv.ho_ten) LIKE ? OR sv.ma_sinh_vien LIKE ?)")
                params.extend([f"%{search_no_accent}%", f"%{search_text}%"])

            if ma_lop and ma_lop != "Tất cả":
                conditions.append("sv.ma_lop = ?")
                params.append(ma_lop)
            
            if ten_mon and ten_mon != "Tất cả":
                conditions.append("mh.ten_mon = ?")
                params.append(ten_mon)
                
            if hoc_ky and hoc_ky != "Tất cả":
                conditions.append("dk.hoc_ky = ?")
                params.append(hoc_ky)

            where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""

            base_query = f"""
                FROM diem d
                JOIN dang_ky_hoc dk ON d.id_dang_ky = dk.id
                JOIN sinh_vien sv ON dk.ma_sinh_vien = sv.ma_sinh_vien
                JOIN mon_hoc mh ON dk.ma_mon = mh.ma_mon
                {where_clause}
            """

            cursor.execute(f"SELECT COUNT(*) {base_query}", params)
            total_records = cursor.fetchone()[0]

            select_query = f"""
                SELECT 
                    d.id, sv.ma_sinh_vien, sv.ho_ten, sv.ma_lop,
                    mh.ten_mon, mh.so_tin_chi, dk.hoc_ky,
                    d.diem_qt, d.diem_gk, d.diem_ck, 
                    d.tong_diem_10, d.tong_diem_4
                {base_query}
                ORDER BY sv.ma_lop, sv.ma_sinh_vien, dk.hoc_ky
                LIMIT ? OFFSET ?
            """
            cursor.execute(select_query, params + [page_size, offset])
            grades = [dict(row) for row in cursor.fetchall()]
            return grades, total_records
        except sqlite3.Error as e:
            print(f"Lỗi GradeService: {e}")
            return [], 0
        finally:
            conn.close()

    def update_grade(self, grade_id, diem_qt, diem_gk, diem_ck, current_user="system"):
        # Cập nhật điểm một bản ghi, tính lại tổng điểm và hệ 4, rồi ghi log.
        conn = get_connection()
        if not conn: return False, "Lỗi DB"
        try:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT mh.ty_le_qt, mh.ty_le_gk, mh.ty_le_ck 
                FROM diem d
                JOIN dang_ky_hoc dk ON d.id_dang_ky = dk.id
                JOIN mon_hoc mh ON dk.ma_mon = mh.ma_mon
                WHERE d.id = ?
            """, (grade_id,))
            weights = cursor.fetchone()
            
            if not weights:
                return False, "Không tìm thấy thông tin môn học"
                
            w_qt, w_gk, w_ck = weights
            tong_10 = round((diem_qt * w_qt) + (diem_gk * w_gk) + (diem_ck * w_ck), 2)
            
            cursor.execute("SELECT diem_so FROM thang_diem WHERE ? >= diem_min AND ? < diem_max ORDER BY diem_min DESC LIMIT 1", (tong_10, tong_10))
            res_he_4 = cursor.fetchone()
            if not res_he_4:
                cursor.execute("SELECT diem_so FROM thang_diem ORDER BY diem_max DESC LIMIT 1")
                res_he_4 = cursor.fetchone()
            tong_4 = res_he_4[0] if res_he_4 else 0.0

            cursor.execute("""
                UPDATE diem 
                SET diem_qt=?, diem_gk=?, diem_ck=?, tong_diem_10=?, tong_diem_4=?
                WHERE id=?
            """, (diem_qt, diem_gk, diem_ck, tong_10, tong_4, grade_id))
            conn.commit()
            
            LogService().log_action(current_user, "UPDATE", "diem", grade_id, {"qt": diem_qt, "gk": diem_gk, "ck": diem_ck})
            
            return True, "Cập nhật điểm thành công"
        except sqlite3.Error as e:
            return False, str(e)
        finally:
            conn.close()

    def import_grades_from_csv(self, file_path, current_user="system"):
        # Nhập điểm từ file CSV; trả về số dòng thành công và ghi log import.
        conn = get_connection()
        if not conn: return False, "Không thể kết nối CSDL"
        success_count = 0
        error_list = []
        try:
            with open(file_path, mode='r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                reader.fieldnames = [name.strip() for name in reader.fieldnames]
                cursor = conn.cursor()
                for row in reader:
                    msv = row['ma_sinh_vien'].strip()
                    ma_mon = row['ma_mon'].strip()
                    hoc_ky = row['hoc_ky'].strip()
                    try:
                        qt = float(row['diem_qt'])
                        gk = float(row['diem_gk'])
                        ck = float(row['diem_ck'])
                        
                        cursor.execute("INSERT OR IGNORE INTO dang_ky_hoc (ma_sinh_vien, ma_mon, hoc_ky) VALUES (?, ?, ?)", (msv, ma_mon, hoc_ky))
                        cursor.execute("SELECT id FROM dang_ky_hoc WHERE ma_sinh_vien=? AND ma_mon=? AND hoc_ky=?", (msv, ma_mon, hoc_ky))
                        dk_row = cursor.fetchone()
                        if dk_row:
                            id_dang_ky = dk_row[0]
                            cursor.execute("INSERT OR IGNORE INTO diem (id_dang_ky, diem_qt, diem_gk, diem_ck, tong_diem_10, tong_diem_4) VALUES (?, 0, 0, 0, 0, 0)", (id_dang_ky,))
                            
                            cursor.execute("SELECT ty_le_qt, ty_le_gk, ty_le_ck FROM mon_hoc WHERE ma_mon=?", (ma_mon,))
                            w = cursor.fetchone()
                            if w:
                                tong_10 = round(qt*w[0] + gk*w[1] + ck*w[2], 2)
                                cursor.execute("SELECT diem_so FROM thang_diem WHERE ? >= diem_min AND ? < diem_max ORDER BY diem_min DESC LIMIT 1", (tong_10, tong_10))
                                res_he_4 = cursor.fetchone()
                                tong_4 = res_he_4[0] if res_he_4 else (4.0 if tong_10 >= 8.5 else 0.0)
                                cursor.execute("UPDATE diem SET diem_qt=?, diem_gk=?, diem_ck=?, tong_diem_10=?, tong_diem_4=? WHERE id_dang_ky=?", (qt, gk, ck, tong_10, tong_4, id_dang_ky))
                                success_count += 1
                    except Exception:
                        continue
                conn.commit()
                
            LogService().log_action(current_user, "IMPORT", "diem", "CSV", {"count": success_count})
            
            return True, f"Nhập thành công {success_count} dòng."
        except Exception as e:
            return False, f"Lỗi: {e}"
        finally:
            conn.close()

    def export_grades_to_csv(self, file_path, search_text="", ma_lop="", ten_mon="", hoc_ky=""):
        # Xuất danh sách điểm theo bộ lọc ra file CSV.
        conn = get_connection()
        if not conn: return False, "Lỗi DB"
        try:
            cursor = conn.cursor()
            conditions = []
            params = []
            if search_text:
                search_no_accent = remove_accents(search_text)
                conditions.append("(no_accent(sv.ho_ten) LIKE ? OR sv.ma_sinh_vien LIKE ?)")
                params.extend([f"%{search_no_accent}%", f"%{search_text}%"])
            if ma_lop and ma_lop != "Tất cả":
                conditions.append("sv.ma_lop = ?")
                params.append(ma_lop)
            if ten_mon and ten_mon != "Tất cả":
                conditions.append("mh.ten_mon = ?")
                params.append(ten_mon)
            if hoc_ky and hoc_ky != "Tất cả":
                conditions.append("dk.hoc_ky = ?")
                params.append(hoc_ky)
            where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
            query = f"""
                SELECT 
                    sv.ma_sinh_vien, sv.ho_ten, sv.ma_lop,
                    mh.ten_mon, mh.so_tin_chi, dk.hoc_ky,
                    d.diem_qt, d.diem_gk, d.diem_ck, 
                    d.tong_diem_10, d.tong_diem_4
                FROM diem d
                JOIN dang_ky_hoc dk ON d.id_dang_ky = dk.id
                JOIN sinh_vien sv ON dk.ma_sinh_vien = sv.ma_sinh_vien
                JOIN mon_hoc mh ON dk.ma_mon = mh.ma_mon
                {where_clause}
                ORDER BY sv.ma_lop, sv.ma_sinh_vien, dk.hoc_ky
            """
            cursor.execute(query, params)
            rows = cursor.fetchall()
            with open(file_path, mode='w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow(['Mã SV', 'Họ tên', 'Lớp', 'Môn học', 'Số tín chỉ', 'Học kỳ', 'Điểm QT', 'Điểm GK', 'Điểm CK', 'Tổng (10)', 'Hệ 4'])
                for row in rows:
                    writer.writerow(list(row))
            return True, f"Đã xuất {len(rows)} bản ghi."
        except Exception as e:
            return False, f"Lỗi: {e}"
        finally:
            conn.close()

    def get_filter_options(self):
        # Lấy tuỳ chọn lọc cho giao diện điểm (lớp, môn, học kỳ).
        conn = get_connection()
        options = {"lop": [], "mon": [], "hoc_ky": []}
        if not conn: return options
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT ma_lop FROM lop ORDER BY ma_lop DESC")
            options["lop"] = [r[0] for r in cursor.fetchall()]
            cursor.execute("SELECT ten_mon FROM mon_hoc ORDER BY ten_mon")
            options["mon"] = [r[0] for r in cursor.fetchall()]
            cursor.execute("SELECT DISTINCT hoc_ky FROM dang_ky_hoc ORDER BY hoc_ky DESC")
            options["hoc_ky"] = [r[0] for r in cursor.fetchall()]
            return options
        finally:
            conn.close()