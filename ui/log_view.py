import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import messagebox
from services.log_service import LogService

class LogView(tb.Frame):
    def __init__(self, parent, user_data=None):
        super().__init__(parent)
        self.service = LogService()
        self.user_data = user_data
        
        # Pagination
        self.current_page = 1
        self.page_size = 30
        self.total_records = 0
        
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        # --- Toolbar ---
        toolbar = tb.Frame(self, padding=10)
        toolbar.pack(fill=X)
        
        # Tìm kiếm
        self.search_var = tb.StringVar()
        tb.Label(toolbar, text="Tìm kiếm (User/Action):").pack(side=LEFT, padx=5)
        entry_search = tb.Entry(toolbar, textvariable=self.search_var, width=30)
        entry_search.pack(side=LEFT, padx=5)
        entry_search.bind("<Return>", lambda e: self.on_search())
        
        tb.Button(toolbar, text="🔍 Tìm", bootstyle="secondary", command=self.on_search).pack(side=LEFT, padx=2)
        tb.Button(toolbar, text="🔄 Làm mới", bootstyle="info-outline", command=self.load_data).pack(side=LEFT, padx=2)

        # --- Table ---
        self.columns = [
            {"text": "ID", "width": 50},
            {"text": "Thời gian", "width": 150},
            {"text": "Người thực hiện", "width": 120},
            {"text": "Hành động", "width": 100},
            {"text": "Bảng", "width": 100},
            {"text": "ID Đối tượng", "width": 100},
            {"text": "Chi tiết", "stretch": True},
        ]
        
        table_frame = tb.Frame(self, padding=10)
        table_frame.pack(fill=BOTH, expand=YES)
        
        self.tree = tb.Treeview(
            table_frame, 
            columns=[c['text'] for c in self.columns], 
            show="headings", 
            bootstyle="secondary" # Màu xám cho log
        )
        
        for col in self.columns:
            self.tree.heading(col['text'], text=col['text'], anchor=W)
            self.tree.column(col['text'], width=col.get('width', 100), stretch=col.get('stretch', False))
            
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
        # Xóa dữ liệu cũ
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        logs, total = self.service.get_logs(
            self.current_page, self.page_size, self.search_var.get().strip()
        )
        self.total_records = total
        
        for log in logs:
            val = (
                log['id'], 
                log['thoi_gian'], 
                log['nguoi_thuc_hien'], 
                log['hanh_dong'],
                log['ten_bang'],
                log['doi_tuong_id'],
                log['noi_dung_chi_tiet']
            )
            self.tree.insert("", END, values=val)
            
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