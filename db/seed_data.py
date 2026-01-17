import sqlite3
import random
import datetime
import hashlib
import os

# Cấu hình đường dẫn DB (Sửa lại cho đúng với máy của bạn)
DB_PATH = "student_manager.db"

# ==============================================================================
# 1. DỮ LIỆU MẪU (MASTER DATA)
# ==============================================================================

# Danh sách Họ phổ biến
HO_LIST = ['Nguyễn', 'Trần', 'Lê', 'Phạm', 'Hoàng', 'Huỳnh', 'Phan', 'Vũ', 'Võ', 'Đặng', 'Bùi', 'Đỗ', 'Hồ', 'Ngô', 'Dương', 'Lý']

# Danh sách Tên đệm
DEM_NAM = ['Văn', 'Hữu', 'Đức', 'Thành', 'Công', 'Minh', 'Quang', 'Thế', 'Tuấn', 'Duy', 'Gia', 'Nhật', 'Đình', 'Xuân', 'Trọng']
DEM_NU = ['Thị', 'Ngọc', 'Thu', 'Mai', 'Thanh', 'Khánh', 'Hồng', 'Thùy', 'Kim', 'Phương', 'Bảo', 'Mỹ', 'Ánh', 'Diệu']

# Danh sách Tên
TEN_NAM = ['Huy', 'Hoàng', 'Hiếu', 'Dũng', 'Anh', 'Bảo', 'Tùng', 'Nam', 'Quân', 'Thắng', 'Thịnh', 'Khoa', 'Long', 'Hải', 'Hùng', 'Cường', 'Phúc', 'Việt', 'Bách', 'Khang', 'Kiên', 'Lâm']
TEN_NU = ['Linh', 'Trang', 'Hương', 'Huyền', 'Tâm', 'Hằng', 'Giang', 'Dương', 'Quỳnh', 'Thảo', 'Vân', 'Lan', 'Hoa', 'Anh', 'Chi', 'Ngân', 'Uyên', 'Phương', 'Nhi', 'Yến']

# CẬP NHẬT: Danh sách các Thành phố tại Việt Nam
DIA_CHI_LIST = [
    'Hà Nội', 'TP. Hồ Chí Minh', 'Đà Nẵng', 'Hải Phòng', 'Cần Thơ', 
    'TP. Vinh', 'TP. Huế', 'TP. Nha Trang', 'TP. Đà Lạt', 'TP. Buôn Ma Thuột',
    'TP. Quy Nhơn', 'TP. Vũng Tàu', 'TP. Hạ Long', 'TP. Việt Trì', 'TP. Thái Nguyên',
    'TP. Nam Định', 'TP. Thanh Hóa', 'TP. Phan Thiết', 'TP. Biên Hòa', 'TP. Mỹ Tho',
    'TP. Long Xuyên', 'TP. Rạch Giá', 'TP. Cà Mau', 'TP. Pleiku', 'TP. Tuy Hòa'
]

MON_HOC_DATA = [
    ('INT1001', 'Nhập môn CNTT', 3), ('MAT1010', 'Giải tích 1', 3), ('MAT1020', 'Đại số tuyến tính', 3),
    ('INT1002', 'Tin học cơ sở 1', 4), ('INT1006', 'Kỹ thuật lập trình', 3), ('INT2001', 'Cấu trúc dữ liệu & GT', 3),
    ('INT2002', 'Cơ sở dữ liệu', 3), ('INT2003', 'Mạng máy tính', 3), ('INT2005', 'Hệ điều hành', 3),
    ('SE3001', 'Phân tích thiết kế hệ thống', 3), ('SE3002', 'Công nghệ Java', 3), ('SE3003', 'Kiểm thử phần mềm', 3),
    ('CS3001', 'Trí tuệ nhân tạo', 3), ('CS3002', 'Học máy', 3), ('CS4001', 'Khai phá dữ liệu', 3),
    ('SEC3001', 'Mật mã học', 3), ('SEC3002', 'An toàn mạng', 3),
]

NGANH_MAP = {'SE': 'KTPM', 'CS': 'KHMT', 'IS': 'HTTT', 'SEC': 'ATTT', 'NET': 'MMT'}
KHOA_LIST = ['SE', 'CS', 'IS', 'SEC', 'NET']
HOC_VI_LIST = ['ThS', 'TS', 'PGS', 'GS']

# ==============================================================================
# 2. HÀM TIỆN ÍCH
# ==============================================================================

def get_hash_password(password='123456'):
    return hashlib.sha256(password.encode()).hexdigest()

def get_random_name():
    ho = random.choice(HO_LIST)
    if random.random() > 0.5: # 50% Nam
        dem = random.choice(DEM_NAM)
        ten = random.choice(TEN_NAM)
        gioi_tinh = 'Nam'
    else: # 50% Nữ
        dem = random.choice(DEM_NU)
        ten = random.choice(TEN_NU)
        gioi_tinh = 'Nữ' 
    
    full_name = f"{ho} {dem} {ten}"
    return full_name, gioi_tinh

def generate_dob(year_start=2000, year_end=2004):
    start = datetime.date(year_start, 1, 1)
    end = datetime.date(year_end, 12, 31)
    random_days = random.randint(0, (end - start).days)
    dob = start + datetime.timedelta(days=random_days)
    return dob.isoformat()

def generate_phone():
    """Tạo số điện thoại ngẫu nhiên (Việt Nam)"""
    prefixes = ['09', '03', '07', '08', '05']
    prefix = random.choice(prefixes)
    suffix = ''.join([str(random.randint(0, 9)) for _ in range(8)])
    return f"{prefix}{suffix}"

def calculate_grade_components(target_total_10):
    qt = min(10, max(0, target_total_10 + random.uniform(-1, 1)))
    gk = min(10, max(0, target_total_10 + random.uniform(-1.5, 1.5)))
    ck_needed = (target_total_10 - 0.1*qt - 0.3*gk) / 0.6
    ck = min(10, max(0, ck_needed))
    return round(qt, 1), round(gk, 1), round(ck, 1)

def get_grade_4(score_10):
    if score_10 >= 8.5: return 4.0
    elif score_10 >= 7.0: return 3.0
    elif score_10 >= 5.5: return 2.0
    elif score_10 >= 4.0: return 1.0
    else: return 0.0

# ==============================================================================
# 3. HÀM SEED CHÍNH
# ==============================================================================

def seed_database():
    print(f"Connecting to {DB_PATH}...")
    if not os.path.exists(DB_PATH):
        print("❌ Lỗi: Không tìm thấy file database. Hãy chạy migration.py trước!")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    # 1. SEED GIẢNG VIÊN & TÀI KHOẢN (USER)
    print("Seeding Giảng viên & Tài khoản...")
    lecturers = [] 
    lecturers_by_khoa = {k: [] for k in KHOA_LIST} 
    default_pass = get_hash_password('123456')

    for ma_khoa in KHOA_LIST:
        for i in range(1, 6):
            ma_gv = f"GV{ma_khoa}{i:02d}"
            ho_ten, gioi = get_random_name()
            email = f"{ma_gv.lower()}@school.edu.vn"
            hoc_vi = random.choice(HOC_VI_LIST)
            dob = generate_dob(1975, 1990)
            
            try:
                cursor.execute("""
                    INSERT INTO giang_vien (ma_gv, ho_ten, ngay_sinh, email, hoc_vi, ma_khoa)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (ma_gv, ho_ten, dob, email, hoc_vi, ma_khoa))
                
                cursor.execute("""
                    INSERT INTO nguoi_dung (ten_dang_nhap, mat_khau_hash, vai_tro, ma_gv)
                    VALUES (?, ?, ?, ?)
                """, (ma_gv, default_pass, 'giang_vien', ma_gv))
                
                lecturers.append(ma_gv)
                lecturers_by_khoa[ma_khoa].append(ma_gv)
            except sqlite3.IntegrityError:
                lecturers.append(ma_gv) 
                lecturers_by_khoa[ma_khoa].append(ma_gv)

    # 2. SEED MÔN HỌC
    print("Seeding Môn học...")
    for mh in MON_HOC_DATA:
        try:
            cursor.execute("INSERT INTO mon_hoc (ma_mon, ten_mon, so_tin_chi) VALUES (?, ?, ?)", mh)
        except sqlite3.IntegrityError:
            pass 

    # 3. SEED LỚP HỌC
    print("Seeding Lớp học...")
    classes = [] 
    years = [2020, 2021, 2022, 2023]
    
    for code, name_prefix in NGANH_MAP.items():
        for year in years:
            khoa_so = year - 2006
            ma_lop = f"{name_prefix}{khoa_so:02d}"
            ten_lop = f"Lớp {name_prefix} - Khóa {khoa_so}"
            
            potential_advisors = lecturers_by_khoa.get(code, [])
            ma_gv_cvht = random.choice(potential_advisors) if potential_advisors else None
            
            try:
                cursor.execute("""
                    INSERT INTO lop (ma_lop, ten_lop, nam_nhap_hoc, nganh_hoc, ma_gv_co_van) 
                    VALUES (?, ?, ?, ?, ?)
                """, (ma_lop, ten_lop, year, code, ma_gv_cvht))
                classes.append(ma_lop)
            except sqlite3.IntegrityError:
                classes.append(ma_lop)

    # 4. SEED SINH VIÊN
    print("Seeding Sinh viên & Điểm số...")
    student_count = 0
    error_count = 0
    last_error_msg = ""
    
    for ma_lop in classes:
        for i in range(1, 31): 
            hoten, gioi_tinh = get_random_name()
            dob = generate_dob(2000, 2005)
            msv = f"{ma_lop}{i:03d}"
            email = f"{msv.lower()}@school.edu.vn"
            
            # Random địa chỉ từ danh sách Thành phố
            dia_chi = random.choice(DIA_CHI_LIST)
            sdt = generate_phone()
            
            try:
                cursor.execute("""
                    INSERT INTO sinh_vien (ma_sinh_vien, ho_ten, gioi_tinh, ngay_sinh, email, sdt, dia_chi, ma_lop, trang_thai)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (msv, hoten, gioi_tinh, dob, email, sdt, dia_chi, ma_lop, 'Đang học'))
                student_count += 1
                
                # Điểm số
                num_subjects = random.randint(5, 10)
                selected_subjects = random.sample(MON_HOC_DATA, num_subjects)
                
                for sub in selected_subjects:
                    ma_mon = sub[0]
                    hoc_ky = f"202{random.randint(0,3)}_{random.randint(1,2)}"
                    
                    target_score = random.gauss(7.0, 1.5)
                    target_score = max(0, min(10, target_score))
                    
                    qt, gk, ck = calculate_grade_components(target_score)
                    tong_10 = qt*0.1 + gk*0.3 + ck*0.6
                    tong_4 = get_grade_4(tong_10)
                    
                    try:
                        cursor.execute("INSERT INTO dang_ky_hoc (ma_sinh_vien, ma_mon, hoc_ky) VALUES (?, ?, ?)", (msv, ma_mon, hoc_ky))
                        id_dang_ky = cursor.lastrowid
                        cursor.execute("INSERT INTO diem (id_dang_ky, diem_qt, diem_gk, diem_ck, tong_diem_10, tong_diem_4) VALUES (?, ?, ?, ?, ?, ?)", (id_dang_ky, qt, gk, ck, round(tong_10, 2), tong_4))
                    except sqlite3.IntegrityError:
                        pass
            except sqlite3.IntegrityError as e:
                error_count += 1
                last_error_msg = str(e)
                pass

    conn.commit()
    conn.close()
    print(f"=== HOÀN TẤT ===")
    print(f"Đã tạo {len(lecturers)} giảng viên.")
    print(f"Đã tạo {len(classes)} lớp học.")
    print(f"Đã tạo {student_count} sinh viên (địa chỉ là các Thành phố).")
    
    if student_count == 0 and error_count > 0:
        print(f"\n⚠️ CẢNH BÁO QUAN TRỌNG: Không tạo được sinh viên nào!")
        print(f"❌ Nguyên nhân: {last_error_msg}")
        print("💡 GỢI Ý KHẮC PHỤC: Dữ liệu 'Nữ'/'Đang học' có thể không khớp với cấu trúc Database cũ.")
        print("👉 Hãy XÓA file 'student_manager.db' và chạy lại 'migration.py' để cập nhật cấu trúc mới.")

if __name__ == "__main__":
    seed_database()