import ttkbootstrap as tb
from ttkbootstrap.constants import *
from services.dashboard_service import DashboardService
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class DashboardView(tb.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.service = DashboardService()
        
        self.stats = self.service.get_summary_stats()
        self.fail_data = self.service.get_top_failed_subjects()
        self.gpa_data = self.service.get_top_classes_by_gpa()
        
        self.setup_ui()

    def setup_ui(self):
        canvas = tb.Canvas(self)
        scrollbar = tb.Scrollbar(self, orient="vertical", command=canvas.yview)
        scrollable_frame = tb.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        header_frame = tb.Frame(scrollable_frame, padding=20)
        header_frame.pack(fill=X)
        tb.Label(header_frame, text="TỔNG QUAN HỆ THỐNG", font=("Helvetica", 20, "bold"), bootstyle="primary").pack(side=LEFT)

        cards_frame = tb.Frame(scrollable_frame, padding=20)
        cards_frame.pack(fill=X)
        cards_frame.columnconfigure(0, weight=1); cards_frame.columnconfigure(1, weight=1)

        self.create_stat_card(cards_frame, "SINH VIÊN", self.stats['sinh_vien'], "👨‍🎓", "info", 0, 0)
        self.create_stat_card(cards_frame, "GIẢNG VIÊN", self.stats['giang_vien'], "👨‍🏫", "success", 0, 1)
        self.create_stat_card(cards_frame, "LỚP HỌC", self.stats['lop'], "🏫", "warning", 1, 0)
        self.create_stat_card(cards_frame, "MÔN HỌC", self.stats['mon_hoc'], "📚", "danger", 1, 1)

        charts_container = tb.Frame(scrollable_frame, padding=20)
        charts_container.pack(fill=BOTH, expand=YES)

        tb.Label(charts_container, text="TOP 10 MÔN CÓ TỶ LỆ RỚT CAO NHẤT (%)", 
                 font=("Helvetica", 14, "bold"), bootstyle="danger").pack(pady=(10, 5))
        self.draw_chart_fail(charts_container)

        tb.Separator(charts_container).pack(fill=X, pady=30)
        tb.Label(charts_container, text="TOP 10 LỚP CÓ GPA TRUNG BÌNH CAO NHẤT (Hệ 4)", 
                 font=("Helvetica", 14, "bold"), bootstyle="success").pack(pady=(0, 5))
        self.draw_chart_gpa(charts_container)

    def create_stat_card(self, parent, title, value, icon, color, row, col):
        card = tb.Labelframe(parent, text=f"  {icon}  {title}  ", bootstyle=color, padding=15)
        card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        meter = tb.Meter(card, bootstyle=color, subtext="Tổng số", interactive=False, textright="", amounttotal=value * 1.5 if value > 0 else 100, amountused=value, textfont=("Helvetica", 20, "bold"), subtextfont=("Helvetica", 10), metersize=150)
        meter.pack()

    def draw_chart_fail(self, parent):
        if not self.fail_data:
            tb.Label(parent, text="Chưa có dữ liệu.", font=("Arial", 12, "italic")).pack(pady=10)
            return

        subjects = [item['ten_mon'] for item in self.fail_data]
        rates = [item['ty_le'] for item in self.fail_data]
        
        fig, ax = plt.subplots(figsize=(10, 5), dpi=100)
        bars = ax.bar(subjects, rates, color='#e74c3c', width=0.6)
        
        ax.set_ylabel('Tỷ lệ rớt (%)')
        ax.set_ylim(0, 100)
        plt.xticks(rotation=30, ha='right', fontsize=9)
        
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f'{height}%', xy=(bar.get_x() + bar.get_width() / 2, height), xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=9, fontweight='bold')

        plt.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=BOTH, expand=YES, pady=(0, 10))

    def draw_chart_gpa(self, parent):
        if not self.gpa_data:
            tb.Label(parent, text="Chưa có dữ liệu GPA.", font=("Arial", 12, "italic")).pack(pady=10)
            return

        classes = [item['ma_lop'] for item in self.gpa_data]
        gpas = [item['gpa'] for item in self.gpa_data]
        
        fig, ax = plt.subplots(figsize=(10, 5), dpi=100)
        bars = ax.bar(classes, gpas, color='#2ecc71', width=0.6)
        
        ax.set_ylabel('GPA Trung bình')
        ax.set_ylim(0, 4.0)
        
        plt.xticks(rotation=30, ha='right', fontsize=9)
        
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f'{height}', xy=(bar.get_x() + bar.get_width() / 2, height), xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=9, fontweight='bold')

        plt.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=BOTH, expand=YES, pady=(0, 20))