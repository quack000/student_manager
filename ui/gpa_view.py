import ttkbootstrap as tb
from ttkbootstrap.constants import *
from services.gpa_service import GPAService

class GPAView(tb.Frame):
    def __init__(self, parent, user_data=None):
        super().__init__(parent)
        self.service = GPAService()
        self.user_data = user_data
        
        self.current_page = 1
        self.page_size = 25
        self.total_records = 0
        self.class_list = self.service.get_filter_options()
        
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        # Toolbar
        toolbar = tb.Frame(self, padding=10)
        toolbar.pack(fill=X)
        
        filter_frame = tb.Labelframe(toolbar, text="Tra cứu & Xếp loại", padding=5)
        filter_frame.pack(side=LEFT, fill=Y)

        self.search_var = tb.StringVar()
        tb.Label(filter_frame, text="Tìm kiếm:").pack(side=LEFT, padx=5)
        entry_search = tb.Entry(filter_frame, textvariable=self.search_var, width=20)
        entry_search.pack(side=LEFT, padx=5)
        entry_search.bind("<Return>", lambda e: self.on_search())

        tb.Label(filter_frame, text="Lớp:").pack(side=LEFT, padx=5)
        self.cbo_lop = tb.Combobox(filter_frame, values=["Tất cả"] + self.class_list, state="readonly", width=10)
        self.cbo_lop.current(0)
        self.cbo_lop.pack(side=LEFT, padx=5)
        self.cbo_lop.bind("<<ComboboxSelected>>", lambda e: self.on_search())

        tb.Button(filter_frame, text="🔍 Xem KQ", bootstyle="primary", command=self.on_search).pack(side=LEFT, padx=10)

        # Legend (Chú thích)
        legend = tb.Frame(toolbar)
        legend.pack(side=RIGHT, padx=10)
        tb.Label(legend, text="CPA < 2.0: Cảnh báo", bootstyle="danger", font=("Arial", 9, "bold")).pack(side=RIGHT)

        # Table
        self.columns = [
            {"text": "Mã SV", "width": 100},
            {"text": "Họ và Tên", "width": 200},
            {"text": "Lớp", "width": 80},
            {"text": "TC Tích lũy", "width": 80, "anchor": CENTER},
            {"text": "CPA (Hệ 4)", "width": 100, "anchor": CENTER},
            {"text": "Xếp loại", "width": 100, "anchor": CENTER},
            {"text": "Trạng thái", "width": 100},
        ]
        
        table_frame = tb.Frame(self, padding=10)
        table_frame.pack(fill=BOTH, expand=YES)
        
        self.tree = tb.Treeview(
            table_frame, 
            columns=[c['text'] for c in self.columns], 
            show="headings", 
            bootstyle="info"
        )
        
        for col in self.columns:
            self.tree.heading(col['text'], text=col['text'], anchor=col.get("anchor", W))
            self.tree.column(col['text'], width=col['width'], anchor=col.get("anchor", W))
            
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
            
        data, total = self.service.get_academic_list(
            self.current_page, self.page_size,
            self.search_var.get().strip(),
            self.cbo_lop.get()
        )
        self.total_records = total
        
        for sv in data:
            val = (
                sv['ma_sinh_vien'], sv['ho_ten'], sv['ma_lop'],
                sv['tin_chi'], sv['cpa'], sv['xep_loai'], sv['trang_thai']
            )
            # Highlight sinh viên yếu
            tags = ("warning",) if sv['cpa'] < 2.0 else ()
            self.tree.insert("", END, values=val, tags=tags)
            
        self.tree.tag_configure("warning", background="#ffcccc") # Màu nền đỏ nhạt cho SV cảnh báo

        self.update_pagination()

    def update_pagination(self):
        pages = (self.total_records + self.page_size - 1) // self.page_size or 1
        self.lbl_page.config(text=f"Trang {self.current_page} / {pages} (Tổng: {self.total_records})")

    def on_search(self): self.current_page = 1; self.load_data()
    def next_page(self): self.current_page += 1; self.load_data()
    def prev_page(self): 
        if self.current_page > 1: self.current_page -= 1; self.load_data()