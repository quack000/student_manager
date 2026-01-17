import ttkbootstrap as tb
from ui.login_window import LoginWindow
from ui.main_window import MainWindow

class App(tb.Window):
    def __init__(self):
        super().__init__(themename="litera")
        self.title("Hệ thống Quản lý Sinh viên")
        self.geometry("400x550")
        
        self.center_window(400, 550)
        self.user_data = None
        
        self.show_login()

    def center_window(self, width, height):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.geometry(f"{width}x{height}+{x}+{y}")

    def show_login(self):
        for widget in self.winfo_children():
            widget.destroy()
            
        self.login_view = LoginWindow(self)
        self.login_view.pack(fill="both", expand=True)

    def switch_to_main(self, user_data):
        self.user_data = user_data
        
        self.title(f"Hệ thống Quản lý Sinh viên - Xin chào {user_data['ten_dang_nhap']}")
        self.state("zoomed")
        
        for widget in self.winfo_children():
            widget.destroy()
            
        self.main_view = MainWindow(self, user_data)
        self.main_view.pack(fill="both", expand=True)

if __name__ == "__main__":
    app = App()
    app.mainloop()