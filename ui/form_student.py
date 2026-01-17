import ttkbootstrap as tb
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
from services.student_service import StudentService

class StudentForm(tb.Toplevel):
    def __init__(self, parent, callback, user_data, student_data=None): # Thêm user_data
        super().__init__(parent)
        self.title("Thông tin Sinh viên")
        self.geometry("500x650")
        self.resizable(False, False)
        
        self.callback = callback 
        self.user_data = user_data # Lưu thông tin user
        self.student_data = student_data 
        self.service = StudentService()
        self.class_list = self.service.get_all_classes()

        self.setup_ui()
        
        if self.student_data:
            self.load_data()
            self.title("Cập nhật Sinh viên")
        else:
            self.title("Thêm mới Sinh viên")

    def setup_ui(self):
        main_frame = tb.Frame(self, padding=20)
        main_frame.pack(fill=BOTH, expand=YES)

        # 1. Mã Sinh viên
        tb.Label(main_frame, text="Mã sinh viên (*):").pack(fill=X, pady=(0, 5))
        self.entry_msv = tb.Entry(main_frame)
        self.entry_msv.pack(fill=X, pady=(0, 10))

        # 2. Họ tên
        tb.Label(main_frame, text="Họ và tên (*):").pack(fill=X, pady=(0, 5))
        self.entry_name = tb.Entry(main_frame)
        self.entry_name.pack(fill=X, pady=(0, 10))

        # 3. Row: Lớp + Giới tính
        row1 = tb.Frame(main_frame)
        row1.pack(fill=X, pady=(0, 10))

        col_lop = tb.Frame(row1)
        col_lop.pack(side=LEFT, fill=X, expand=YES, padx=(0, 5))
        tb.Label(col_lop, text="Lớp (*):").pack(fill=X, pady=(0, 5))
        self.cbo_lop = tb.Combobox(col_lop, values=self.class_list, state="readonly")
        self.cbo_lop.pack(fill=X)
        self.cbo_lop.bind("<<ComboboxSelected>>", self.on_class_selected)

        col_gender = tb.Frame(row1)
        col_gender.pack(side=RIGHT, fill=X, expand=YES, padx=(5, 0))
        tb.Label(col_gender, text="Giới tính:").pack(fill=X, pady=(0, 5))
        self.cbo_gender = tb.Combobox(col_gender, values=["Nam", "Nu", "Khac"], state="readonly")
        self.cbo_gender.pack(fill=X)
        self.cbo_gender.current(0)

        # 4. Row: Ngày sinh + Trạng thái
        row2 = tb.Frame(main_frame)
        row2.pack(fill=X, pady=(0, 10))
        
        col_dob = tb.Frame(row2)
        col_dob.pack(side=LEFT, fill=X, expand=YES, padx=(0, 5))
        tb.Label(col_dob, text="Ngày sinh (YYYY-MM-DD) (*):").pack(fill=X, pady=(0, 5))
        self.entry_dob = tb.DateEntry(col_dob, bootstyle="primary", firstweekday=0)
        self.entry_dob.pack(fill=X)

        col_status = tb.Frame(row2)
        col_status.pack(side=RIGHT, fill=X, expand=YES, padx=(5, 0))
        tb.Label(col_status, text="Trạng thái:").pack(fill=X, pady=(0, 5))
        self.cbo_status = tb.Combobox(col_status, values=["Đang học", "Bảo lưu", "Thôi học", "Tốt nghiệp"], state="readonly")
        self.cbo_status.pack(fill=X)
        self.cbo_status.current(0)

        # 5. Email
        tb.Label(main_frame, text="Email (*):").pack(fill=X, pady=(0, 5))
        self.entry_email = tb.Entry(main_frame)
        self.entry_email.pack(fill=X, pady=(0, 10))

        # 6. SĐT & Địa chỉ
        tb.Label(main_frame, text="Số điện thoại:").pack(fill=X, pady=(0, 5))
        self.entry_sdt = tb.Entry(main_frame)
        self.entry_sdt.pack(fill=X, pady=(0, 10))

        tb.Label(main_frame, text="Địa chỉ:").pack(fill=X, pady=(0, 5))
        self.entry_address = tb.Entry(main_frame)
        self.entry_address.pack(fill=X, pady=(0, 20))

        btn_save = tb.Button(main_frame, text="LƯU DỮ LIỆU", bootstyle="success", command=self.on_save)
        btn_save.pack(fill=X, ipady=5)

    def on_class_selected(self, event):
        if not self.student_data:
            ma_lop = self.cbo_lop.get()
            if ma_lop:
                new_msv = self.service.generate_student_id(ma_lop)
                if new_msv:
                    self.entry_msv.delete(0, END)
                    self.entry_msv.insert(0, new_msv)
                    self.entry_email.delete(0, END)
                    self.entry_email.insert(0, f"{new_msv.lower()}@school.edu.vn")

    def load_data(self):
        data = self.student_data
        self.entry_msv.insert(0, data['ma_sinh_vien'])
        self.entry_msv.configure(state="disabled") 
        self.entry_name.insert(0, data['ho_ten'])
        self.cbo_lop.set(data['ma_lop'])
        self.cbo_lop.configure(state="disabled") 
        self.cbo_gender.set(data['gioi_tinh'])
        self.entry_dob.entry.delete(0, END)
        self.entry_dob.entry.insert(0, data['ngay_sinh'])
        self.cbo_status.set(data['trang_thai'])
        if data['email']: self.entry_email.insert(0, data['email'])
        if data.get('sdt'): self.entry_sdt.insert(0, data['sdt'])
        if data.get('dia_chi'): self.entry_address.insert(0, data['dia_chi'])

    def on_save(self):
        data = {
            'ma_sinh_vien': self.entry_msv.get().strip(),
            'ho_ten': self.entry_name.get().strip(),
            'ma_lop': self.cbo_lop.get(),
            'gioi_tinh': self.cbo_gender.get(),
            'ngay_sinh': self.entry_dob.entry.get(),
            'trang_thai': self.cbo_status.get(),
            'email': self.entry_email.get().strip(),
            'sdt': self.entry_sdt.get().strip(),
            'dia_chi': self.entry_address.get().strip()
        }

        if not data['ma_sinh_vien'] or not data['ho_ten'] or not data['ma_lop'] or not data['email']:
            Messagebox.show_warning("Vui lòng điền các trường bắt buộc (*)", title="Thiếu thông tin")
            return

        current_user = self.user_data.get('ten_dang_nhap', 'system') # Lấy username

        if self.student_data:
            success, msg = self.service.update_student(data, current_user)
        else:
            if self.service.check_exists(data['ma_sinh_vien']):
                Messagebox.show_error(f"Mã sinh viên {data['ma_sinh_vien']} đã tồn tại!", title="Trùng lặp")
                return
            success, msg = self.service.add_student(data, current_user)

        if success:
            Messagebox.show_info(msg, title="Thành công")
            self.callback()
            self.destroy()
        else:
            Messagebox.show_error(msg, title="Lỗi")