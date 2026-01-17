import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import messagebox
from services.class_service import ClassService
from ui.form_class import ClassForm

class ClassView(tb.Frame):
    def __init__(self, parent, user_data=None):
        super().__init__(parent)
        self.service = ClassService()
        self.user_data = user_data
        
        self.current_page = 1
        self.page_size = 20
        self.total_records = 0
        
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        # Toolbar
        toolbar = tb.Frame(self, padding=10)
        toolbar.pack(fill=X)
        
        # Search
        self.search_var = tb.StringVar()
        tb.Label(toolbar, text="Tìm kiếm:").pack(side=LEFT, padx=5)
        tb.Entry(toolbar, textvariable=self.search_var, width=25).pack(side=LEFT, padx=5)
        tb.Button(toolbar, text="🔍", bootstyle="secondary", command=self.on_search).pack(side=LEFT, padx=2)

        # Buttons
        bg = tb.Frame(toolbar)
        bg.pack(side=RIGHT)
        
        role = self.user_data.get('vai_tro', '') if self.user_data else ''
        if role in ['admin', 'dao_tao']:
            tb.Button(bg, text="+ Thêm Lớp", bootstyle="success", command=self.on_add).pack(side=LEFT, padx=2)
            tb.Button(bg, text="✏️ Sửa", bootstyle="warning", command=self.on_edit).pack(side=LEFT, padx=2)
            tb.Button(bg, text="🗑️ Xóa", bootstyle="danger", command=self.on_delete).pack(side=LEFT, padx=2)

        # Table
        self.columns = [
            {"text": "Mã Lớp", "width": 100},
            {"text": "Tên Lớp", "stretch": True},
            {"text": "Năm Nhập học", "width": 120},
            {"text": "Ngành", "width": 100},
            {"text": "CVHT", "width": 200},
        ]
        
        table_frame = tb.Frame(self, padding=10)
        table_frame.pack(fill=BOTH, expand=YES)
        
        self.tree = tb.Treeview(
            table_frame, 
            columns=[c['text'] for c in self.columns], 
            show="headings", 
            bootstyle="primary"
        )
        
        for col in self.columns:
            self.tree.heading(col['text'], text=col['text'], anchor=W)
            self.tree.column(col['text'], width=col.get('width', 100), stretch=col.get('stretch', False))
            
        scrollbar = tb.Scrollbar(table_frame, orient=VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=LEFT, fill=BOTH, expand=YES)
        scrollbar.pack(side=RIGHT, fill=Y)

        # Pagination
        page_frame = tb.Frame(self, padding=10)
        page_frame.pack(fill=X, side=BOTTOM)
        
        self.lbl_page = tb.Label(page_frame, text="Trang 1/1")
        self.lbl_page.pack(side=LEFT)
        
        tb.Button(page_frame, text="Sau >", bootstyle="outline", command=self.next_page).pack(side=RIGHT, padx=2)
        tb.Button(page_frame, text="< Trước", bootstyle="outline", command=self.prev_page).pack(side=RIGHT, padx=2)

    def load_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        classes, total = self.service.get_classes(
            self.current_page, self.page_size, self.search_var.get().strip()
        )
        self.total_records = total
        
        for c in classes:
            cvht = c['ten_cvht'] if c['ten_cvht'] else "(Trống)"
            val = (c['ma_lop'], c['ten_lop'], c['nam_nhap_hoc'], c['nganh_hoc'], cvht)
            self.tree.insert("", END, values=val, tags=(c['ma_gv_co_van'] or "",))
            
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

    def on_add(self):
        # Truyền user_data vào Form
        ClassForm(self, callback=self.load_data, user_data=self.user_data)

    def on_edit(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Chọn lớp", "Vui lòng chọn lớp cần sửa")
            return
            
        values = self.tree.item(sel[0])['values']
        ma_gv = self.tree.item(sel[0], "tags")[0]
        
        data = {
            'ma_lop': str(values[0]),
            'ten_lop': values[1],
            'nam_nhap_hoc': values[2],
            'nganh_hoc': values[3],
            'ma_gv_co_van': ma_gv
        }
        # Truyền user_data vào Form
        ClassForm(self, callback=self.load_data, user_data=self.user_data, class_data=data)

    def on_delete(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Chọn lớp", "Vui lòng chọn lớp cần xóa")
            return
            
        ma_lop = self.tree.item(sel[0])['values'][0]
        
        # Lấy tên người dùng hiện tại
        current_user = self.user_data.get('ten_dang_nhap', 'system') if self.user_data else 'system'

        if messagebox.askyesno("Xác nhận", f"Bạn có chắc muốn xóa lớp {ma_lop}?"):
            # Truyền user vào hàm delete
            success, msg = self.service.delete_class(str(ma_lop), current_user)
            if success:
                messagebox.showinfo("Thành công", msg)
                self.load_data()
            else:
                messagebox.showerror("Lỗi", msg)