import sqlite3
from db.connection import get_connection

# Dịch vụ cung cấp dữ liệu tổng quan và số liệu cho màn hình dashboard.
class DashboardService:
    # Trả về số liệu tóm tắt: số sinh viên đang học, giảng viên, lớp, và môn học.
    def get_summary_stats(self):
        conn = get_connection()
        if not conn:
            return {"sinh_vien": 0, "giang_vien": 0, "lop": 0, "mon_hoc": 0}
        
        try:
            cursor = conn.cursor()
            return {
                "sinh_vien": cursor.execute("SELECT COUNT(*) FROM sinh_vien WHERE trang_thai='Đang học'").fetchone()[0],
                "giang_vien": cursor.execute("SELECT COUNT(*) FROM giang_vien").fetchone()[0],
                "lop": cursor.execute("SELECT COUNT(*) FROM lop").fetchone()[0],
                "mon_hoc": cursor.execute("SELECT COUNT(*) FROM mon_hoc").fetchone()[0]
            }
        except sqlite3.Error as e:
            print(f"Lỗi Dashboard: {e}")
            return {"sinh_vien": 0, "giang_vien": 0, "lop": 0, "mon_hoc": 0}
        finally:
            conn.close()

    # Trả về danh sách Top 10 môn theo tỷ lệ rớt cao nhất (định dạng: [{'ten_mon','ty_le'}]).
    def get_top_failed_subjects(self):
        """Lấy Top 10 môn có tỷ lệ rớt cao nhất (Điểm < 4.0)"""
        conn = get_connection()
        if not conn: return []
        try:
            cursor = conn.cursor()
            query = """
                SELECT 
                    mh.ten_mon,
                    COUNT(d.id) as total_sv,
                    SUM(CASE WHEN d.tong_diem_10 < 4.0 THEN 1 ELSE 0 END) as failed_sv
                FROM diem d
                JOIN dang_ky_hoc dk ON d.id_dang_ky = dk.id
                JOIN mon_hoc mh ON dk.ma_mon = mh.ma_mon
                GROUP BY mh.ma_mon, mh.ten_mon
                HAVING total_sv > 0
                ORDER BY (CAST(failed_sv AS FLOAT) / total_sv) DESC
                LIMIT 10
            """
            cursor.execute(query)
            data = []
            for row in cursor.fetchall():
                percent = round((row[2] / row[1]) * 100, 1) if row[1] > 0 else 0
                data.append({"ten_mon": row[0], "ty_le": percent})
            return data
        except sqlite3.Error as e:
            print(f"Lỗi biểu đồ Rớt môn: {e}")
            return []
        finally:
            conn.close()

    # Trả về Top 10 lớp có GPA trung bình cao nhất (gpa làm tròn 2 chữ số).
    def get_top_classes_by_gpa(self):
        """
        Lấy Top 10 lớp có GPA trung bình cao nhất.
        Công thức: Tổng(Điểm hệ 4 * Số tín chỉ) / Tổng(Số tín chỉ) của toàn lớp.
        """
        conn = get_connection()
        if not conn: return []
        try:
            cursor = conn.cursor()
            query = """
                SELECT 
                    sv.ma_lop,
                    SUM(d.tong_diem_4 * mh.so_tin_chi) / SUM(mh.so_tin_chi) as avg_gpa
                FROM diem d
                JOIN dang_ky_hoc dk ON d.id_dang_ky = dk.id
                JOIN sinh_vien sv ON dk.ma_sinh_vien = sv.ma_sinh_vien
                JOIN mon_hoc mh ON dk.ma_mon = mh.ma_mon
                WHERE d.tong_diem_4 IS NOT NULL
                GROUP BY sv.ma_lop
                HAVING SUM(mh.so_tin_chi) > 0
                ORDER BY avg_gpa DESC
                LIMIT 10
            """
            cursor.execute(query)
            data = []
            for row in cursor.fetchall():
                data.append({
                    "ma_lop": row[0], 
                    "gpa": round(row[1], 2)
                })
            return data
        except sqlite3.Error as e:
            print(f"Lỗi biểu đồ GPA lớp: {e}")
            return []
        finally:
            conn.close()