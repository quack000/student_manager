import ttkbootstrap as tb
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
from services.grade_service import GradeService

class GradeForm(tb.Toplevel):
    def __init__(self, parent, callback, user_data, grade_data): # Thêm user_data
        super().__init__(parent)
        self.title("Cập nhật Điểm số")
        self.geometry("400x450")
        self.resizable(False, False)
        
        self.callback = callback
        self.user_data = user_data # Lưu user_data
        self.grade_data = grade_data
        self.service = GradeService()

        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        main = tb.Frame(self, padding=20)
        main.pack(fill=BOTH, expand=YES)
        
        info_frame = tb.Labelframe(main, text="Thông tin", padding=10)
        info_frame.pack(fill=X, pady=(0, 20))
        self.lbl_info = tb.Label(info_frame, text="", font=("Helvetica", 10))
        self.lbl_info.pack(anchor=W)

        input_frame = tb.Frame(main); input_frame.pack(fill=X)
        tb.Label(input_frame, text="Điểm Quá trình:").grid(row=0, column=0, pady=5, sticky=W)
        self.entry_qt = tb.Spinbox(input_frame, from_=0, to=10, increment=0.1, format="%.1f")
        self.entry_qt.grid(row=0, column=1, pady=5, padx=10, sticky=EW)

        tb.Label(input_frame, text="Điểm Giữa kỳ:").grid(row=1, column=0, pady=5, sticky=W)
        self.entry_gk = tb.Spinbox(input_frame, from_=0, to=10, increment=0.1, format="%.1f")
        self.entry_gk.grid(row=1, column=1, pady=5, padx=10, sticky=EW)

        tb.Label(input_frame, text="Điểm Cuối kỳ:").grid(row=2, column=0, pady=5, sticky=W)
        self.entry_ck = tb.Spinbox(input_frame, from_=0, to=10, increment=0.1, format="%.1f")
        self.entry_ck.grid(row=2, column=1, pady=5, padx=10, sticky=EW)
        input_frame.columnconfigure(1, weight=1)

        btn_save = tb.Button(main, text="LƯU ĐIỂM", bootstyle="success", command=self.on_save)
        btn_save.pack(fill=X, pady=20, ipady=5)
        tb.Label(main, text="* Điểm tổng kết sẽ được tự động tính lại", font=("Arial", 8, "italic"), foreground="gray").pack()

    def load_data(self):
        d = self.grade_data
        info_text = f"SV: {d['ho_ten']} ({d['ma_sinh_vien']})\nMôn: {d['ten_mon']}\nHọc kỳ: {d['hoc_ky']}"
        self.lbl_info.config(text=info_text)
        self.entry_qt.set(d['diem_qt'])
        self.entry_gk.set(d['diem_gk'])
        self.entry_ck.set(d['diem_ck'])

    def on_save(self):
        try:
            qt = float(self.entry_qt.get())
            gk = float(self.entry_gk.get())
            ck = float(self.entry_ck.get())
            if not (0 <= qt <= 10 and 0 <= gk <= 10 and 0 <= ck <= 10): Messagebox.show_error("Điểm phải nằm trong khoảng 0 - 10", "Dữ liệu không hợp lệ"); return
                
            current_user = self.user_data.get('ten_dang_nhap', 'system') # Lấy username
            success, msg = self.service.update_grade(self.grade_data['id'], qt, gk, ck, current_user)
            
            if success: Messagebox.show_info(msg, "Thành công"); self.callback(); self.destroy()
            else: Messagebox.show_error(msg, "Lỗi")
        except ValueError: Messagebox.show_error("Vui lòng nhập số hợp lệ", "Lỗi nhập liệu")