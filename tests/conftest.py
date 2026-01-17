import pytest
import os
import sqlite3

TEST_DB = "test_student_manager.db"

@pytest.fixture(scope="session")
def setup_database():
    """Khởi tạo cấu trúc DB test một lần duy nhất"""
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)
    
    conn = sqlite3.connect(TEST_DB)
    conn.row_factory = sqlite3.Row
    
    def remove_accents(text):
        return text
    conn.create_function("no_accent", 1, remove_accents)
    
    _create_tables(conn)
    conn.close()
    
    yield
    
    if os.path.exists(TEST_DB):
        try:
            os.remove(TEST_DB)
        except PermissionError:
            pass

@pytest.fixture
def db_connection(setup_database):
    """
    Fixture này cung cấp một connection mới cho mỗi test function.
    Nó cũng chịu trách nhiệm xóa dữ liệu (clean) trước khi test chạy.
    """
    # Clean data
    conn = sqlite3.connect(TEST_DB)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = OFF")
    conn.execute("DELETE FROM diem")
    conn.execute("DELETE FROM dang_ky_hoc")
    conn.execute("DELETE FROM sinh_vien")
    conn.execute("DELETE FROM lop")
    conn.execute("DELETE FROM mon_hoc")
    conn.execute("PRAGMA foreign_keys = ON")
    conn.commit()
    
    # Mock function lại cho connection này (vì mỗi conn mới phải reg lại function)
    conn.create_function("no_accent", 1, lambda x: x)
    
    yield conn
    conn.close()

def _create_tables(conn):
    cursor = conn.cursor()
    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS lop (
        ma_lop TEXT PRIMARY KEY,
        ten_lop TEXT NOT NULL,
        nam_nhap_hoc INTEGER NOT NULL,
        nganh_hoc TEXT,
        ma_gv_co_van TEXT
    );

    CREATE TABLE IF NOT EXISTS sinh_vien (
        ma_sinh_vien TEXT PRIMARY KEY,
        ho_ten TEXT NOT NULL,
        gioi_tinh TEXT,
        ngay_sinh TEXT NOT NULL,
        email TEXT UNIQUE,
        sdt TEXT,
        dia_chi TEXT,
        ma_lop TEXT NOT NULL,
        trang_thai TEXT DEFAULT 'Đang học',
        FOREIGN KEY(ma_lop) REFERENCES lop(ma_lop)
    );

    CREATE TABLE IF NOT EXISTS mon_hoc (
        ma_mon TEXT PRIMARY KEY,
        ten_mon TEXT NOT NULL,
        so_tin_chi INTEGER NOT NULL,
        ty_le_qt REAL DEFAULT 0.1,
        ty_le_gk REAL DEFAULT 0.3,
        ty_le_ck REAL DEFAULT 0.6
    );

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

    CREATE TABLE IF NOT EXISTS diem (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_dang_ky INTEGER UNIQUE NOT NULL,
        diem_qt REAL, diem_gk REAL, diem_ck REAL,
        tong_diem_10 REAL, tong_diem_4 REAL,
        ghi_chu TEXT,
        FOREIGN KEY(id_dang_ky) REFERENCES dang_ky_hoc(id) ON DELETE CASCADE
    );
                         
    CREATE TABLE IF NOT EXISTS thang_diem (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        diem_min REAL, diem_max REAL, diem_chu TEXT, diem_so REAL, xep_loai TEXT
    );
    
    INSERT INTO thang_diem (diem_min, diem_max, diem_chu, diem_so) VALUES 
    (8.5, 10.1, 'A', 4.0), (7.0, 8.5, 'B', 3.0), (5.5, 7.0, 'C', 2.0), (4.0, 5.5, 'D', 1.0), (0.0, 4.0, 'F', 0.0);
    """)
    conn.commit()
