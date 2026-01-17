import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import filedialog, messagebox
from services.grade_service import GradeService
from ui.form_grade import GradeForm

class ExportGradeForm(tb.Toplevel):
    def __init__(self, parent, service, filters):
        super().__init__(parent)
        self.title("Tùy chọn Xuất Bảng Điểm")
        self.geometry("500x600")
        self.resizable(False, False)
        
        self.service = service
        self.filters = filters # Dữ liệu danh sách lớp, môn, học kỳ để fill vào combobox
        
        self.setup_ui()

    def setup_ui(self):
        main = tb.Frame(self, padding=20)
        main.pack(fill=BOTH, expand=YES)

        tb.Label(main, text="CẤU HÌNH XUẤT DỮ LIỆU", font=("Helvetica", 14, "bold"), bootstyle="primary").pack(pady=(0, 20))

        group_scope = tb.Labelframe(main, text="1. Phạm vi xuất", padding=15)
        group_scope.pack(fill=X, pady=(0, 15))

        self.var_scope = tb.StringVar(value="all")
        
        tb.Radiobutton(group_scope, text="Tất cả sinh viên", variable=self.var_scope, value="all", command=self.toggle_inputs).pack(anchor=W, pady=2)
        
        f_class = tb.Frame(group_scope)
        f_class.pack(fill=X, pady=2)
        tb.Radiobutton(f_class, text="Theo Lớp:", variable=self.var_scope, value="class", command=self.toggle_inputs).pack(side=LEFT)
        self.cbo_export_class = tb.Combobox(f_class, values=self.filters['lop'], state="disabled", width=25)
        self.cbo_export_class.pack(side=LEFT, padx=10)

        f_sv = tb.Frame(group_scope)
        f_sv.pack(fill=X, pady=2)
        tb.Radiobutton(f_sv, text="Sinh viên cụ thể (Mã SV):", variable=self.var_scope, value="student", command=self.toggle_inputs).pack(side=LEFT)
        self.entry_export_msv = tb.Entry(f_sv, state="disabled", width=20)
        self.entry_export_msv.pack(side=LEFT, padx=10)

        group_subject = tb.Labelframe(main, text="2. Môn học", padding=15)
        group_subject.pack(fill=X, pady=(0, 15))

        self.var_subject = tb.StringVar(value="all")
        tb.Radiobutton(group_subject, text="Tất cả các môn", variable=self.var_subject, value="all", command=self.toggle_inputs).pack(anchor=W, pady=2)
        
        f_sub = tb.Frame(group_subject)
        f_sub.pack(fill=X, pady=2)
        tb.Radiobutton(f_sub, text="Môn cụ thể:", variable=self.var_subject, value="specific", command=self.toggle_inputs).pack(side=LEFT)
        self.cbo_export_subject = tb.Combobox(f_sub, values=self.filters['mon'], state="disabled", width=30)
        self.cbo_export_subject.pack(side=LEFT, padx=10)

        group_sem = tb.Labelframe(main, text="3. Học kỳ", padding=15)
        group_sem.pack(fill=X, pady=(0, 20))

        self.var_sem = tb.StringVar(value="all")
        tb.Radiobutton(group_sem, text="Tất cả học kỳ", variable=self.var_sem, value="all", command=self.toggle_inputs).pack(anchor=W, pady=2)
        
        f_sem = tb.Frame(group_sem)
        f_sem.pack(fill=X, pady=2)
        tb.Radiobutton(f_sem, text="Học kỳ cụ thể:", variable=self.var_sem, value="specific", command=self.toggle_inputs).pack(side=LEFT)
        self.cbo_export_sem = tb.Combobox(f_sem, values=self.filters['hoc_ky'], state="disabled", width=20)
        self.cbo_export_sem.pack(side=LEFT, padx=10)

        btn_frame = tb.Frame(main)
        btn_frame.pack(fill=X, pady=10)
        tb.Button(btn_frame, text="Hủy bỏ", bootstyle="secondary-outline", command=self.destroy).pack(side=LEFT, expand=YES, fill=X, padx=(0, 5))
        tb.Button(btn_frame, text="XUẤT FILE CSV", bootstyle="success", command=self.on_confirm_export).pack(side=RIGHT, expand=YES, fill=X, padx=(5, 0))

    def toggle_inputs(self):
        """Bật/Tắt các ô nhập liệu dựa trên radio button"""
        scope = self.var_scope.get()
        self.cbo_export_class.configure(state="readonly" if scope == "class" else "disabled")
        self.entry_export_msv.configure(state="normal" if scope == "student" else "disabled")

        subj = self.var_subject.get()
        self.cbo_export_subject.configure(state="readonly" if subj == "specific" else "disabled")

        sem = self.var_sem.get()
        self.cbo_export_sem.configure(state="readonly" if sem == "specific" else "disabled")

    def on_confirm_export(self):
        scope = self.var_scope.get()
        ma_lop = ""
        search_text = ""
        
        if scope == "class":
            ma_lop = self.cbo_export_class.get()
            if not ma_lop:
                messagebox.showwarning("Thiếu thông tin", "Vui lòng chọn Lớp cần xuất!")
                return
        elif scope == "student":
            search_text = self.entry_export_msv.get().strip()
            if not search_text:
                messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập Mã sinh viên!")
                return

        ten_mon = ""
        if self.var_subject.get() == "specific":
            ten_mon = self.cbo_export_subject.get()
            if not ten_mon:
                messagebox.showwarning("Thiếu thông tin", "Vui lòng chọn Môn học!")
                return

        hoc_ky = ""
        if self.var_sem.get() == "specific":
            hoc_ky = self.cbo_export_sem.get()
            if not hoc_ky:
                messagebox.showwarning("Thiếu thông tin", "Vui lòng chọn Học kỳ!")
                return

        file_path = filedialog.asksaveasfilename(
            title="Lưu file CSV",
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv")],
            initialfile="bang_diem_export.csv"
        )
        if not file_path:
            return

        success, msg = self.service.export_grades_to_csv(
            file_path, 
            search_text=search_text, 
            ma_lop=ma_lop, 
            ten_mon=ten_mon, 
            hoc_ky=hoc_ky
        )
        
        if success:
            messagebox.showinfo("Xuất dữ liệu thành công", msg)
            self.destroy()
        else:
            messagebox.showerror("Lỗi Xuất", msg)

class GradeView(tb.Frame):
    def __init__(self, parent, user_data=None):
        super().__init__(parent)
        self.service = GradeService()
        self.user_data = user_data
        
        self.current_page = 1
        self.page_size = 30
        self.total_records = 0
        
        self.filters = self.service.get_filter_options()
        
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        toolbar = tb.Frame(self, padding=10)
        toolbar.pack(fill=X)
        
        filter_group = tb.Labelframe(toolbar, text="Tìm kiếm & Lọc", padding=5)
        filter_group.pack(side=LEFT, fill=Y, padx=5)
        
        self.search_var = tb.StringVar()
        tb.Entry(filter_group, textvariable=self.search_var, width=15).pack(side=LEFT, padx=2)
        
        tb.Label(filter_group, text="Lớp:").pack(side=LEFT, padx=(5, 2))
        self.cbo_lop = tb.Combobox(filter_group, values=["Tất cả"] + self.filters['lop'], width=8, state="readonly")
        self.cbo_lop.current(0)
        self.cbo_lop.pack(side=LEFT, padx=2)
        
        tb.Label(filter_group, text="Môn:").pack(side=LEFT, padx=(5, 2))
        self.cbo_mon = tb.Combobox(filter_group, values=["Tất cả"] + self.filters['mon'], width=15, state="readonly") 
        self.cbo_mon.current(0)
        self.cbo_mon.pack(side=LEFT, padx=2)
        
        tb.Label(filter_group, text="HK:").pack(side=LEFT, padx=(5, 2))
        self.cbo_hk = tb.Combobox(filter_group, values=["Tất cả"] + self.filters['hoc_ky'], width=8, state="readonly")
        self.cbo_hk.current(0)
        self.cbo_hk.pack(side=LEFT, padx=2)
        
        tb.Button(filter_group, text="🔍", bootstyle="secondary", command=self.on_search).pack(side=LEFT, padx=5)

        btn_group = tb.Frame(toolbar)
        btn_group.pack(side=RIGHT, fill=Y)
        
        tb.Button(btn_group, text="📥 Import CSV", bootstyle="success-outline", command=self.on_import_csv).pack(side=LEFT, padx=2)
        tb.Button(btn_group, text="📤 Xuất CSV", bootstyle="info-outline", command=self.on_export_csv).pack(side=LEFT, padx=2)
        
        tb.Button(btn_group, text="✏️ Sửa điểm", bootstyle="primary", command=self.on_edit).pack(side=LEFT, padx=2)

        self.columns = [
            {"text": "Mã SV", "width": 80},
            {"text": "Họ tên", "width": 150},
            {"text": "Lớp", "width": 70},
            {"text": "Môn học", "width": 150},
            {"text": "Học kỳ", "width": 80},
            {"text": "QT", "width": 50},
            {"text": "GK", "width": 50},
            {"text": "CK", "width": 50},
            {"text": "Tổng (10)", "width": 70},
            {"text": "Hệ 4", "width": 60},
        ]
        
        table_frame = tb.Frame(self, padding=10)
        table_frame.pack(fill=BOTH, expand=YES)
        
        self.tree = tb.Treeview(
            table_frame, 
            columns=[c["text"] for c in self.columns], 
            show="headings", 
            bootstyle="primary"
        )
        
        for col in self.columns:
            self.tree.heading(col["text"], text=col["text"], anchor=W)
            self.tree.column(col["text"], width=col["width"], stretch=True)
            
        scrollbar = tb.Scrollbar(table_frame, orient=VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=LEFT, fill=BOTH, expand=YES)
        scrollbar.pack(side=RIGHT, fill=Y)

        # --- Pagination ---
        page_frame = tb.Frame(self, padding=10)
        page_frame.pack(fill=X, side=BOTTOM)
        
        self.lbl_page = tb.Label(page_frame, text="Trang 1/1")
        self.lbl_page.pack(side=LEFT)
        
        tb.Button(page_frame, text="Sau >", bootstyle="outline", command=self.next_page).pack(side=RIGHT, padx=2)
        tb.Button(page_frame, text="< Trước", bootstyle="outline", command=self.prev_page).pack(side=RIGHT, padx=2)

    def load_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        grades, total = self.service.get_grades(
            self.current_page, self.page_size,
            self.search_var.get().strip(),
            self.cbo_lop.get(),
            self.cbo_mon.get(),
            self.cbo_hk.get()
        )
        self.total_records = total
        
        for g in grades:
            val = (
                g['ma_sinh_vien'], g['ho_ten'], g['ma_lop'], 
                g['ten_mon'], g['hoc_ky'],
                g['diem_qt'], g['diem_gk'], g['diem_ck'],
                g['tong_diem_10'], g['tong_diem_4']
            )
            item_id = self.tree.insert("", END, values=val)
            self.tree.item(item_id, tags=(g['id'],))

        self.update_pagination()

    def update_pagination(self):
        pages = (self.total_records + self.page_size - 1) // self.page_size or 1
        self.lbl_page.config(text=f"Trang {self.current_page} / {pages} (Tổng: {self.total_records})")

    def on_search(self):
        self.current_page = 1
        self.load_data()

    def next_page(self):
        self.current_page += 1
        self.load_data()

    def prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.load_data()

    def on_edit(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một dòng điểm để nhập!")
            return
            
        grade_id = self.tree.item(selected[0], "tags")[0]
        values = self.tree.item(selected[0])['values']
        
        grade_data = {
            'id': grade_id,
            'ma_sinh_vien': values[0],
            'ho_ten': values[1],
            'ten_mon': values[3],
            'hoc_ky': values[4],
            'diem_qt': float(values[5]),
            'diem_gk': float(values[6]),
            'diem_ck': float(values[7])
        }
        
        GradeForm(self, callback=self.load_data, user_data=self.user_data, grade_data=grade_data)

    def on_import_csv(self):
        file_path = filedialog.askopenfilename(
            title="Chọn file CSV bảng điểm",
            filetypes=[("CSV Files", "*.csv")]
        )
        if not file_path:
            return

        current_user = self.user_data.get('ten_dang_nhap', 'system')
        success, msg = self.service.import_grades_from_csv(file_path, current_user)
        if success:
            messagebox.showinfo("Thành công", msg)
            self.load_data()
        else:
            messagebox.showerror("Lỗi Import", msg)

    def on_export_csv(self):
        ExportGradeForm(self, self.service, self.filters)