## Student Manager – Ứng dụng Quản lý Sinh viên

Ứng dụng desktop quản lý sinh viên được xây dựng bằng **Python**, sử dụng **SQLite** làm cơ sở dữ liệu và **Tkinter/ttkbootstrap** cho giao diện.

### 1. Yêu cầu hệ thống

Yêu cầu tối thiểu:
- **Python 3.10 trở lên** (khuyến nghị Python 3.10+)
- **Windows** (đã được kiểm thử trên Windows 10)

### 2. Cài đặt thư viện

Mở terminal/Command Prompt trong thư mục dự án và chạy lệnh sau:

```bash
pip install -r requirements.txt
```
hoặc
```bash
python -m pip install -r requirements.txt
```

**Lưu ý:** Các thư viện chuẩn như `sqlite3`, `hashlib`, `os`, `sys`, `tkinter`, `datetime`, `json`, `csv`, `re` đã được tích hợp sẵn trong Python, bạn không cần cài đặt thêm.

### 3. Cấu trúc dự án

```text
student_manager/
│
├── app.py                     # Điểm chạy chính của ứng dụng
├── run_tests.py               # Script hỗ trợ chạy kiểm thử
├── requirements.txt           # Danh sách thư viện cần cài đặt
├── README.md                  # Hướng dẫn sử dụng
├── student_manager.db         # File SQLite DB (có thể tạo lại)
├── TEST.csv                   # File CSV test (không bắt buộc)
├── bang_diem_export.csv       # File export điểm (không bắt buộc)
│
├── db/
│   └── connection.py         # Kết nối DB + hàm no_accent cho tìm kiếm không dấu
│
├── services/                  # Tầng nghiệp vụ (business logic)
│   ├── auth_service.py       # Đăng nhập, kiểm tra user, ghi log
│   ├── class_service.py      # Quản lý lớp học
│   ├── dashboard_service.py  # Thống kê tổng quan, dữ liệu biểu đồ
│   ├── gpa_service.py        # Tính GPA/CPA, xếp loại học lực
│   ├── grade_service.py      # Quản lý điểm, import/export CSV
│   ├── log_service.py        # Ghi và đọc nhật ký hệ thống
│   ├── student_service.py    # Quản lý sinh viên, tìm kiếm không dấu
│   └── subject_service.py    # Quản lý môn học
│
├── ui/                        # Giao diện người dùng (Tkinter + ttkbootstrap)
│   ├── class_view.py         # Màn hình danh sách lớp
│   ├── dashboard_view.py     # Màn hình Dashboard + biểu đồ
│   ├── form_class.py         # Form thêm/sửa lớp
│   ├── form_grade.py         # Form nhập/sửa điểm
│   ├── form_student.py       # Form thêm/sửa sinh viên
│   ├── form_subject.py       # Form thêm/sửa môn
│   ├── gpa_view.py           # Màn hình kết quả học tập (CPA/GPA)
│   ├── grade_view.py         # Màn hình bảng điểm + import/export CSV
│   ├── log_view.py           # Màn hình nhật ký hệ thống
│   ├── login_window.py       # Màn hình đăng nhập
│   ├── main_window.py        # Khung chính sau khi đăng nhập
│   ├── student_view.py       # Màn hình danh sách sinh viên
│   └── subject_view.py       # Màn hình danh sách môn học
│
├── tests/                     # Kiểm thử đơn vị cho các service
│   ├── __init__.py            # Đánh dấu package
│   ├── conftest.py            # Cấu hình Pytest và fixtures
│   ├── test_student_service.py  # Kiểm thử quản lý sinh viên
│   ├── test_grade_service.py    # Kiểm thử quản lý điểm số
│   └── test_gpa_service.py      # Kiểm thử tính toán GPA/CPA
│
└── db/                # Script tạo và seed database
    ├── migration.py           # Tạo schema bảng, trigger, FTS, tài khoản admin
    └── seed_data.py           # Sinh dữ liệu mẫu (khoa, GV, lớp, SV, điểm,…)
```

### 4. Khởi tạo cơ sở dữ liệu

Khi chạy ứng dụng lần đầu tiên (hoặc trên máy mới), bạn cần khởi tạo database. Chạy lần lượt hai lệnh sau:

```bash
python db/migration.py
python db/seed_data.py
```

Sau khi chạy xong, bạn sẽ có:
- Cấu trúc database đầy đủ với tất cả các bảng cần thiết
- Tài khoản admin mặc định: **admin / 123456**
- Tài khoản giảng viên mặc định: **gv / 654321**
- Dữ liệu mẫu bao gồm: khoa, giảng viên, lớp, sinh viên, môn học, điểm số, thang điểm

**Lưu ý:** Nếu bạn đã có file `student_manager.db` cũ nhưng gặp lỗi về cấu trúc (ví dụ: lỗi CHECK constraint, sai định dạng giới tính, trạng thái), hãy xóa file database cũ và chạy lại hai lệnh trên để tạo lại từ đầu.

### 5. Phân quyền
- Admin/Đào tạo: Toàn quyền (thêm, sửa, xóa, xem log).
- Giảng viên: Chỉ được xem dữ liệu và nhập điểm. Không được xóa sinh viên hay sửa cấu trúc lớp/môn.

### 6. Chạy ứng dụng

Để khởi động ứng dụng, mở terminal trong thư mục gốc của dự án và chạy:

```bash
python app.py
```


Sau khi đăng nhập thành công, bạn sẽ thấy giao diện chính với các chức năng:
- **Dashboard**: Xem thống kê tổng quan và biểu đồ
- **Sinh viên**: Quản lý thông tin sinh viên
- **Điểm số**: Nhập và quản lý điểm
- **Kết quả học tập**: Xem GPA/CPA và xếp loại
- **Lớp học**: Quản lý lớp
- **Môn học**: Quản lý môn học
- **Nhật ký hệ thống**: Xem log hoạt động (chỉ dành cho admin)

Bạn có thể thực hiện các thao tác: thêm, sửa, xóa dữ liệu; nhập/xuất điểm từ file CSV; xem các biểu đồ thống kê trực quan.

### 7. Chạy kiểm thử

Dự án có sẵn bộ kiểm thử đơn vị để kiểm tra các service chính. Các file test nằm trong thư mục `tests/`:
- `test_student_service.py` - Kiểm tra các chức năng quản lý sinh viên
- `test_grade_service.py` - Kiểm tra các chức năng quản lý điểm số
- `test_gpa_service.py` - Kiểm tra logic tính toán GPA/CPA

**Cách 1: Sử dụng script helper (Đơn giản nhất)**

Đây là cách dễ nhất để chạy tất cả các bài kiểm thử:

```bash
python run_tests.py
```

**Cách 2: Chạy bằng pytest trực tiếp**

Nếu bạn muốn có nhiều tùy chọn hơn:

```bash
# Chạy tất cả các test
pytest tests/ -v

# Chạy test cho một service cụ thể
pytest tests/test_student_service.py -v

# Chạy một test case cụ thể
pytest tests/test_student_service.py::test_add_student_success -v
```

**Cách 3: Chạy qua Python module**

```bash
python -m pytest tests/ -v
```

**Lưu ý quan trọng:**
- Cần cài đặt `pytest` trước: `pip install pytest` hoặc `pip install -r requirements.txt`
- Bài kiểm thử sẽ tự động tạo một database test riêng (`test_student_manager.db`) và tự động dọn dẹp sau khi hoàn thành
- Database chính (`student_manager.db`) sẽ không bị ảnh hưởng
- File `test_student_manager.db` có thể xuất hiện tạm thời trong thư mục gốc khi chạy test, nhưng sẽ được xóa tự động

### 8. Thư viện phụ thuộc

**Thư viện bên ngoài (cần cài đặt qua pip):**

- **ttkbootstrap** (>=1.10.0) - Framework GUI hiện đại, cung cấp các widget và theme đẹp mắt cho Tkinter
- **matplotlib** (>=3.7.0) - Thư viện vẽ biểu đồ, được sử dụng trong phần Dashboard để hiển thị thống kê
- **pytest** (>=7.4.0) - Framework kiểm thử, chỉ cần khi bạn muốn chạy các test case (tùy chọn)

**Thư viện chuẩn Python (không cần cài đặt):**

Các thư viện sau đã được tích hợp sẵn trong Python, bạn không cần cài đặt thêm:
- `sqlite3` - Làm việc với database SQLite
- `hashlib` - Mã hóa mật khẩu (SHA256)
- `os`, `sys` - Thao tác với hệ thống file và môi trường
- `tkinter` - Framework GUI cơ bản (có sẵn trong Python)
- `datetime`, `json`, `csv`, `re` - Xử lý dữ liệu và định dạng

