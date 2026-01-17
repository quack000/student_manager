import sqlite3
from db.connection import get_connection, remove_accents

class GPAService:
    # Dịch vụ tính toán điểm trung bình (CPA/GPA) và tổng tín chỉ tích lũy.
    def calculate_cpa_and_credits(self, msv):
        # Tính CPA và tổng tín chỉ tích lũy; nếu học lại thì lấy điểm hệ 4 cao nhất.
        conn = get_connection()
        if not conn: return 0.0, 0
        
        try:
            cursor = conn.cursor()
            query = """
                SELECT mh.so_tin_chi, MAX(d.tong_diem_4) as diem_max
                FROM diem d
                JOIN dang_ky_hoc dk ON d.id_dang_ky = dk.id
                JOIN mon_hoc mh ON dk.ma_mon = mh.ma_mon
                WHERE dk.ma_sinh_vien = ? AND d.tong_diem_4 IS NOT NULL
                GROUP BY mh.ma_mon, mh.so_tin_chi
            """
            cursor.execute(query, (msv,))
            rows = cursor.fetchall()
            
            total_points = 0
            total_credits = 0
            accumulated_credits = 0
            
            for row in rows:
                tin_chi = row['so_tin_chi']
                diem_4 = row['diem_max']
                
                total_points += diem_4 * tin_chi
                total_credits += tin_chi
                
                if diem_4 >= 1.0:
                    accumulated_credits += tin_chi
            
            cpa = round(total_points / total_credits, 2) if total_credits > 0 else 0.0
            
            return cpa, accumulated_credits
            
        except sqlite3.Error:
            return 0.0, 0
        finally:
            conn.close()

    def get_semester_gpa(self, msv, hoc_ky):
        # Tính GPA cho một học kỳ cụ thể (trả về float).
        conn = get_connection()
        if not conn: return 0.0
        try:
            cursor = conn.cursor()
            query = """
                SELECT mh.so_tin_chi, d.tong_diem_4
                FROM diem d
                JOIN dang_ky_hoc dk ON d.id_dang_ky = dk.id
                JOIN mon_hoc mh ON dk.ma_mon = mh.ma_mon
                WHERE dk.ma_sinh_vien = ? AND dk.hoc_ky = ? AND d.tong_diem_4 IS NOT NULL
            """
            cursor.execute(query, (msv, hoc_ky))
            rows = cursor.fetchall()
            
            total_p = 0
            total_c = 0
            for row in rows:
                total_p += row['tong_diem_4'] * row['so_tin_chi']
                total_c += row['so_tin_chi']
                
            return round(total_p / total_c, 2) if total_c > 0 else 0.0
        finally:
            conn.close()

    def get_academic_list(self, page=1, page_size=20, search_text="", ma_lop=""):
        # Lấy danh sách sinh viên kèm CPA, xếp loại và tổng tín chỉ (phân trang).
        conn = get_connection()
        if not conn: return [], 0
        try:
            cursor = conn.cursor()
            offset = (page - 1) * page_size
            
            conditions = []
            params = []

            if search_text:
                no_accent = remove_accents(search_text)
                conditions.append("(no_accent(ho_ten) LIKE ? OR ma_sinh_vien LIKE ?)")
                params.extend([f"%{no_accent}%", f"%{search_text}%"])
            
            if ma_lop and ma_lop != "Tất cả":
                conditions.append("ma_lop = ?")
                params.append(ma_lop)
            
            where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""

            count_query = f"SELECT COUNT(*) FROM sinh_vien {where_clause}"
            cursor.execute(count_query, params)
            total = cursor.fetchone()[0]

            data_query = f"""
                SELECT ma_sinh_vien, ho_ten, ma_lop, trang_thai 
                FROM sinh_vien 
                {where_clause}
                ORDER BY ma_lop, ma_sinh_vien
                LIMIT ? OFFSET ?
            """
            cursor.execute(data_query, params + [page_size, offset])
            students = [dict(row) for row in cursor.fetchall()]
            
            results = []
            for sv in students:
                msv = sv['ma_sinh_vien']
                cpa, acc_credits = self.calculate_cpa_and_credits(msv)
                
                xep_loai = ""
                if cpa >= 3.6: xep_loai = "Xuất sắc"
                elif cpa >= 3.2: xep_loai = "Giỏi"
                elif cpa >= 2.5: xep_loai = "Khá"
                elif cpa >= 2.0: xep_loai = "Trung bình"
                else: xep_loai = "Yếu/Cảnh báo"

                sv['cpa'] = cpa
                sv['tin_chi'] = acc_credits
                sv['xep_loai'] = xep_loai
                results.append(sv)
                
            return results, total
        finally:
            conn.close()

    def get_filter_options(self):
        # Lấy các tuỳ chọn lọc (danh sách lớp) cho giao diện CPA.
        conn = get_connection()
        if not conn: return []
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT ma_lop FROM lop ORDER BY ma_lop DESC")
            return [r[0] for r in cursor.fetchall()]
        finally:
            conn.close()