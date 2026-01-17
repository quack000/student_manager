import ttkbootstrap as tb
from ttkbootstrap.constants import *
from ui.dashboard_view import DashboardView
from ui.student_view import StudentView 
from ui.grade_view import GradeView
from ui.class_view import ClassView
from ui.subject_view import SubjectView
from ui.log_view import LogView
from ui.gpa_view import GPAView

class MainWindow(tb.Frame):
    def __init__(self, parent, user_data):
        super().__init__(parent)
        self.parent = parent
        self.user_data = user_data
        self.setup_ui()
        self.show_view("dashboard")

    def setup_ui(self):
        header = tb.Frame(self, bootstyle="secondary", padding=10)
        header.pack(fill=X, side=TOP)
        tb.Label(header, text="🎓 STUDENT MANAGER PRO", font=("Helvetica", 14, "bold"), bootstyle="inverse-secondary").pack(side=LEFT, padx=10)
        tb.Label(header, text=f"Xin chào, {self.user_data['ten_dang_nhap'].upper()}", bootstyle="inverse-secondary").pack(side=RIGHT, padx=20)
        tb.Button(header, text="Đăng xuất", bootstyle="danger", command=self.logout).pack(side=RIGHT, padx=5)

        sidebar = tb.Frame(self, bootstyle="light", padding=10, width=250)
        sidebar.pack(fill=Y, side=LEFT)
        sidebar.pack_propagate(False)

        self.create_menu_btn(sidebar, "📊 Dashboard", "dashboard", "primary")
        self.create_menu_btn(sidebar, "👨‍🎓 Sinh viên", "sinh_vien", "info")
        self.create_menu_btn(sidebar, "📝 Điểm số", "diem", "success")
        self.create_menu_btn(sidebar, "🏆 Kết quả học tập", "gpa", "warning")
        
        tb.Separator(sidebar).pack(fill=X, pady=10)
        self.create_menu_btn(sidebar, "🏫 Lớp học", "lop", "secondary")
        self.create_menu_btn(sidebar, "📚 Môn học", "mon", "secondary")
        
        tb.Separator(sidebar).pack(fill=X, pady=10)
        if self.user_data['vai_tro'] == 'admin':
            self.create_menu_btn(sidebar, "⚙️ Nhật ký HT", "log", "dark")

        self.content_area = tb.Frame(self, padding=20)
        self.content_area.pack(fill=BOTH, expand=YES, side=RIGHT)

    def create_menu_btn(self, parent, text, view_name, color):
        btn = tb.Button(parent, text=text, bootstyle=f"{color}-outline", command=lambda: self.show_view(view_name))
        btn.pack(fill=X, pady=5, ipady=5)

    def show_view(self, view_name):
        for widget in self.content_area.winfo_children(): widget.destroy()

        if view_name == "dashboard": GPAView(self.content_area).pack(fill=BOTH, expand=YES) if 0 else DashboardView(self.content_area).pack(fill=BOTH, expand=YES)
        elif view_name == "sinh_vien": StudentView(self.content_area, user_data=self.user_data).pack(fill=BOTH, expand=YES)
        elif view_name == "diem": GradeView(self.content_area, user_data=self.user_data).pack(fill=BOTH, expand=YES)
        elif view_name == "lop": ClassView(self.content_area, user_data=self.user_data).pack(fill=BOTH, expand=YES)
        elif view_name == "mon": SubjectView(self.content_area, user_data=self.user_data).pack(fill=BOTH, expand=YES)
        elif view_name == "log": LogView(self.content_area, user_data=self.user_data).pack(fill=BOTH, expand=YES)
        elif view_name == "gpa": 
            GPAView(self.content_area, user_data=self.user_data).pack(fill=BOTH, expand=YES)
            
        else:
            tb.Label(self.content_area, text="Chức năng đang phát triển", font=("Arial", 18)).pack(pady=50)

    def logout(self):
        self.parent.show_login()
        self.parent.geometry("400x550")
        self.parent.center_window(400, 550)