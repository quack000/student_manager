import pytest
import csv
import os
import sqlite3
from unittest.mock import patch
from services.grade_service import GradeService

TEST_DB = "test_student_manager.db"

def get_test_connection():
    conn = sqlite3.connect(TEST_DB)
    conn.row_factory = sqlite3.Row
    conn.create_function("no_accent", 1, lambda x: x)
    return conn

@pytest.fixture
def service(db_connection):
    with patch('services.grade_service.get_connection', side_effect=get_test_connection):
        yield GradeService()

def test_import_grades_success(service, db_connection):
    db_connection.execute("INSERT INTO lop VALUES ('SE1', 'Lop 1', 2023, '', '')")
    db_connection.execute("INSERT INTO mon_hoc (ma_mon, ten_mon, so_tin_chi, ty_le_qt, ty_le_gk, ty_le_ck) VALUES ('M1', 'Mon 1', 3, 0.2, 0.3, 0.5)")
    db_connection.execute("INSERT INTO sinh_vien (ma_sinh_vien, ho_ten, ngay_sinh, ma_lop) VALUES ('SV1', 'A', '2000', 'SE1')")
    db_connection.commit()
    
    csv_path = "temp_test_import.csv"
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['ma_sinh_vien', 'ma_mon', 'hoc_ky', 'diem_qt', 'diem_gk', 'diem_ck'])
        # 8*0.2 + 7*0.3 + 9*0.5 = 1.6 + 2.1 + 4.5 = 8.2 --> 3.0 (B)
        writer.writerow(['SV1', 'M1', 'HK1', '8.0', '7.0', '9.0'])
    
    try:
        success, msg = service.import_grades_from_csv(csv_path)
        assert success is True
        
        row = db_connection.execute("SELECT tong_diem_10, tong_diem_4 FROM diem").fetchone()
        assert row['tong_diem_10'] == 8.2
        assert row['tong_diem_4'] == 3.0
    finally:
        if os.path.exists(csv_path): os.remove(csv_path)

def test_update_grade(service, db_connection):
    db_connection.execute("INSERT INTO lop VALUES ('SE1', 'Lop 1', 2023, '', '')")
    db_connection.execute("INSERT INTO mon_hoc VALUES ('M1', 'Mon 1', 3, 0.2, 0.3, 0.5)")
    db_connection.execute("INSERT INTO sinh_vien (ma_sinh_vien, ho_ten, ngay_sinh, ma_lop) VALUES ('SV1', 'A', '2000', 'SE1')")
    db_connection.execute("INSERT INTO dang_ky_hoc (ma_sinh_vien, ma_mon, hoc_ky) VALUES ('SV1', 'M1', 'HK1')")
    id_dk = db_connection.execute("SELECT last_insert_rowid()").fetchone()[0]
    db_connection.execute("INSERT INTO diem (id_dang_ky, diem_qt, diem_gk, diem_ck) VALUES (?, 0, 0, 0)", (id_dk,))
    grade_id = db_connection.execute("SELECT last_insert_rowid()").fetchone()[0]
    db_connection.commit()
    
    success, msg = service.update_grade(grade_id, 10, 10, 10)
    assert success is True
    
    row = db_connection.execute("SELECT tong_diem_10, tong_diem_4 FROM diem WHERE id=?", (grade_id,)).fetchone()
    assert row['tong_diem_10'] == 10.0
    assert row['tong_diem_4'] == 4.0

def test_export_grades(service):
    csv_path = "temp_test_export.csv"
    try:
        success, msg = service.export_grades_to_csv(csv_path)
        assert success is True
        assert os.path.exists(csv_path)
    finally:
         if os.path.exists(csv_path): os.remove(csv_path)
