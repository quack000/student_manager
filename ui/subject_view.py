import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import messagebox
from services.subject_service import SubjectService
from ui.form_subject import SubjectForm

class SubjectView(tb.Frame):
    def __init__(self, parent, user_data=None):
        super().__init__(parent)
        self.service = SubjectService()
        self.user_data = user_data
        self.current_page = 1
        self.page_size = 20
        self.total_records = 0
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        # (Phần UI giữ nguyên, chỉ sửa các hàm on_...)
        toolbar = tb.Frame(self, padding=10)
        toolbar.pack(fill=X)
        self.search_var = tb.StringVar()
        tb.Label(toolbar, text="Tìm kiếm:").pack(side=LEFT, padx=5)
        tb.Entry(toolbar, textvariable=self.search_var, width=30).pack(side=LEFT, padx=5)
        tb.Button(toolbar, text="🔍", bootstyle="secondary", command=self.on_search).pack(side=LEFT, padx=2)

        bg = tb.Frame(toolbar); bg.pack(side=RIGHT)
        role = self.user_data.get('vai_tro', '') if self.user_data else ''
        if role in ['admin', 'dao_tao']:
            tb.Button(bg, text="+ Thêm Môn", bootstyle="success", command=self.on_add).pack(side=LEFT, padx=2)
            tb.Button(bg, text="✏️ Sửa", bootstyle="warning", command=self.on_edit).pack(side=LEFT, padx=2)
            tb.Button(bg, text="🗑️ Xóa", bootstyle="danger", command=self.on_delete).pack(side=LEFT, padx=2)

        self.columns = [{"text": "Mã Môn", "width": 80}, {"text": "Tên Môn Học", "stretch": True}, {"text": "Số TC", "width": 60}, {"text": "QT", "width": 50}, {"text": "GK", "width": 50}, {"text": "CK", "width": 50}]
        table_frame = tb.Frame(self, padding=10); table_frame.pack(fill=BOTH, expand=YES)
        self.tree = tb.Treeview(table_frame, columns=[c['text'] for c in self.columns], show="headings", bootstyle="primary")
        for col in self.columns: self.tree.heading(col['text'], text=col['text'], anchor=W); self.tree.column(col['text'], width=col.get('width', 100), stretch=col.get('stretch', False))
        scrollbar = tb.Scrollbar(table_frame, orient=VERTICAL, command=self.tree.yview); self.tree.configure(yscrollcommand=scrollbar.set); self.tree.pack(side=LEFT, fill=BOTH, expand=YES); scrollbar.pack(side=RIGHT, fill=Y)

        page_frame = tb.Frame(self, padding=10); page_frame.pack(fill=X, side=BOTTOM)
        self.lbl_page = tb.Label(page_frame, text="Trang 1/1"); self.lbl_page.pack(side=LEFT)
        tb.Button(page_frame, text="Sau >", bootstyle="outline", command=self.next_page).pack(side=RIGHT, padx=2)
        tb.Button(page_frame, text="< Trước", bootstyle="outline", command=self.prev_page).pack(side=RIGHT, padx=2)

    def load_data(self):
        for item in self.tree.get_children(): self.tree.delete(item)
        subjects, total = self.service.get_subjects(self.current_page, self.page_size, self.search_var.get().strip())
        self.total_records = total
        for s in subjects:
            val = (s['ma_mon'], s['ten_mon'], s['so_tin_chi'], s['ty_le_qt'], s['ty_le_gk'], s['ty_le_ck'])
            self.tree.insert("", END, values=val)
        self.update_pagination()

    def update_pagination(self):
        pages = (self.total_records + self.page_size - 1) // self.page_size or 1
        self.lbl_page.config(text=f"Trang {self.current_page} / {pages} (Tổng: {self.total_records})")

    def on_search(self): self.current_page = 1; self.load_data()
    def next_page(self): self.current_page += 1; self.load_data()
    def prev_page(self): 
        if self.current_page > 1: self.current_page -= 1; self.load_data()

    def on_add(self):
        SubjectForm(self, callback=self.load_data, user_data=self.user_data) # Truyền user_data

    def on_edit(self):
        sel = self.tree.selection()
        if not sel: messagebox.showwarning("Chọn môn", "Vui lòng chọn môn học cần sửa"); return
        values = self.tree.item(sel[0])['values']
        data = {'ma_mon': str(values[0]), 'ten_mon': values[1], 'so_tin_chi': int(values[2]), 'ty_le_qt': float(values[3]), 'ty_le_gk': float(values[4]), 'ty_le_ck': float(values[5])}
        SubjectForm(self, callback=self.load_data, user_data=self.user_data, subject_data=data) # Truyền user_data

    def on_delete(self):
        sel = self.tree.selection()
        if not sel: messagebox.showwarning("Chọn môn", "Vui lòng chọn môn học cần xóa"); return
        ma_mon = self.tree.item(sel[0])['values'][0]
        if messagebox.askyesno("Xác nhận", f"Bạn có chắc muốn xóa môn {ma_mon}?"):
            current_user = self.user_data.get('ten_dang_nhap', 'system') # Lấy username
            success, msg = self.service.delete_subject(str(ma_mon), current_user)
            if success: messagebox.showinfo("Thành công", msg); self.load_data()
            else: messagebox.showerror("Lỗi", msg)