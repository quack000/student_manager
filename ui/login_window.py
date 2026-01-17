import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import messagebox
from services.auth_service import AuthService

class LoginWindow(tb.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.auth_service = AuthService()
        self.setup_ui()

    def setup_ui(self):
        main_frame = tb.Frame(self, padding=30)
        main_frame.pack(fill=BOTH, expand=YES)

        lbl_logo = tb.Label(
            main_frame, 
            text="🎓", 
            font=("Segoe UI Emoji", 64)
        )
        lbl_logo.pack(pady=(20, 10))

        lbl_title = tb.Label(
            main_frame, 
            text="QUẢN LÝ SINH VIÊN", 
            font=("Helvetica", 16, "bold"),
            bootstyle="primary"
        )
        lbl_title.pack(pady=(0, 30))

        lbl_user = tb.Label(main_frame, text="Tên đăng nhập", font=("Helvetica", 10))
        lbl_user.pack(fill=X, pady=(0, 5))
        
        self.entry_user = tb.Entry(main_frame, font=("Helvetica", 11))
        self.entry_user.pack(fill=X, pady=(0, 15), ipady=5)
        self.entry_user.focus()

        lbl_pass = tb.Label(main_frame, text="Mật khẩu", font=("Helvetica", 10))
        lbl_pass.pack(fill=X, pady=(0, 5))
        
        self.entry_pass = tb.Entry(main_frame, font=("Helvetica", 11), show="•")
        self.entry_pass.pack(fill=X, pady=(0, 20), ipady=5)
        self.entry_pass.bind("<Return>", self.on_login_click)

        btn_login = tb.Button(
            main_frame, 
            text="ĐĂNG NHẬP", 
            bootstyle="primary", 
            command=self.on_login_click,
            width=20
        )
        btn_login.pack(fill=X, ipady=10)

        lbl_footer = tb.Label(
            main_frame, 
            text="Khoa Công nghệ Thông tin © 2024", 
            font=("Helvetica", 8),
            foreground="gray"
        )
        lbl_footer.pack(side=BOTTOM, pady=10)

    def on_login_click(self, event=None):
        username = self.entry_user.get().strip()
        password = self.entry_pass.get().strip()

        if not username or not password:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập đầy đủ thông tin!")
            return

        result = self.auth_service.login(username, password)

        if result and "error" in result:
             messagebox.showerror("Lỗi", result["error"])
        elif result:
            self.parent.switch_to_main(result)
        else:
            messagebox.showerror("Thất bại", "Tên đăng nhập hoặc mật khẩu không đúng.")