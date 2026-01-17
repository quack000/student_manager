import pytest
import sqlite3
from unittest.mock import patch
from services.gpa_service import GPAService

TEST_DB = "test_student_manager.db"

def get_test_connection():
    conn = sqlite3.connect(TEST_DB)
    conn.row_factory = sqlite3.Row
    conn.create_function("no_accent", 1, lambda x: x)
    return conn

@pytest.fixture
def service(db_connection):
    with patch('services.gpa_service.get_connection', side_effect=get_test_connection):
        yield GPAService()

def test_calculate_cpa_simple(service, db_connection):
    db_connection.execute("INSERT INTO lop VALUES ('L1', '', 2023, '', '')")
    db_connection.execute("INSERT INTO sinh_vien (ma_sinh_vien, ho_ten, ngay_sinh, ma_lop) VALUES ('SV1', 'A', '2000', 'L1')")
    db_connection.execute("INSERT INTO mon_hoc VALUES ('M1', 'Mon 1', 3, 0,0,0)")
    db_connection.execute("INSERT INTO mon_hoc VALUES ('M2', 'Mon 2', 2, 0,0,0)")

    # M1: 4.0
    db_connection.execute("INSERT INTO dang_ky_hoc (ma_sinh_vien, ma_mon, hoc_ky) VALUES ('SV1', 'M1', 'HK1')")
    id1 = db_connection.execute("SELECT last_insert_rowid()").fetchone()[0]
    db_connection.execute("INSERT INTO diem (id_dang_ky, tong_diem_4) VALUES (?, 4.0)", (id1,))
    
    # M2: 3.0
    db_connection.execute("INSERT INTO dang_ky_hoc (ma_sinh_vien, ma_mon, hoc_ky) VALUES ('SV1', 'M2', 'HK1')")
    id2 = db_connection.execute("SELECT last_insert_rowid()").fetchone()[0]
    db_connection.execute("INSERT INTO diem (id_dang_ky, tong_diem_4) VALUES (?, 3.0)", (id2,))
    
    db_connection.commit()
    
    cpa, credits = service.calculate_cpa_and_credits('SV1')
    assert cpa == 3.6
    assert credits == 5

def test_calculate_cpa_retake(service, db_connection):
    db_connection.execute("INSERT INTO lop VALUES ('L1', '', 2023, '', '')")
    db_connection.execute("INSERT INTO sinh_vien (ma_sinh_vien, ho_ten, ngay_sinh, ma_lop) VALUES ('SV1', 'A', '2000', 'L1')")
    db_connection.execute("INSERT INTO mon_hoc VALUES ('M1', 'Mon 1', 3, 0,0,0)") # 3 TC

    # Lan 1: Rot (0.0)
    db_connection.execute("INSERT INTO dang_ky_hoc (ma_sinh_vien, ma_mon, hoc_ky) VALUES ('SV1', 'M1', 'HK1')")
    id1 = db_connection.execute("SELECT last_insert_rowid()").fetchone()[0]
    db_connection.execute("INSERT INTO diem (id_dang_ky, tong_diem_4) VALUES (?, 0.0)", (id1,))
    
    # Lan 2: Dau (3.0)
    db_connection.execute("INSERT INTO dang_ky_hoc (ma_sinh_vien, ma_mon, hoc_ky) VALUES ('SV1', 'M1', 'HK2')")
    id2 = db_connection.execute("SELECT last_insert_rowid()").fetchone()[0]
    db_connection.execute("INSERT INTO diem (id_dang_ky, tong_diem_4) VALUES (?, 3.0)", (id2,))
    
    db_connection.commit()

    cpa, credits = service.calculate_cpa_and_credits('SV1')
    assert cpa == 3.0
    assert credits == 3
