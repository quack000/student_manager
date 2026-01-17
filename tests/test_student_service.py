import pytest
import sqlite3
from unittest.mock import patch
from services.student_service import StudentService

TEST_DB = "test_student_manager.db"

def get_test_connection():
    conn = sqlite3.connect(TEST_DB)
    conn.row_factory = sqlite3.Row
    conn.create_function("no_accent", 1, lambda x: x)
    return conn

@pytest.fixture
def service(db_connection):
    with patch('services.student_service.get_connection', side_effect=get_test_connection):
        yield StudentService()

def test_add_student_success(service, db_connection):
    db_connection.execute("INSERT INTO lop VALUES ('SE101', 'Kỹ thuật PM', 2023, 'SE', NULL)")
    db_connection.commit()
    
    data = {
        'ma_sinh_vien': 'SE101001',
        'ho_ten': 'Nguyễn Văn A',
        'gioi_tinh': 'Nam',
        'ngay_sinh': '2000-01-01',
        'ma_lop': 'SE101',
        'email': 'a@test.com',
        'trang_thai': 'Đang học'
    }
    
    success, msg = service.add_student(data)
    assert success is True
    
    row = db_connection.execute("SELECT * FROM sinh_vien WHERE ma_sinh_vien='SE101001'").fetchone()
    assert row is not None

def test_add_student_duplicate(service, db_connection):
    db_connection.execute("INSERT INTO lop VALUES ('SE101', 'Kỹ thuật PM', 2023, 'SE', NULL)")
    data = {
        'ma_sinh_vien': 'SE101001', 'ho_ten': 'A', 'gioi_tinh': 'Nam', 
        'ngay_sinh': '2000', 'ma_lop': 'SE101', 'email': 'a@test.com', 'trang_thai': 'Đang học'
    }
    service.add_student(data)
    
    # Thêm lần 2
    success, msg = service.add_student(data)
    assert success is False

def test_update_student(service, db_connection):
    db_connection.execute("INSERT INTO lop VALUES ('SE101', 'Test', 2023, 'SE', NULL)")
    db_connection.execute("INSERT INTO sinh_vien (ma_sinh_vien, ho_ten, ngay_sinh, ma_lop, trang_thai) VALUES ('SV01', 'Old Name', '2000', 'SE101', 'Đang học')")
    db_connection.commit()
    
    update_data = {
        'ma_sinh_vien': 'SV01',
        'ho_ten': 'New Name',
        'gioi_tinh': 'Nữ',
        'ngay_sinh': '2000-01-01',
        'ma_lop': 'SE101', 
        'email': 'new@mail.com',
        'trang_thai': 'Bảo lưu'
    }
    
    success, msg = service.update_student(update_data)
    assert success is True
    
    row = db_connection.execute("SELECT ho_ten, trang_thai FROM sinh_vien WHERE ma_sinh_vien='SV01'").fetchone()
    assert row['ho_ten'] == 'New Name'
    assert row['trang_thai'] == 'Bảo lưu'

def test_delete_student_success(service, db_connection):
    db_connection.execute("INSERT INTO lop VALUES ('SE101', 'Test', 2023, 'SE', NULL)")
    db_connection.execute("INSERT INTO sinh_vien (ma_sinh_vien, ho_ten, ngay_sinh, ma_lop) VALUES ('SV02', 'To Delete', '2000', 'SE101')")
    db_connection.commit()
    
    success, msg = service.delete_student('SV02', user_role='admin')
    assert success is True
    
    assert db_connection.execute("SELECT count(*) FROM sinh_vien WHERE ma_sinh_vien='SV02'").fetchone()[0] == 0

def test_delete_student_permission_denied(service):
    success, msg = service.delete_student('SV02', user_role='giang_vien')
    assert success is False
    assert "không có quyền" in msg

def test_generate_student_id(service, db_connection):
    db_connection.execute("INSERT INTO lop VALUES ('L01', 'Lop 1', 2023, '', '')")
    db_connection.commit()

    new_id = service.generate_student_id('L01')
    assert new_id == "L01001"
    
    db_connection.execute("INSERT INTO sinh_vien (ma_sinh_vien, ho_ten, ngay_sinh, ma_lop) VALUES ('L01005', 'A', '2000', 'L01')")
    db_connection.commit()
    
    new_id_2 = service.generate_student_id('L01')
    assert new_id_2 == "L01006"

def test_get_students_filter(service, db_connection):
    db_connection.execute("INSERT INTO lop VALUES ('L01', 'Lop 1', 2023, '', '')")
    db_connection.execute("INSERT INTO sinh_vien (ma_sinh_vien, ho_ten, ngay_sinh, ma_lop, trang_thai) VALUES ('SV01', 'A', '2000', 'L01', 'Đang học')")
    db_connection.execute("INSERT INTO sinh_vien (ma_sinh_vien, ho_ten, ngay_sinh, ma_lop, trang_thai) VALUES ('SV02', 'B', '2000', 'L01', 'Bảo lưu')")
    db_connection.commit()
    
    # Lọc theo trạng thái
    students, count = service.get_students(status_filter='Đang học')
    assert count == 1
    assert students[0]['ma_sinh_vien'] == 'SV01'
    
    # Lọc theo tên
    students, count = service.get_students(search_text='B')
    assert count == 1
    assert students[0]['ma_sinh_vien'] == 'SV02'
