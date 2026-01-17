import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import messagebox
from services.student_service import StudentService
from ui.form_student import StudentForm

class StudentView(tb.Frame):
    def __init__(self, parent, user_data=None):
        super().__init__(parent)
        self.service = StudentService()
        self.user_data = user_data
        
        self.current_page = 1
        self.page_size = 40
        self.total_records = 0
        self.class_list = ["Tất cả"] + self.service.get_all_classes()
        
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        toolbar = tb.Frame(self, padding=10)
        toolbar.pack(fill=X)

        filter_group = tb.Labelframe(toolbar, text="Bộ lọc & Tìm kiếm", padding=5)
        filter_group.pack(side=LEFT, fill=Y, padx=5)

        self.search_var = tb.StringVar()
        entry_search = tb.Entry(filter_group, textvariable=self.search_var, width=20)
        entry_search.pack(side=LEFT, padx=5)
        entry_search.bind("<Return>", lambda e: self.on_search())
        
        tb.Label(filter_group, text="Lớp:").pack(side=LEFT, padx=(10, 2))
        self.cbo_filter_class = tb.Combobox(filter_group, values=self.class_list, state="readonly", width=10)
        self.cbo_filter_class.pack(side=LEFT, padx=2)
        self.cbo_filter_class.current(0)
        self.cbo_filter_class.bind("<<ComboboxSelected>>", lambda e: self.on_search())

        tb.Label(filter_group, text="Trạng thái:").pack(side=LEFT, padx=(10, 2))
        self.cbo_filter_status = tb.Combobox(filter_group, values=["Tất cả", "Đang học", "Bảo lưu", "Thôi học", "Tốt nghiệp"], state="readonly", width=12)
        self.cbo_filter_status.pack(side=LEFT, padx=2)
        self.cbo_filter_status.current(0)
        self.cbo_filter_status.bind("<<ComboboxSelected>>", lambda e: self.on_search())

        tb.Button(filter_group, text="🔍", bootstyle="secondary", command=self.on_search).pack(side=LEFT, padx=5)

        btn_group = tb.Frame(toolbar)
        btn_group.pack(side=RIGHT, fill=Y)

        tb.Button(btn_group, text="+ Thêm", bootstyle="success", command=self.on_add).pack(side=LEFT, padx=2)
        tb.Button(btn_group, text="✏️ Sửa", bootstyle="warning", command=self.on_edit).pack(side=LEFT, padx=2)
        tb.Button(btn_group, text="🗑️ Xóa", bootstyle="danger", command=self.on_delete).pack(side=LEFT, padx=2)

        self.columns = [
            {"text": "Mã SV", "width": 90},
            {"text": "Họ và Tên", "stretch": True},
            {"text": "Giới tính", "width": 70},
            {"text": "Ngày sinh", "width": 90},
            {"text": "Lớp", "width": 80},
            {"text": "Email", "stretch": True},
            {"text": "SĐT", "width": 100},
            {"text": "Địa chỉ", "width": 150},
            {"text": "Trạng thái", "width": 100},
        ]
        
        table_frame = tb.Frame(self, padding=10)
        table_frame.pack(fill=BOTH, expand=YES)
        
        self.tree = tb.Treeview(table_frame, columns=[c["text"] for c in self.columns], show="headings", bootstyle="primary")
        for col in self.columns:
            self.tree.heading(col["text"], text=col["text"], anchor=W)
            self.tree.column(col["text"], width=col.get("width", 100), stretch=col.get("stretch", False))
        
        scrollbar = tb.Scrollbar(table_frame, orient=VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side=LEFT, fill=BOTH, expand=YES)
        scrollbar.pack(side=RIGHT, fill=Y)

        pagination_frame = tb.Frame(self, padding=10)
        pagination_frame.pack(fill=X, side=BOTTOM)
        self.lbl_page_info = tb.Label(pagination_frame, text="Trang 1/1")
        self.lbl_page_info.pack(side=LEFT)
        self.btn_next = tb.Button(pagination_frame, text="Sau >", bootstyle="outline", command=self.next_page)
        self.btn_next.pack(side=RIGHT, padx=5)
        self.btn_prev = tb.Button(pagination_frame, text="< Trước", bootstyle="outline", command=self.prev_page)
        self.btn_prev.pack(side=RIGHT, padx=5)

    def load_data(self):
        for item in self.tree.get_children(): self.tree.delete(item)
        students, total = self.service.get_students(self.current_page, self.page_size, self.search_var.get().strip(), self.cbo_filter_class.get(), self.cbo_filter_status.get())
        self.total_records = total
        for sv in students:
            values = (
                sv['ma_sinh_vien'], 
                sv['ho_ten'], 
                sv['gioi_tinh'], 
                sv['ngay_sinh'], 
                sv['ma_lop'], 
                sv['email'], 
                sv.get('sdt', ''), 
                sv.get('dia_chi', ''), # Thêm địa chỉ
                sv['trang_thai']
            )
            self.tree.insert("", END, values=values)
        self.update_pagination_controls()

    def update_pagination_controls(self):
        total_pages = (self.total_records + self.page_size - 1) // self.page_size or 1
        self.lbl_page_info.config(text=f"Trang {self.current_page} / {total_pages} (Tổng: {self.total_records} SV)")
        self.btn_prev.config(state="normal" if self.current_page > 1 else "disabled")
        self.btn_next.config(state="normal" if self.current_page < total_pages else "disabled")

    def on_search(self): self.current_page = 1; self.load_data()
    def next_page(self): self.current_page += 1; self.load_data()
    def prev_page(self): 
        if self.current_page > 1: self.current_page -= 1; self.load_data()

    def on_add(self):
        StudentForm(self, callback=self.load_data, user_data=self.user_data)

    def on_edit(self):
        selected = self.tree.selection()
        if not selected: messagebox.showwarning("Cảnh báo", "Vui lòng chọn sinh viên cần sửa!"); return
        
        values = self.tree.item(selected[0])['values']
        student_data = {
            'ma_sinh_vien': str(values[0]), 
            'ho_ten': values[1], 
            'gioi_tinh': values[2], 
            'ngay_sinh': values[3], 
            'ma_lop': str(values[4]), 
            'email': values[5], 
            'sdt': str(values[6]) if values[6] != 'None' else '', 
            'dia_chi': str(values[7]) if values[7] != 'None' else '', # Cập nhật lấy địa chỉ
            'trang_thai': values[8]
        }
        StudentForm(self, callback=self.load_data, user_data=self.user_data, student_data=student_data)

    def on_delete(self):
        if not self.user_data: messagebox.showerror("Lỗi", "Không tìm thấy thông tin người dùng."); return
        user_role = self.user_data.get('vai_tro', '')
        if user_role not in ['admin', 'dao_tao']: messagebox.showerror("Từ chối truy cập", "Bạn không có quyền xóa sinh viên!"); return
        selected = self.tree.selection()
        if not selected: messagebox.showwarning("Cảnh báo", "Vui lòng chọn sinh viên cần xóa!"); return
        if messagebox.askyesno("Xác nhận", "Hành động này sẽ XÓA TOÀN BỘ dữ liệu điểm và đăng ký học của sinh viên.\nBạn có chắc chắn muốn tiếp tục?"):
            msv = self.tree.item(selected[0])['values'][0]
            current_user = self.user_data.get('ten_dang_nhap', 'system')
            success, msg = self.service.delete_student(str(msv), user_role, current_user)
            if success: messagebox.showinfo("Thành công", msg); self.load_data()
            else: messagebox.showerror("Lỗi", msg)