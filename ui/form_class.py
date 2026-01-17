import ttkbootstrap as tb
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
from services.class_service import ClassService
import datetime

class ClassForm(tb.Toplevel):
    def __init__(self, parent, callback, user_data, class_data=None):
        super().__init__(parent)
        self.title("Thông tin Lớp học")
        self.geometry("500x550")
        self.resizable(False, False)
        
        self.callback = callback
        self.user_data = user_data # Lưu thông tin người dùng
        self.class_data = class_data
        self.service = ClassService()
        
        # Data Loading
        self.lecturers = self.service.get_lecturers()
        self.majors = self.service.get_majors()
        
        # Format options
        self.lecturer_options = [f"{gv['ma_gv']} - {gv['ho_ten']}" for gv in self.lecturers]
        self.lecturer_options.insert(0, "--- Chọn CVHT ---")
        
        self.major_options = [f"{m['ma_khoa']} - {m['ten_khoa']}" for m in self.majors]
        if not self.major_options:
             self.major_options = ["SE - Công nghệ phần mềm", "CS - Khoa học máy tính"]

        self.setup_ui()
        if self.class_data:
            self.load_data()
            self.title("Cập nhật Lớp học")
            self.entry_malop.configure(state="disabled")
        else:
            self.on_auto_fill()

    def setup_ui(self):
        main = tb.Frame(self, padding=20)
        main.pack(fill=BOTH, expand=YES)

        # 1. Row: Năm nhập học & Ngành
        row1 = tb.Labelframe(main, text="Thông tin Khóa học", padding=10)
        row1.pack(fill=X, pady=(0, 15))
        
        # Năm
        col1 = tb.Frame(row1)
        col1.pack(side=LEFT, fill=X, expand=YES, padx=(0, 5))
        tb.Label(col1, text="Năm nhập học:").pack(fill=X)
        
        current_year = datetime.datetime.now().year
        self.spin_nam = tb.Spinbox(col1, from_=2015, to=2030, command=self.on_auto_fill)
        self.spin_nam.pack(fill=X)
        self.spin_nam.set(current_year)
        self.spin_nam.bind("<FocusOut>", lambda e: self.on_auto_fill())
        self.spin_nam.bind("<Return>", lambda e: self.on_auto_fill())

        # Ngành
        col2 = tb.Frame(row1)
        col2.pack(side=RIGHT, fill=X, expand=YES, padx=(5, 0))
        tb.Label(col2, text="Ngành học:").pack(fill=X)
        self.cbo_nganh = tb.Combobox(col2, values=self.major_options, state="readonly")
        self.cbo_nganh.pack(fill=X)
        self.cbo_nganh.current(0)
        self.cbo_nganh.bind("<<ComboboxSelected>>", lambda e: self.on_auto_fill())

        # 2. Mã lớp & Tên lớp
        tb.Label(main, text="Mã lớp (*):").pack(fill=X, pady=(0, 5))
        self.entry_malop = tb.Entry(main)
        self.entry_malop.pack(fill=X, pady=(0, 15))

        tb.Label(main, text="Tên lớp (*):").pack(fill=X, pady=(0, 5))
        self.entry_tenlop = tb.Entry(main)
        self.entry_tenlop.pack(fill=X, pady=(0, 15))

        # 3. Cố vấn học tập
        tb.Label(main, text="Cố vấn học tập:").pack(fill=X, pady=(0, 5))
        self.cbo_cvht = tb.Combobox(main, values=self.lecturer_options, state="readonly")
        self.cbo_cvht.pack(fill=X, pady=(0, 20))
        self.cbo_cvht.current(0)

        # Button
        tb.Button(main, text="LƯU DỮ LIỆU", bootstyle="success", command=self.on_save).pack(fill=X, ipady=5)

    def on_auto_fill(self):
        if self.class_data: return

        try:
            nam = int(self.spin_nam.get())
        except:
            return

        nganh_str = self.cbo_nganh.get()
        if not nganh_str: return
        
        ma_khoa = nganh_str.split(" - ")[0]
        ma_lop_new, ten_lop_new = self.service.suggest_class_info(ma_khoa, nam)
        
        if ma_lop_new and ten_lop_new:
            self.entry_malop.delete(0, END)
            self.entry_malop.insert(0, ma_lop_new)
            
            self.entry_tenlop.delete(0, END)
            self.entry_tenlop.insert(0, ten_lop_new)

    def load_data(self):
        d = self.class_data
        self.entry_malop.insert(0, d['ma_lop'])
        self.entry_tenlop.insert(0, d['ten_lop'])
        self.spin_nam.set(d['nam_nhap_hoc'])
        
        ma_nganh = d['nganh_hoc']
        for opt in self.major_options:
            if opt.startswith(ma_nganh):
                self.cbo_nganh.set(opt)
                break
        
        if d['ma_gv_co_van']:
            for option in self.lecturer_options:
                if option.startswith(d['ma_gv_co_van']):
                    self.cbo_cvht.set(option)
                    break

    def on_save(self):
        ma_lop = self.entry_malop.get().strip()
        ten_lop = self.entry_tenlop.get().strip()
        nam = self.spin_nam.get()
        
        nganh_str = self.cbo_nganh.get()
        nganh = nganh_str.split(" - ")[0] if nganh_str else ""
        
        cvht_str = self.cbo_cvht.get()
        ma_gv = cvht_str.split(" - ")[0] if cvht_str and "---" not in cvht_str else None

        if not ma_lop or not ten_lop:
            Messagebox.show_warning("Vui lòng nhập Mã lớp và Tên lớp", "Thiếu thông tin")
            return

        data = {
            'ma_lop': ma_lop,
            'ten_lop': ten_lop,
            'nam_nhap_hoc': nam,
            'nganh_hoc': nganh,
            'ma_gv_co_van': ma_gv
        }

        # Lấy username hiện tại để ghi log
        current_user = self.user_data.get('ten_dang_nhap', 'system')

        if self.class_data:
            success, msg = self.service.update_class(data, current_user)
        else:
            if self.service.check_exists(ma_lop):
                Messagebox.show_error("Mã lớp đã tồn tại!", "Trùng lặp")
                return
            success, msg = self.service.add_class(data, current_user)

        if success:
            Messagebox.show_info(msg, "Thành công")
            self.callback()
            self.destroy()
        else:
            Messagebox.show_error(msg, "Lỗi")