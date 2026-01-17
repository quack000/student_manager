import ttkbootstrap as tb
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
from services.subject_service import SubjectService

class SubjectForm(tb.Toplevel):
    def __init__(self, parent, callback, user_data, subject_data=None): # Thêm user_data
        super().__init__(parent)
        self.title("Thông tin Môn học")
        self.geometry("500x550")
        self.resizable(False, False)
        
        self.callback = callback
        self.user_data = user_data # Lưu user_data
        self.subject_data = subject_data
        self.service = SubjectService()

        self.setup_ui()
        if self.subject_data:
            self.load_data()
            self.title("Cập nhật Môn học")
            self.entry_mamon.configure(state="disabled")

    def setup_ui(self):
        main = tb.Frame(self, padding=20)
        main.pack(fill=BOTH, expand=YES)

        group_info = tb.Labelframe(main, text="Thông tin chung", padding=10)
        group_info.pack(fill=X, pady=(0, 15))

        tb.Label(group_info, text="Mã môn (*):").pack(fill=X)
        self.entry_mamon = tb.Entry(group_info)
        self.entry_mamon.pack(fill=X, pady=(5, 10))

        tb.Label(group_info, text="Tên môn (*):").pack(fill=X)
        self.entry_tenmon = tb.Entry(group_info)
        self.entry_tenmon.pack(fill=X, pady=(5, 10))

        tb.Label(group_info, text="Số tín chỉ:").pack(fill=X)
        self.spin_tinchi = tb.Spinbox(group_info, from_=1, to=10, width=10)
        self.spin_tinchi.pack(anchor=W, pady=(5, 5))
        self.spin_tinchi.set(3)

        group_weight = tb.Labelframe(main, text="Cấu hình Trọng số (Tổng = 1.0)", padding=10, bootstyle="info")
        group_weight.pack(fill=X, pady=(0, 20))
        group_weight.columnconfigure(0, weight=1); group_weight.columnconfigure(1, weight=1); group_weight.columnconfigure(2, weight=1)

        tb.Label(group_weight, text="Quá trình (0.x)").grid(row=0, column=0, padx=5)
        self.spin_qt = tb.Spinbox(group_weight, from_=0.0, to=1.0, increment=0.1, format="%.1f")
        self.spin_qt.grid(row=1, column=0, padx=5, sticky=EW); self.spin_qt.set(0.1)

        tb.Label(group_weight, text="Giữa kỳ (0.x)").grid(row=0, column=1, padx=5)
        self.spin_gk = tb.Spinbox(group_weight, from_=0.0, to=1.0, increment=0.1, format="%.1f")
        self.spin_gk.grid(row=1, column=1, padx=5, sticky=EW); self.spin_gk.set(0.3)

        tb.Label(group_weight, text="Cuối kỳ (0.x)").grid(row=0, column=2, padx=5)
        self.spin_ck = tb.Spinbox(group_weight, from_=0.0, to=1.0, increment=0.1, format="%.1f")
        self.spin_ck.grid(row=1, column=2, padx=5, sticky=EW); self.spin_ck.set(0.6)

        tb.Button(main, text="LƯU DỮ LIỆU", bootstyle="success", command=self.on_save).pack(fill=X, ipady=5)

    def load_data(self):
        d = self.subject_data
        self.entry_mamon.insert(0, d['ma_mon'])
        self.entry_tenmon.insert(0, d['ten_mon'])
        self.spin_tinchi.set(d['so_tin_chi'])
        self.spin_qt.set(d['ty_le_qt'])
        self.spin_gk.set(d['ty_le_gk'])
        self.spin_ck.set(d['ty_le_ck'])

    def on_save(self):
        ma_mon = self.entry_mamon.get().strip()
        ten_mon = self.entry_tenmon.get().strip()
        try:
            tin_chi = int(self.spin_tinchi.get())
            qt = float(self.spin_qt.get())
            gk = float(self.spin_gk.get())
            ck = float(self.spin_ck.get())
        except ValueError: Messagebox.show_error("Vui lòng nhập số hợp lệ!", "Lỗi nhập liệu"); return

        if not ma_mon or not ten_mon: Messagebox.show_warning("Vui lòng nhập Mã môn và Tên môn", "Thiếu thông tin"); return

        data = {'ma_mon': ma_mon, 'ten_mon': ten_mon, 'so_tin_chi': tin_chi, 'ty_le_qt': qt, 'ty_le_gk': gk, 'ty_le_ck': ck}
        current_user = self.user_data.get('ten_dang_nhap', 'system') # Lấy username

        if self.subject_data:
            success, msg = self.service.update_subject(data, current_user)
        else:
            if self.service.check_exists(ma_mon): Messagebox.show_error("Mã môn đã tồn tại!", "Trùng lặp"); return
            success, msg = self.service.add_subject(data, current_user)

        if success: Messagebox.show_info(msg, "Thành công"); self.callback(); self.destroy()
        else: Messagebox.show_error(msg, "Lỗi")