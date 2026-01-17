import sqlite3
import os
import hashlib

# Cấu hình đường dẫn DB
DB_PATH = "student_manager.db"

def get_admin_password_hash():
    """Tạo hash SHA256 cho mật khẩu mặc định '123456'"""
    return hashlib.sha256('123456'.encode()).hexdigest()
def get_gv_password_hash():
    """Tạo hash SHA256 cho mật khẩu mặc định '654321'"""
    return hashlib.sha256('654321'.encode()).hexdigest()

def run_migrations():
    print(f"🔄 Đang khởi tạo cơ sở dữ liệu tại: {DB_PATH}...")
    
    # Kết nối DB
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Bật Foreign Keys để đảm bảo toàn vẹn dữ liệu
    cursor.execute("PRAGMA foreign_keys = ON;")

    # ==========================================================================
    # 1. ĐỊNH NGHĨA SCHEMA (BẢNG & TRIGGER)
    # ==========================================================================
    schema_script = """
    -- 1. KHOA
    CREATE TABLE IF NOT EXISTS khoa (
        ma_khoa TEXT PRIMARY KEY,
        ten_khoa TEXT NOT NULL
    );

    -- 2. GIẢNG VIÊN
    CREATE TABLE IF NOT EXISTS giang_vien (
        ma_gv TEXT PRIMARY KEY,
        ho_ten TEXT NOT NULL,
        ngay_sinh TEXT,
        sdt TEXT,
        email TEXT UNIQUE,
        hoc_vi TEXT CHECK(hoc_vi IN ('ThS','TS','PGS','GS')),
        ma_khoa TEXT,
        FOREIGN KEY(ma_khoa) REFERENCES khoa(ma_khoa)
    );

    -- 3. NGƯỜI DÙNG (ĐĂNG NHẬP)
    CREATE TABLE IF NOT EXISTS nguoi_dung (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ten_dang_nhap TEXT UNIQUE NOT NULL,
        mat_khau_hash TEXT NOT NULL,
        vai_tro TEXT CHECK(vai_tro IN ('admin','dao_tao','giang_vien')) DEFAULT 'dao_tao',
        ma_gv TEXT,
        trang_thai INTEGER DEFAULT 1,
        FOREIGN KEY(ma_gv) REFERENCES giang_vien(ma_gv) ON DELETE SET NULL
    );

    -- 4. LỚP
    CREATE TABLE IF NOT EXISTS lop (
        ma_lop TEXT PRIMARY KEY,
        ten_lop TEXT NOT NULL,
        nam_nhap_hoc INTEGER NOT NULL,
        nganh_hoc TEXT,
        ma_gv_co_van TEXT,
        FOREIGN KEY(ma_gv_co_van) REFERENCES giang_vien(ma_gv)
    );

    -- 5. SINH VIÊN (ĐÃ CẬP NHẬT CHECK CONSTRAINT TIẾNG VIỆT CÓ DẤU)
    CREATE TABLE IF NOT EXISTS sinh_vien (
        ma_sinh_vien TEXT PRIMARY KEY,
        ho_ten TEXT NOT NULL,
        gioi_tinh TEXT CHECK(gioi_tinh IN ('Nam','Nữ','Khác')), -- Sửa: Nữ
        ngay_sinh TEXT NOT NULL,
        email TEXT UNIQUE,
        sdt TEXT,
        dia_chi TEXT,
        ma_lop TEXT NOT NULL,
        trang_thai TEXT CHECK(trang_thai IN ('Đang học','Bảo lưu','Thôi học','Tốt nghiệp')) 
            DEFAULT 'Đang học', -- Sửa: Đang học
        FOREIGN KEY(ma_lop) REFERENCES lop(ma_lop)
    );

    -- 6. MÔN HỌC
    CREATE TABLE IF NOT EXISTS mon_hoc (
        ma_mon TEXT PRIMARY KEY,
        ten_mon TEXT NOT NULL,
        so_tin_chi INTEGER NOT NULL,
        ty_le_qt REAL DEFAULT 0.1,
        ty_le_gk REAL DEFAULT 0.3,
        ty_le_ck REAL DEFAULT 0.6,
        CHECK (ABS(ty_le_qt + ty_le_gk + ty_le_ck - 1.0) < 0.001)
    );

    -- 7. THANG ĐIỂM (HỆ 4)
    CREATE TABLE IF NOT EXISTS thang_diem (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        diem_min REAL NOT NULL,
        diem_max REAL NOT NULL,
        diem_chu TEXT NOT NULL,
        diem_so REAL CHECK(diem_so BETWEEN 0 AND 4),
        xep_loai TEXT
    );

    -- 8. ĐĂNG KÝ HỌC
    CREATE TABLE IF NOT EXISTS dang_ky_hoc (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ma_sinh_vien TEXT NOT NULL,
        ma_mon TEXT NOT NULL,
        hoc_ky TEXT NOT NULL,
        ngay_dang_ky DATETIME DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(ma_sinh_vien, ma_mon, hoc_ky),
        FOREIGN KEY(ma_sinh_vien) REFERENCES sinh_vien(ma_sinh_vien),
        FOREIGN KEY(ma_mon) REFERENCES mon_hoc(ma_mon)
    );

    -- 9. ĐIỂM
    CREATE TABLE IF NOT EXISTS diem (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_dang_ky INTEGER UNIQUE NOT NULL,
        diem_qt REAL CHECK(diem_qt BETWEEN 0 AND 10),
        diem_gk REAL CHECK(diem_gk BETWEEN 0 AND 10),
        diem_ck REAL CHECK(diem_ck BETWEEN 0 AND 10),
        tong_diem_10 REAL,
        tong_diem_4 REAL,
        ghi_chu TEXT,
        FOREIGN KEY(id_dang_ky) REFERENCES dang_ky_hoc(id) ON DELETE CASCADE
    );

    -- 10. NHẬT KÝ HỆ THỐNG
    CREATE TABLE IF NOT EXISTS nhat_ky_he_thong (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        thoi_gian DATETIME DEFAULT CURRENT_TIMESTAMP,
        nguoi_thuc_hien TEXT,
        hanh_dong TEXT,
        ten_bang TEXT,
        doi_tuong_id TEXT,
        noi_dung_chi_tiet TEXT
    );

    -- 11. FTS5 (FULL TEXT SEARCH) - TÌM KIẾM NHANH
    CREATE VIRTUAL TABLE IF NOT EXISTS fts_sinh_vien USING fts5(
        ho_ten, 
        ma_sinh_vien, 
        email, 
        content='sinh_vien', 
        content_rowid='rowid'
    );

    -- Trigger FTS: INSERT
    CREATE TRIGGER IF NOT EXISTS sinh_vien_ai AFTER INSERT ON sinh_vien BEGIN
      INSERT INTO fts_sinh_vien(rowid, ho_ten, ma_sinh_vien, email) 
      VALUES (new.rowid, new.ho_ten, new.ma_sinh_vien, new.email);
    END;

    -- Trigger FTS: DELETE
    CREATE TRIGGER IF NOT EXISTS sinh_vien_ad AFTER DELETE ON sinh_vien BEGIN
      INSERT INTO fts_sinh_vien(fts_sinh_vien, rowid, ho_ten, ma_sinh_vien, email) 
      VALUES('delete', old.rowid, old.ho_ten, old.ma_sinh_vien, old.email);
    END;

    -- Trigger FTS: UPDATE
    CREATE TRIGGER IF NOT EXISTS sinh_vien_au AFTER UPDATE ON sinh_vien BEGIN
      INSERT INTO fts_sinh_vien(fts_sinh_vien, rowid, ho_ten, ma_sinh_vien, email) 
      VALUES('delete', old.rowid, old.ho_ten, old.ma_sinh_vien, old.email);
      INSERT INTO fts_sinh_vien(rowid, ho_ten, ma_sinh_vien, email) 
      VALUES (new.rowid, new.ho_ten, new.ma_sinh_vien, new.email);
    END;
    """

    try:
        # Thực thi script tạo bảng
        cursor.executescript(schema_script)
        print("✅ Đã tạo bảng và cấu trúc cơ sở dữ liệu thành công.")
    except sqlite3.Error as e:
        print(f"❌ Lỗi khi tạo bảng: {e}")
        conn.close()
        return

    # ==========================================================================
    # 2. SEED DATA CỐ ĐỊNH (KHOA, THANG ĐIỂM, ADMIN)
    # ==========================================================================
    
    print("🌱 Đang khởi tạo dữ liệu mặc định...")

    # 2.1 Seed Khoa
    khoa_data = [
        ('SE', 'Công nghệ phần mềm'),
        ('CS', 'Khoa học máy tính'),
        ('IS', 'Hệ thống thông tin'),
        ('SEC', 'An toàn thông tin'),
        ('NET', 'Mạng máy tính và Truyền thông')
    ]
    cursor.executemany("INSERT OR IGNORE INTO khoa VALUES (?, ?)", khoa_data)

    # 2.2 Seed Thang điểm (Lấp đầy khoảng trống)
    thang_diem_data = [
        (8.5, 10.1, 'A', 4.0, 'Xuất sắc'),
        (7.0, 8.5,  'B', 3.0, 'Giỏi'),
        (5.5, 7.0,  'C', 2.0, 'Khá'),
        (4.0, 5.5,  'D', 1.0, 'Trung bình'),
        (0.0, 4.0,  'F', 0.0, 'Yếu')
    ]
    cursor.executemany("""
        INSERT OR IGNORE INTO thang_diem (diem_min, diem_max, diem_chu, diem_so, xep_loai) 
        VALUES (?, ?, ?, ?, ?)
    """, thang_diem_data)

    # 2.3 Seed Admin, GV
    admin_pass = get_admin_password_hash()
    cursor.execute("""
        INSERT OR IGNORE INTO nguoi_dung (ten_dang_nhap, mat_khau_hash, vai_tro) 
        VALUES (?, ?, ?)
    """, ('admin', admin_pass, 'admin'))
    gv_pass = get_gv_password_hash()
    cursor.execute("""
        INSERT OR IGNORE INTO nguoi_dung (ten_dang_nhap, mat_khau_hash, vai_tro) 
        VALUES (?, ?, ?)
    """, ('gv', gv_pass, 'giang_vien'))
    # Lưu thay đổi và đóng kết nối
    conn.commit()
    conn.close()
    
    print("✅ KHỞI TẠO HOÀN TẤT!")
    print(f"🔑 Tài khoản Admin mặc định: admin / 123456")
    print(f"🔑 Tài khoản Giảng viên mặc định: gv / 654321")

if __name__ == "__main__":
    if os.path.exists(DB_PATH):
        print(f"⚠️  Cảnh báo: File '{DB_PATH}' đã tồn tại.")
        print("❗ Bạn cần XÓA file database cũ để áp dụng cấu trúc Tiếng Việt có dấu mới.")

    run_migrations()

