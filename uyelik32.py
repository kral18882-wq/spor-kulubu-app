import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import pandas as pd
from datetime import datetime
import os
import sys

# Pillow kütüphanesi logo için
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# ReportLab kütüphanesi PDF için
try:
    from reportlab.lib.pagesizes import letter, landscape
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    
    FONT_NAME = 'Helvetica'
    for font_path in ["C:\\Windows\\Fonts\\arial.ttf", "/Library/Fonts/Arial.ttf", "/System/Library/Fonts/Supplemental/Arial.ttf"]:
        if os.path.exists(font_path):
            try:
                pdfmetrics.registerFont(TTFont('ArialTurk', font_path))
                FONT_NAME = 'ArialTurk'
                break
            except Exception:
                pass
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


def fix_tr(text):
    if not text:
        return ""
    text_str = str(text)
    if 'ArialTurk' not in pdfmetrics.getRegisteredFontNames():
        tr_map = {
            'İ': 'I', 'ı': 'i', 'Ş': 'S', 'ş': 's', 
            'Ğ': 'G', 'ğ': 'g', 'Ü': 'U', 'ü': 'u', 
            'Ö': 'O', 'ö': 'o', 'Ç': 'C', 'ç': 'c'
        }
        for k, v in tr_map.items():
            text_str = text_str.replace(k, v)
    return text_str


class SportsClubApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Spor Kulübü & Üyelik, Seans, Dondurma, Yoklama, Ay Ay Ödeme ve Raporlama Sistemi")
        self.root.geometry("1500x880")
        self.root.minsize(1200, 750)

        self.editing_student_id = None
        self.selected_student_ids = set()
        
        # --- ŞİFRE VE YETKİ AYARLARI ---
        self.admin_username = "admin"
        self.admin_password = "1234"
        self.ROOT_RECOVERY_KEY = "aeboydak1234"
        self.is_payment_unlocked = False

        # --- TEMA AYARLARI ---
        self.style = ttk.Style()
        self.style.theme_use('clam')

        self.root.configure(bg='#F4F6F9')

        self.style.configure('.', 
            background='#F4F6F9', 
            foreground='#1E293B', 
            font=('Segoe UI', 10, 'bold')
        )
        
        self.style.configure('TNotebook', background='#F4F6F9', borderwidth=0)
        self.style.configure('TNotebook.Tab', 
            background='#E2E8F0', 
            foreground='#0F172A', 
            font=('Segoe UI', 11, 'bold'),
            padding=[16, 9]
        )
        self.style.map('TNotebook.Tab', 
            background=[('selected', '#FFFFFF')], 
            foreground=[('selected', '#0F172A')]
        )

        self.style.configure('TLabelframe', background='#FFFFFF', bordercolor='#CBD5E1', borderwidth=1)
        self.style.configure('TLabelframe.Label', background='#FFFFFF', foreground='#0F172A', font=('Segoe UI', 12, 'bold'))
        self.style.configure('TFrame', background='#FFFFFF')
        self.style.configure('TLabel', background='#FFFFFF', foreground='#1E293B', font=('Segoe UI', 10, 'bold'))
        
        self.style.configure('TButton', 
            background='#E2E8F0', 
            foreground='#0F172A', 
            font=('Segoe UI', 10, 'bold'),
            borderwidth=1,
            focusthickness=0,
            padding=6
        )
        self.style.map('TButton', background=[('active', '#CBD5E1')])

        self.style.configure('Treeview', 
            background='#FFFFFF', 
            foreground='#0F172A', 
            fieldbackground='#FFFFFF',
            font=('Segoe UI', 10, 'bold'),
            rowheight=28
        )
        self.style.configure('Treeview.Heading', 
            background='#334155', 
            foreground='#FFFFFF', 
            font=('Segoe UI', 10, 'bold'),
            padding=5
        )
        self.style.map('Treeview.Heading', background=[('active', '#475569')])

        self.groups = [
            "Taekwondo", "Muaythai-Kickboks", "Pilates", 
            "Temel Hareket Jimnastik", "Kayak", "Yüzme"
        ]

        self.sessions = [
            "09:00 - 10:00", "10:00 - 11:00", "11:00 - 12:00", 
            "13:00 - 14:00", "14:00 - 15:00", "15:00 - 16:00", 
            "16:00 - 17:00", "18:00 - 19:00", "19:00 - 20:00", 
            "20:00 - 21:00"
        ]

        self.days_list = [
            "Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"
        ]

        self.months_list = [
            "Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", 
            "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"
        ]

        self.duration_options = [
            "12 Ay (1 Yıl - Varsayılan)", "1 Ay", "2 Ay", "3 Ay", "4 Ay", "5 Ay", 
            "6 Ay", "7 Ay", "8 Ay", "9 Ay", "10 Ay", "11 Ay"
        ]

        self.columns = [
            "Seç", "ID", "Ad Soyad", "TC No", "Doğum Tarihi", "İletişim 1", "İletişim 2", 
            "Kayıt Tarihi", "Kronik Hastalık", "Veli Ad Soyad", "Veli Meslek", 
            "Veli İletişim 1", "Veli İletişim 2", "Grup / Branş", "Seans / Saat", 
            "Haftanın Günleri", "Üyelik Süresi", "Üyelik Durumu", "Aylık Tutar", "Son Ödeme Tarihi", "Ödeme Durumu"
        ]
        
        self.df = pd.DataFrame(columns=[col for col in self.columns if col != "Seç"])
        self.attendance_records = {}
        self.monthly_payments = {}
        
        # --- DOSYA YOLU AYARI (.exe İçin Kalıcılık Düzeltmesi) ---
        if getattr(sys, 'frozen', False):
            script_dir = os.path.dirname(sys.executable)
        else:
            script_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in locals() or '__file__' in globals() else os.getcwd()
            
        self.AUTO_SAVE_FILE = os.path.join(script_dir, "spor_kulubu_otomatik_kayit.xlsx")
        self.LOGO_FILE = os.path.join(script_dir, "logo.png")

        self.load_from_storage()
        self.setup_ui()

    def save_to_storage(self):
        """Tüm Öğrenci, Ödeme, Yoklama ve Şifre verilerini kalıcı Excel sayfalarına kaydeder."""
        try:
            with pd.ExcelWriter(self.AUTO_SAVE_FILE, engine='openpyxl') as writer:
                # 1. Ana Öğrenci Tablosu
                self.df.to_excel(writer, sheet_name='Ogrenciler', index=False)
                
                # 2. Ay Ay Ödeme Tablosu
                pay_data = []
                for (student_id, month), status in self.monthly_payments.items():
                    pay_data.append({'ID': student_id, 'Ay': month, 'Durum': status})
                df_pay = pd.DataFrame(pay_data)
                df_pay.to_excel(writer, sheet_name='Odemeler', index=False)

                # 3. Yoklama Tablosu (Gelişmiş Detaylar)
                att_data = []
                for key, val in self.attendance_records.items():
                    student_id, date_str = key[0], key[1]
                    if isinstance(val, dict):
                        status = val.get('status', 'Geldi')
                        branch = val.get('branch', '')
                        session = val.get('session', '')
                    else:
                        status = str(val)
                        branch = ""
                        session = ""
                    att_data.append({
                        'ID': student_id, 
                        'Tarih': date_str, 
                        'Durum': status, 
                        'Brans': branch, 
                        'Seans': session
                    })
                df_att = pd.DataFrame(att_data)
                df_att.to_excel(writer, sheet_name='Yoklama', index=False)

                # 4. Kullanıcı Giriş Bilgileri
                df_auth = pd.DataFrame([{'Kullanici': self.admin_username, 'Sifre': self.admin_password}])
                df_auth.to_excel(writer, sheet_name='Ayarlar', index=False)

        except Exception as e:
            print(f"Otomatik kayıt hatası: {e}")

    def load_from_storage(self):
        """Kayıtlı Excel dosyasından tüm verileri eksiksiz geri yükler."""
        if os.path.exists(self.AUTO_SAVE_FILE):
            try:
                excel_file = pd.ExcelFile(self.AUTO_SAVE_FILE)
                
                # 1. Öğrenci Verilerini Yükle
                if 'Ogrenciler' in excel_file.sheet_names:
                    imported_df = pd.read_excel(excel_file, sheet_name='Ogrenciler', dtype=str)
                    if not imported_df.empty:
                        for col in self.df.columns:
                            if col not in imported_df.columns:
                                imported_df[col] = ""
                        self.df = imported_df[self.df.columns]

                # 2. Ödeme Verilerini Yükle
                if 'Odemeler' in excel_file.sheet_names:
                    df_pay = pd.read_excel(excel_file, sheet_name='Odemeler', dtype=str)
                    self.monthly_payments = {}
                    for _, row in df_pay.iterrows():
                        self.monthly_payments[(str(row['ID']), str(row['Ay']))] = str(row['Durum'])

                # 3. Yoklama Verilerini Yükle
                if 'Yoklama' in excel_file.sheet_names:
                    df_att = pd.read_excel(excel_file, sheet_name='Yoklama', dtype=str)
                    self.attendance_records = {}
                    for _, row in df_att.iterrows():
                        sid = str(row['ID'])
                        dt = str(row['Tarih'])
                        st = str(row['Durum'])
                        br = str(row.get('Brans', '')) if pd.notna(row.get('Brans')) else ""
                        se = str(row.get('Seans', '')) if pd.notna(row.get('Seans')) else ""
                        self.attendance_records[(sid, dt)] = {'status': st, 'branch': br, 'session': se}

                # 4. Giriş Bilgilerini Yükle
                if 'Ayarlar' in excel_file.sheet_names:
                    df_auth = pd.read_excel(excel_file, sheet_name='Ayarlar', dtype=str)
                    if not df_auth.empty:
                        self.admin_username = str(df_auth.iloc[0]['Kullanici'])
                        self.admin_password = str(df_auth.iloc[0]['Sifre'])

            except Exception as e:
                print(f"Otomatik yükleme hatası: {e}")

    def setup_ui(self):
        self.main_notebook = ttk.Notebook(self.root)
        self.main_notebook.pack(fill="both", expand=True, padx=12, pady=12)

        self.tab_register = ttk.Frame(self.main_notebook)
        self.main_notebook.add(self.tab_register, text="  Öğrenci Kayıt İşlemleri  ")

        self.tab_general_list = ttk.Frame(self.main_notebook)
        self.main_notebook.add(self.tab_general_list, text="  Genel Liste & Arama  ")

        self.tab_groups = ttk.Frame(self.main_notebook)
        self.main_notebook.add(self.tab_groups, text="  Branş Grupları  ")

        self.tab_weekly_schedule = ttk.Frame(self.main_notebook)
        self.main_notebook.add(self.tab_weekly_schedule, text="  Haftalık Günlük Program  ")

        self.tab_attendance = ttk.Frame(self.main_notebook)
        self.main_notebook.add(self.tab_attendance, text="  Yoklama & Günlük Takip  ")

        self.tab_payments = ttk.Frame(self.main_notebook)
        self.main_notebook.add(self.tab_payments, text="  Ay Ay Ödeme & Aidat Takibi 🔒  ")

        self.setup_register_tab()
        self.setup_general_list_tab()
        self.setup_groups_tab()
        self.setup_weekly_schedule_tab()
        self.setup_attendance_tab()
        self.setup_payments_tab()
        
        self.refresh_main_table()
        self.refresh_all_groups()

    def setup_register_tab(self):
        main_reg_frame = ttk.Frame(self.tab_register, padding=12)
        main_reg_frame.pack(fill="both", expand=True)

        header_frame = ttk.Frame(main_reg_frame)
        header_frame.pack(fill="x", padx=5, pady=(0, 10))

        if PIL_AVAILABLE and os.path.exists(self.LOGO_FILE):
            try:
                img = Image.open(self.LOGO_FILE)
                img = img.resize((70, 70), Image.Resampling.LANCZOS)
                self.logo_img_ref = ImageTk.PhotoImage(img)
                lbl_logo = ttk.Label(header_frame, image=self.logo_img_ref)
                lbl_logo.pack(side="left", padx=(0, 15))
            except Exception as e:
                print(f"Logo gösterilemedi: {e}")

        ttk.Label(header_frame, text="SPOR KULÜBÜ ÜYE YÖNETİM PANELİ", font=('Segoe UI', 16, 'bold'), foreground='#1E293B').pack(side="left", anchor="center")

        form_container = ttk.LabelFrame(main_reg_frame, text="  Öğrenci Kayıt ve Bilgi Güncelleme Formu  ", padding=15)
        form_container.pack(fill="both", expand=True, padx=5, pady=5)

        left_col = ttk.Frame(form_container)
        left_col.pack(side="left", fill="both", expand=True, padx=15)

        right_col = ttk.Frame(form_container)
        right_col.pack(side="left", fill="both", expand=True, padx=15)

        # --- SOL SÜTUN ---
        ttk.Label(left_col, text="--- ÖĞRENCİ BİLGİLERİ ---", font=('Segoe UI', 11, 'bold'), foreground='#0F172A').pack(anchor="w", pady=(0, 6))
        
        self.form_vars = {}
        fields_student = [
            ("Ad Soyad:", "txt_name"),
            ("TC Kimlik No:", "txt_tc"),
            ("İletişim 1:", "txt_phone1"),
            ("İletişim 2:", "txt_phone2"),
            ("Kronik Hastalık (Varsa):", "txt_chronic"),
        ]

        for label_text, var_name in fields_student:
            row_f = ttk.Frame(left_col)
            row_f.pack(fill="x", pady=3)
            ttk.Label(row_f, text=label_text, width=22, anchor="w").pack(side="left")
            entry = ttk.Entry(row_f, width=25, font=('Segoe UI', 10, 'bold'))
            entry.pack(side="left", fill="x", expand=True)
            self.form_vars[var_name] = entry

        row_f = ttk.Frame(left_col)
        row_f.pack(fill="x", pady=3)
        ttk.Label(row_f, text="Doğum Tar. (gg/aa/yyyy):", width=22, anchor="w").pack(side="left")
        entry_birth = ttk.Entry(row_f, width=25, font=('Segoe UI', 10, 'bold'))
        entry_birth.insert(0, datetime.now().strftime('%d/%m/%Y'))
        entry_birth.pack(side="left", fill="x", expand=True)
        self.form_vars["txt_birth"] = entry_birth

        row_f = ttk.Frame(left_col)
        row_f.pack(fill="x", pady=3)
        ttk.Label(row_f, text="Kayıt Tar. (gg/aa/yyyy):", width=22, anchor="w").pack(side="left")
        entry_reg = ttk.Entry(row_f, width=25, font=('Segoe UI', 10, 'bold'))
        entry_reg.insert(0, datetime.now().strftime('%d/%m/%Y'))
        entry_reg.pack(side="left", fill="x", expand=True)
        self.form_vars["txt_reg"] = entry_reg

        row_f = ttk.Frame(left_col)
        row_f.pack(fill="x", pady=3)
        ttk.Label(row_f, text="Grup / Branş:", width=22, anchor="w").pack(side="left")
        self.combo_group = ttk.Combobox(row_f, values=self.groups, width=23, state="readonly", font=('Segoe UI', 10, 'bold'))
        self.combo_group.current(0)
        self.combo_group.pack(side="left")

        row_f = ttk.Frame(left_col)
        row_f.pack(fill="x", pady=3)
        ttk.Label(row_f, text="Seans / Saat:", width=22, anchor="w").pack(side="left")
        self.combo_session = ttk.Combobox(row_f, values=self.sessions, width=23, state="readonly", font=('Segoe UI', 10, 'bold'))
        self.combo_session.current(0)
        self.combo_session.pack(side="left")

        row_f = ttk.Frame(left_col)
        row_f.pack(fill="x", pady=3)
        ttk.Label(row_f, text="Haftanın Günleri:", width=22, anchor="nw").pack(side="left")
        
        self.listbox_days = tk.Listbox(
            row_f, 
            selectmode=tk.MULTIPLE, 
            height=7, 
            width=23, 
            exportselection=False, 
            font=('Segoe UI', 10, 'bold'), 
            bg='#FFFFFF', 
            fg='#0F172A',
            selectbackground='#334155',
            selectforeground='#FFFFFF',
            bd=1,
            relief="solid"
        )
        for day in self.days_list:
            self.listbox_days.insert(tk.END, f"  {day}")
        self.listbox_days.pack(side="left", fill="x", expand=True)

        # --- SAĞ SÜTUN ---
        ttk.Label(right_col, text="--- ÜYELİK & ÖDEME BİLGİLERİ ---", font=('Segoe UI', 11, 'bold'), foreground='#0F172A').pack(anchor="w", pady=(0, 6))

        row_f = ttk.Frame(right_col)
        row_f.pack(fill="x", pady=3)
        ttk.Label(row_f, text="Üyelik Süresi (Ay):", width=22, anchor="w").pack(side="left")
        self.combo_duration = ttk.Combobox(row_f, values=self.duration_options, width=23, state="readonly", font=('Segoe UI', 10, 'bold'))
        self.combo_duration.current(0)
        self.combo_duration.pack(side="left")

        row_f = ttk.Frame(right_col)
        row_f.pack(fill="x", pady=3)
        ttk.Label(row_f, text="Üyelik Durumu:", width=22, anchor="w").pack(side="left")
        self.combo_membership_status = ttk.Combobox(row_f, values=["Aktif", "Donduruldu"], width=23, state="readonly", font=('Segoe UI', 10, 'bold'))
        self.combo_membership_status.current(0)
        self.combo_membership_status.pack(side="left")

        row_f = ttk.Frame(right_col)
        row_f.pack(fill="x", pady=3)
        ttk.Label(row_f, text="Aylık Tutar (TL):", width=22, anchor="w").pack(side="left")
        entry_fee = ttk.Entry(row_f, width=25, font=('Segoe UI', 10, 'bold'))
        entry_fee.insert(0, "0")
        entry_fee.pack(side="left", fill="x", expand=True)
        self.form_vars["txt_fee"] = entry_fee

        row_f = ttk.Frame(right_col)
        row_f.pack(fill="x", pady=3)
        ttk.Label(row_f, text="Son Ödeme Tar. (gg/aa/yyyy):", width=22, anchor="w").pack(side="left")
        entry_pay_date = ttk.Entry(row_f, width=25, font=('Segoe UI', 10, 'bold'))
        entry_pay_date.insert(0, datetime.now().strftime('%d/%m/%Y'))
        entry_pay_date.pack(side="left", fill="x", expand=True)
        self.form_vars["txt_pay_date"] = entry_pay_date

        row_f = ttk.Frame(right_col)
        row_f.pack(fill="x", pady=3)
        ttk.Label(row_f, text="Ödeme Durumu:", width=22, anchor="w").pack(side="left")
        self.combo_pay_status = ttk.Combobox(row_f, values=["Ödendi", "Ödenmedi / Gecikti"], width=23, state="readonly", font=('Segoe UI', 10, 'bold'))
        self.combo_pay_status.current(1)
        self.combo_pay_status.pack(side="left")

        ttk.Label(right_col, text="--- VELİ BİLGİLERİ ---", font=('Segoe UI', 11, 'bold'), foreground='#0F172A').pack(anchor="w", pady=(12, 6))

        fields_parent = [
            ("Veli Ad Soyad:", "txt_parent_name"),
            ("Veli Mesleği:", "txt_parent_job"),
            ("Veli İletişim 1:", "txt_parent_phone1"),
            ("Veli İletişim 2:", "txt_parent_phone2"),
        ]

        for label_text, var_name in fields_parent:
            row_f = ttk.Frame(right_col)
            row_f.pack(fill="x", pady=3)
            ttk.Label(row_f, text=label_text, width=22, anchor="w").pack(side="left")
            entry = ttk.Entry(row_f, width=25, font=('Segoe UI', 10, 'bold'))
            entry.pack(side="left", fill="x", expand=True)
            self.form_vars[var_name] = entry

        btn_frame = ttk.Frame(form_container)
        btn_frame.pack(fill="x", pady=15)

        ttk.Button(btn_frame, text="✨ Yeni Kayıt", command=self.prepare_new_student_registration).pack(side="left", expand=True, padx=5, ipady=4)
        ttk.Button(btn_frame, text="💾 Kaydet / Güncelle", command=self.add_or_update_student).pack(side="left", expand=True, padx=5, ipady=4)
        ttk.Button(btn_frame, text="🗑️ Bu Üyeyi Sil", command=self.delete_current_form_student).pack(side="left", expand=True, padx=5, ipady=4)
        ttk.Button(btn_frame, text="🧹 Formu Temizle", command=self.clear_form).pack(side="left", expand=True, padx=5, ipady=4)

    def prepare_new_student_registration(self):
        self.clear_form()
        messagebox.showinfo("Yeni Kayıt Modu", "Form temizlendi. Artık yeni bir öğrenci kaydı oluşturabilirsiniz.")

    def setup_general_list_tab(self):
        list_main = ttk.Frame(self.tab_general_list, padding=12)
        list_main.pack(fill="both", expand=True)

        toolbar = ttk.LabelFrame(list_main, text="  Arama ve İşlemler  ", padding=10)
        toolbar.pack(fill="x", padx=5, pady=5)

        ttk.Label(toolbar, text="🔍 Öğrenci Ara (Ad / Soyad):", font=('Segoe UI', 10, 'bold')).pack(side="left", padx=5)
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *args: self.filter_students())
        ttk.Entry(toolbar, textvariable=self.search_var, width=25, font=('Segoe UI', 10, 'bold')).pack(side="left", padx=5)

        ttk.Button(toolbar, text="✏️ Kayıt Sekmesinde Düzenle", command=self.go_to_edit_student).pack(side="left", padx=10)
        ttk.Button(toolbar, text="📥 Excel'den Yükle", command=self.import_excel).pack(side="left", padx=5)
        ttk.Button(toolbar, text="📤 Excel'e Aktar", command=self.export_excel).pack(side="left", padx=5)
        ttk.Button(toolbar, text="📄 Üye Formu Yazdır (PDF)", command=self.generate_pdf_form).pack(side="left", padx=5)
        ttk.Button(toolbar, text="❌ İşaretli Öğrencileri Sil", command=self.delete_selected_students).pack(side="right", padx=5)

        table_frame = ttk.LabelFrame(list_main, text="  Tüm Kayıtlı Öğrenciler Listesi (Yanındaki kutucuktan seçebilir, çift tıklayarak düzenleyebilirsiniz)  ", padding=10)
        table_frame.pack(fill="both", expand=True, padx=5, pady=5)

        tree_scroll_y = ttk.Scrollbar(table_frame)
        tree_scroll_y.pack(side="right", fill="y")
        tree_scroll_x = ttk.Scrollbar(table_frame, orient="horizontal")
        tree_scroll_x.pack(side="bottom", fill="x")

        self.tree = ttk.Treeview(
            table_frame, 
            columns=self.columns, 
            show="headings",
            yscrollcommand=tree_scroll_y.set,
            xscrollcommand=tree_scroll_x.set
        )
        tree_scroll_y.config(command=self.tree.yview)
        tree_scroll_x.config(command=self.tree.xview)

        for col in self.columns:
            self.tree.heading(col, text=col)
            if col == "Seç":
                self.tree.column(col, width=50, anchor="center")
            else:
                self.tree.column(col, width=115, anchor="center")

        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<Button-1>", self.on_tree_click_checkbox)
        self.tree.bind("<Double-1>", self.on_student_double_click)

    def on_tree_click_checkbox(self, event):
        region = self.tree.identify("region", event.x, event.y)
        if region == "cell":
            column = self.tree.identify_column(event.x)
            if column == "#1":
                item = self.tree.identify_row(event.y)
                if item:
                    values = list(self.tree.item(item, 'values'))
                    student_id = values[1]
                    
                    if values[0] == "[ ]":
                        values[0] = "[X]"
                        self.selected_student_ids.add(str(student_id))
                    else:
                        values[0] = "[ ]"
                        self.selected_student_ids.discard(str(student_id))
                        
                    self.tree.item(item, values=values)

    def setup_groups_tab(self):
        top_bar = ttk.Frame(self.tab_groups, padding=5)
        top_bar.pack(fill="x")
        ttk.Button(top_bar, text="📄 Aktif Branş Listesini PDF Olarak Kaydet", command=self.export_group_pdf).pack(side="right", padx=5)

        self.group_notebook = ttk.Notebook(self.tab_groups)
        self.group_notebook.pack(fill="both", expand=True, padx=5, pady=5)

        self.group_trees = {}

        for group_name in self.groups:
            frame = ttk.Frame(self.group_notebook)
            self.group_notebook.add(frame, text=f" {group_name} ")

            filter_frame = ttk.LabelFrame(frame, text="  Gün ve Seans Filtreleme  ", padding=10)
            filter_frame.pack(fill="x", padx=5, pady=5)

            ttk.Label(filter_frame, text="Gün Seçiniz:").pack(side="left", padx=5)
            combo_day_filter = ttk.Combobox(filter_frame, values=["Tüm Günler"] + self.days_list, state="readonly", width=15, font=('Segoe UI', 10, 'bold'))
            combo_day_filter.current(0)
            combo_day_filter.pack(side="left", padx=5)

            ttk.Label(filter_frame, text="Seans Seçiniz:").pack(side="left", padx=5)
            combo_ses_filter = ttk.Combobox(filter_frame, values=["Tüm Seanslar"] + self.sessions, state="readonly", width=18, font=('Segoe UI', 10, 'bold'))
            combo_ses_filter.current(0)
            combo_ses_filter.pack(side="left", padx=5)

            table_frame = ttk.Frame(frame)
            table_frame.pack(fill="both", expand=True, padx=5, pady=5)

            tree_scroll = ttk.Scrollbar(table_frame)
            tree_scroll.pack(side="right", fill="y")

            group_cols = ["ID", "Ad Soyad", "TC No", "Haftanın Günleri", "Seans / Saat", "Üyelik Süresi", "Üyelik Durumu", "İletişim 1", "Veli Ad Soyad"]
            tree_g = ttk.Treeview(table_frame, columns=group_cols, show="headings", yscrollcommand=tree_scroll.set)
            tree_scroll.config(command=tree_g.yview)

            for col in group_cols:
                tree_g.heading(col, text=col)
                tree_g.column(col, width=125, anchor="center")

            tree_g.pack(fill="both", expand=True)

            self.group_trees[group_name] = (tree_g, combo_day_filter, combo_ses_filter)

            combo_day_filter.bind("<<ComboboxSelected>>", lambda e, g=group_name: self.refresh_group_tab(g))
            combo_ses_filter.bind("<<ComboboxSelected>>", lambda e, g=group_name: self.refresh_group_tab(g))

    def setup_weekly_schedule_tab(self):
        outer_frame = ttk.Frame(self.tab_weekly_schedule, padding=12)
        outer_frame.pack(fill="both", expand=True)

        top_bar = ttk.Frame(outer_frame)
        top_bar.pack(fill="x", pady=5)
        ttk.Button(top_bar, text="Programı Yenile", command=self.refresh_weekly_schedule).pack(side="left", padx=5)
        ttk.Button(top_bar, text="📄 Haftalık Programı PDF Olarak Kaydet", command=self.export_schedule_pdf).pack(side="right", padx=5)
        ttk.Label(top_bar, text=" (Tek ekranda haftalık görünüm - Otomatik güncellenir)", foreground='#64748B').pack(side="left", padx=10)

        grid_container = ttk.Frame(outer_frame)
        grid_container.pack(fill="both", expand=True, pady=5)

        for i in range(3):
            grid_container.columnconfigure(i, weight=1)
        grid_container.rowconfigure(0, weight=1)
        grid_container.rowconfigure(1, weight=1)
        grid_container.rowconfigure(2, weight=1)

        grid_positions = {
            "Pazartesi": (0, 0), "Salı": (0, 1), "Çarşamba": (0, 2),
            "Perşembe": (1, 0), "Cuma": (1, 1), "Cumartesi": (1, 2),
            "Pazar": (2, 0)
        }

        self.day_boxes = {}
        for day, pos in grid_positions.items():
            box_frame = ttk.LabelFrame(grid_container, text=f"  {day}  ", padding=5)
            
            if day == "Pazar":
                box_frame.grid(row=pos[0], column=pos[1], columnspan=3, padx=5, pady=5, sticky="nsew")
            else:
                box_frame.grid(row=pos[0], column=pos[1], padx=5, pady=5, sticky="nsew")

            tree_cols = ["Seans", "Ad Soyad", "Branş", "İletişim"]
            tree_d = ttk.Treeview(box_frame, columns=tree_cols, show="headings", height=7)
            
            for col in tree_cols:
                tree_d.heading(col, text=col)
                if col == "Seans":
                    tree_d.column(col, width=85, anchor="center")
                elif col == "Ad Soyad":
                    tree_d.column(col, width=105, anchor="center")
                elif col == "Branş":
                    tree_d.column(col, width=95, anchor="center")
                else:
                    tree_d.column(col, width=85, anchor="center")

            tree_d.pack(fill="both", expand=True)
            self.day_boxes[day] = tree_d

        self.refresh_weekly_schedule()

    def refresh_weekly_schedule(self):
        """Pazartesi ve Pazar çakışması tam eşleşme kontrolü ile çözüldü."""
        for day, tree in self.day_boxes.items():
            for row in tree.get_children():
                tree.delete(row)

            for _, row in self.df.iterrows():
                student_days_raw = str(row["Haftanın Günleri"])
                # Tam kelime eşleşmesi için virgülle ayrıştırıyoruz
                student_days = [d.strip() for d in student_days_raw.split(",")]
                if day in student_days:
                    tree.insert("", "end", values=[
                        row["Seans / Saat"], row["Ad Soyad"], row["Grup / Branş"], row["İletişim 1"]
                    ])

    def setup_attendance_tab(self):
        att_main = ttk.Frame(self.tab_attendance, padding=12)
        att_main.pack(fill="both", expand=True)

        top_ctrl = ttk.LabelFrame(att_main, text="  Yoklama Tarihi ve Gün Seçimi  ", padding=10)
        top_ctrl.pack(fill="x", padx=5, pady=5)

        ttk.Label(top_ctrl, text="Tarih (gg/aa/yyyy):").pack(side="left", padx=5)
        self.entry_att_date = ttk.Entry(top_ctrl, width=15, font=('Segoe UI', 10, 'bold'))
        self.entry_att_date.insert(0, datetime.now().strftime('%d/%m/%Y'))
        self.entry_att_date.pack(side="left", padx=5)

        ttk.Label(top_ctrl, text="Haftanın Günü:").pack(side="left", padx=15)
        self.combo_att_day = ttk.Combobox(top_ctrl, values=self.days_list, state="readonly", width=15, font=('Segoe UI', 10, 'bold'))
        self.combo_att_day.current(0)
        self.combo_att_day.pack(side="left", padx=5)

        ttk.Button(top_ctrl, text="Listeyi Getir / Güncelle", command=self.load_attendance_list).pack(side="left", padx=15)
        ttk.Button(top_ctrl, text="Yoklamayı Kaydet", command=self.save_attendance).pack(side="left", padx=5)
        ttk.Button(top_ctrl, text="📄 Yoklama Listesini PDF Yap", command=self.export_attendance_pdf).pack(side="right", padx=5)

        table_frame = ttk.LabelFrame(att_main, text="  O Günün Öğrenci Yoklama Listesi (Çift tıklayarak geçmiş katılım detayını açabilirsiniz)  ", padding=10)
        table_frame.pack(fill="both", expand=True, padx=5, pady=5)

        att_cols = ["ID", "Ad Soyad", "Branş", "Seans / Saat", "Yoklama Durumu"]
        
        tree_scroll = ttk.Scrollbar(table_frame)
        tree_scroll.pack(side="right", fill="y")

        self.tree_att = ttk.Treeview(table_frame, columns=att_cols, show="headings", yscrollcommand=tree_scroll.set)
        tree_scroll.config(command=self.tree_att.yview)

        for col in att_cols:
            self.tree_att.heading(col, text=col)
            self.tree_att.column(col, width=150, anchor="center")

        self.tree_att.tag_configure("geldi", background="#DCFCE7", foreground="#166534")
        self.tree_att.tag_configure("gelmedi", background="#FEE2E2", foreground="#991B1B")

        self.tree_att.pack(fill="both", expand=True)
        self.tree_att.bind("<Double-1>", self.on_attendance_double_click)

        ttk.Label(table_frame, text="* İpucu: Çift tıklayarak öğrencinin 'Tüm Geçmiş Katılım Geçmişi' penceresini açabilir, duruma müdahale edebilir veya PDF katılım raporu alabilirsiniz.", foreground='#64748B').pack(anchor="w", pady=5)

    def load_attendance_list(self):
        for row in self.tree_att.get_children():
            self.tree_att.delete(row)

        sel_day = self.combo_att_day.get()
        sel_date = self.entry_att_date.get().strip() or datetime.now().strftime('%d/%m/%Y')

        for _, row in self.df.iterrows():
            student_days = [d.strip() for d in str(row["Haftanın Günleri"]).split(",")]
            if sel_day in student_days:
                student_id = str(row["ID"])
                key = (student_id, sel_date)
                rec = self.attendance_records.get(key, 'Geldi')
                status = rec.get('status', 'Geldi') if isinstance(rec, dict) else str(rec)
                
                tag = "geldi" if status == "Geldi" else "gelmedi"
                
                self.tree_att.insert("", "end", values=[
                    student_id, row["Ad Soyad"], row["Grup / Branş"], row["Seans / Saat"], status
                ], tags=(tag,))

    def on_attendance_double_click(self, event):
        selected = self.tree_att.selection()
        if not selected:
            return
        item = selected[0]
        vals = self.tree_att.item(item, 'values')
        student_id = str(vals[0])
        student_name = str(vals[1])
        
        # Öğrencinin geçmiş katılım detay sayfasını yeni pencerede aç
        self.open_student_attendance_history_window(student_id, student_name)

    def open_student_attendance_history_window(self, student_id, student_name):
        """Öğrencinin geçmiş katılım detaylarını gösteren gelişmiş pencere."""
        win = tk.Toplevel(self.root)
        win.title(f"Öğrenci Ders Katılım Geçmişi - {student_name} (ID: {student_id})")
        win.geometry("750x550")
        win.transient(self.root)

        header = ttk.Frame(win, padding=10)
        header.pack(fill="x")
        ttk.Label(header, text=f"👤 {student_name} - DERS KATILIM DETAYLARI", font=('Segoe UI', 13, 'bold'), foreground='#0F172A').pack(side="left")

        btn_bar = ttk.Frame(win, padding=5)
        btn_bar.pack(fill="x", padx=10)

        table_frame = ttk.Frame(win, padding=10)
        table_frame.pack(fill="both", expand=True)

        cols = ["Tarih", "Grup / Branş", "Seans / Saat", "Katılım Durumu"]
        tree_hist = ttk.Treeview(table_frame, columns=cols, show="headings")
        
        for c in cols:
            tree_hist.heading(c, text=c)
            tree_hist.column(c, width=160, anchor="center")

        tree_hist.tag_configure("geldi", background="#DCFCE7", foreground="#166534")
        tree_hist.tag_configure("gelmedi", background="#FEE2E2", foreground="#991B1B")

        tree_hist.pack(fill="both", expand=True)

        # Öğrencinin geçmiş tüm verilerini getir
        history_list = []
        for (sid, dt), val in self.attendance_records.items():
            if str(sid) == str(student_id):
                if isinstance(val, dict):
                    st = val.get('status', 'Geldi')
                    br = val.get('branch', 'Genel Branş')
                    se = val.get('session', 'Genel Seans')
                else:
                    st = str(val)
                    br = "Genel Branş"
                    se = "Genel Seans"
                history_list.append((dt, br, se, st))

        # Tarihe göre sırala
        history_list.sort(key=lambda x: x[0], reverse=True)

        for dt, br, se, st in history_list:
            tag = "geldi" if st == "Geldi" else "gelmedi"
            tree_hist.insert("", "end", values=[dt, br, se, st], tags=(tag,))

        if not history_list:
            ttk.Label(table_frame, text="Bu öğrenci için henüz kaydedilmiş geçmiş yoklama verisi bulunmuyor.", foreground='#64748B').pack(pady=20)

        # Durum Değiştirme Butonu
        def toggle_hist_status():
            sel = tree_hist.selection()
            if not sel:
                messagebox.showwarning("Seçim Yapılmadı", "Lütfen durumunu değiştirmek istediğiniz satırı seçin.", parent=win)
                return
            it = sel[0]
            v = list(tree_hist.item(it, 'values'))
            dt = v[0]
            curr_st = v[3]
            new_st = "Gelmedi" if curr_st == "Geldi" else "Geldi"
            v[3] = new_st
            
            tag = "geldi" if new_st == "Geldi" else "gelmedi"
            tree_hist.item(it, values=v, tags=(tag,))
            
            # Ana hafızayı güncelle
            self.attendance_records[(student_id, dt)] = {'status': new_st, 'branch': v[1], 'session': v[2]}
            self.save_to_storage()
            self.load_attendance_list()

        ttk.Button(btn_bar, text="🔄 Durumu Değiştir (Geldi / Gelmedi)", command=toggle_hist_status).pack(side="left", padx=5)
        ttk.Button(btn_bar, text="📄 Katılım Raporunu PDF Olarak İndir", command=lambda: self.export_single_student_attendance_pdf(student_name, student_id, history_list)).pack(side="right", padx=5)

    def export_single_student_attendance_pdf(self, student_name, student_id, history_list):
        """Öğrencinin şahsi yoklama/katılım dökümünü PDF yapar."""
        if not REPORTLAB_AVAILABLE:
            messagebox.showerror("Hata", "reportlab kütüphanesi yüklü değil.")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".pdf", initialfile=f"Katilim_Raporu_{student_name}.pdf", filetypes=[("PDF Dosyası", "*.pdf")])
        if not file_path:
            return

        try:
            doc = SimpleDocTemplate(file_path, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
            styles = getSampleStyleSheet()
            font_name = FONT_NAME

            story = [
                Paragraph(fix_tr(f"<b>{student_name} - DERS KATILIM VE YOKLAMA GEÇMİŞİ</b>"), styles['Heading1']),
                Spacer(1, 5),
                Paragraph(fix_tr(f"Öğrenci ID: {student_id} | Rapor Tarihi: {datetime.now().strftime('%d/%m/%Y')}"), styles['Normal']),
                Spacer(1, 15)
            ]

            table_data = [["Tarih", "Grup / Branş", "Seans / Saat", "Katılım Durumu"]]
            for dt, br, se, st in history_list:
                table_data.append([fix_tr(dt), fix_tr(br), fix_tr(se), fix_tr(st)])

            t = Table(table_data, colWidths=[110, 160, 140, 110])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.darkslateblue),
                ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                ('FONTNAME', (0,0), (-1,-1), font_name),
                ('FONTSIZE', (0,0), (-1,-1), 9),
                ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('PADDING', (0,0), (-1,-1), 5),
            ]))
            story.append(t)
            doc.build(story)
            messagebox.showinfo("Başarılı", f"Öğrenci katılım raporu PDF olarak kaydedildi:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Hata", f"PDF oluşturulamadı: {str(e)}")

    def save_attendance(self):
        sel_date = self.entry_att_date.get().strip() or datetime.now().strftime('%d/%m/%Y')
        for item in self.tree_att.get_children():
            vals = self.tree_att.item(item, 'values')
            student_id = vals[0]
            branch = vals[2]
            session = vals[3]
            status = vals[4]
            self.attendance_records[(student_id, sel_date)] = {
                'status': status, 
                'branch': branch, 
                'session': session
            }

        self.save_to_storage()
        messagebox.showinfo("Başarılı", f"{sel_date} tarihli yoklama kalıcı olarak kaydedildi.")

    # --- ÖDEME VE ŞİFRE/YETKİLENDİRME PANELDİ ---
    def setup_payments_tab(self):
        self.pay_container = ttk.Frame(self.tab_payments)
        self.pay_container.pack(fill="both", expand=True, padx=12, pady=12)

        # 1. ŞİFRELEME GİRİŞ EKRANI
        self.login_frame = ttk.LabelFrame(self.pay_container, text="  🔒 Yetkili Girişi (Aidat & Ödeme Ekranı Kilitli)  ", padding=20)
        self.login_frame.pack(anchor="center", expand=True, pady=40)

        ttk.Label(self.login_frame, text="Bu ekrana yalnızca yetkili kullanıcı erişebilir.", font=('Segoe UI', 10, 'italic'), foreground='#64748B').pack(pady=(0, 15))

        f_user = ttk.Frame(self.login_frame)
        f_user.pack(fill="x", pady=5)
        ttk.Label(f_user, text="Kullanıcı Adı:", width=15, anchor="w").pack(side="left")
        self.entry_login_user = ttk.Entry(f_user, width=25, font=('Segoe UI', 10, 'bold'))
        self.entry_login_user.pack(side="left")

        f_pass = ttk.Frame(self.login_frame)
        f_pass.pack(fill="x", pady=5)
        ttk.Label(f_pass, text="Şifre:", width=15, anchor="w").pack(side="left")
        self.entry_login_pass = ttk.Entry(f_pass, width=25, show="*", font=('Segoe UI', 10, 'bold'))
        self.entry_login_pass.pack(side="left")

        btn_login_row = ttk.Frame(self.login_frame)
        btn_login_row.pack(fill="x", pady=(15, 0))

        ttk.Button(btn_login_row, text="🔓 Giriş Yap", command=self.check_payment_login).pack(side="left", padx=5, expand=True)
        ttk.Button(btn_login_row, text="🔑 Şifremi Sıfırla / Değiştir", command=self.reset_password_with_root).pack(side="right", padx=5, expand=True)

        # 2. ÖDEME YÖNETİM EKRANI (BAŞLANGIÇTA GİZLİ)
        self.payment_content_frame = ttk.Frame(self.pay_container)

        top_p_frame = ttk.LabelFrame(self.payment_content_frame, text="  Ay Ay Ödeme & Fiyat Kontrol Panel  ", padding=10)
        top_p_frame.pack(fill="x", padx=5, pady=5)

        search_pay_frame = ttk.Frame(top_p_frame)
        search_pay_frame.pack(fill="x", pady=5)

        ttk.Label(search_pay_frame, text="🔍 Ödeme Listesinde Ara (Ad / Soyad):", font=('Segoe UI', 10, 'bold')).pack(side="left", padx=3)
        self.search_pay_var = tk.StringVar()
        self.search_pay_var.trace("w", lambda *args: self.filter_monthly_payments())
        ttk.Entry(search_pay_frame, textvariable=self.search_pay_var, width=22, font=('Segoe UI', 10, 'bold')).pack(side="left", padx=3)

        btn_row = ttk.Frame(top_p_frame)
        btn_row.pack(fill="x", pady=5)

        ttk.Button(btn_row, text="Listeyi Yenile", command=self.load_monthly_payments).pack(side="left", padx=5)
        ttk.Button(btn_row, text="⚠️ Borçluları Öne Getir", command=self.sort_unpaid_students_first).pack(side="left", padx=5)
        ttk.Button(btn_row, text="Seçili 'Ödendi' Yap", command=lambda: self.mark_monthly_payment("Ödendi")).pack(side="left", padx=5)
        ttk.Button(btn_row, text="Seçili 'Ödenmedi' Yap", command=lambda: self.mark_monthly_payment("Ödenmedi")).pack(side="left", padx=5)
        ttk.Button(btn_row, text="🔐 Şifre/Kullanıcı Değiştir", command=self.change_credentials_popup).pack(side="left", padx=10)
        ttk.Button(btn_row, text="🔒 Çıkış Yap / Kilitle", command=self.lock_payment_tab).pack(side="left", padx=5)
        ttk.Button(btn_row, text="📄 Ödeme Raporu (PDF)", command=self.export_payments_pdf).pack(side="right", padx=5)

        list_p_frame = ttk.LabelFrame(self.payment_content_frame, text="  Öğrenci 12 Aylık Aidat ve Ödeme Takip Matrisi  ", padding=10)
        list_p_frame.pack(fill="both", expand=True, padx=5, pady=5)

        self.pay_cols = ["ID", "Ad Soyad", "Grup / Branş", "Aylık Tutar (TL)"] + self.months_list
        
        tree_scroll_y = ttk.Scrollbar(list_p_frame)
        tree_scroll_y.pack(side="right", fill="y")
        tree_scroll_x = ttk.Scrollbar(list_p_frame, orient="horizontal")
        tree_scroll_x.pack(side="bottom", fill="x")

        self.tree_pay = ttk.Treeview(
            list_p_frame, 
            columns=self.pay_cols, 
            show="headings",
            yscrollcommand=tree_scroll_y.set,
            xscrollcommand=tree_scroll_x.set
        )
        tree_scroll_y.config(command=self.tree_pay.yview)
        tree_scroll_x.config(command=self.tree_pay.xview)

        for col in self.pay_cols:
            self.tree_pay.heading(col, text=col)
            if col in ["ID"]:
                self.tree_pay.column(col, width=50, anchor="center")
            elif col in ["Ad Soyad", "Grup / Branş"]:
                self.tree_pay.column(col, width=125, anchor="center")
            elif col == "Aylık Tutar (TL)":
                self.tree_pay.column(col, width=110, anchor="center")
            else:
                self.tree_pay.column(col, width=80, anchor="center")

        self.tree_pay.pack(fill="both", expand=True)
        self.tree_pay.bind("<Double-1>", self.toggle_monthly_payment)

    def check_payment_login(self):
        usr = self.entry_login_user.get().strip()
        pwd = self.entry_login_pass.get().strip()

        if usr == self.admin_username and pwd == self.admin_password:
            self.is_payment_unlocked = True
            self.login_frame.pack_forget()
            self.payment_content_frame.pack(fill="both", expand=True)
            self.load_monthly_payments()
            self.entry_login_pass.delete(0, tk.END)
        else:
            messagebox.showerror("Hatalı Giriş", "Kullanıcı adı veya şifre yanlış!")

    def lock_payment_tab(self):
        self.is_payment_unlocked = False
        self.payment_content_frame.pack_forget()
        self.login_frame.pack(anchor="center", expand=True, pady=40)
        messagebox.showinfo("Kilitlendi", "Ödeme ekranı başarıyla kilitlendi.")

    def reset_password_with_root(self):
        root_key = simpledialog.askstring("Root Doğrulama", "Lütfen Şifre Sıfırlama Root Kodunu Girin:", show="*")
        if root_key == self.ROOT_RECOVERY_KEY:
            new_user = simpledialog.askstring("Yeni Kullanıcı Adı", "Yeni Kullanıcı Adı Girin:", initialvalue=self.admin_username)
            if new_user:
                new_pass = simpledialog.askstring("Yeni Şifre", "Yeni Şifreyi Girin:", show="*")
                if new_pass:
                    self.admin_username = new_user.strip()
                    self.admin_password = new_pass.strip()
                    self.save_to_storage()
                    messagebox.showinfo("Başarılı", "Kullanıcı adı ve şifreniz başarıyla güncellendi!")
        elif root_key is not None:
            messagebox.showerror("Hata", "Girdiğiniz Root Sıfırlama Kodu Geçersizdir!")

    def change_credentials_popup(self):
        old_pass = simpledialog.askstring("Mevcut Şifre", "Lütfen mevcut şifrenizi girin:", show="*")
        if old_pass == self.admin_password:
            new_user = simpledialog.askstring("Yeni Kullanıcı Adı", "Yeni Kullanıcı Adınızı yazın:", initialvalue=self.admin_username)
            if new_user:
                new_pass = simpledialog.askstring("Yeni Şifre", "Yeni Şifrenizi yazın:", show="*")
                if new_pass:
                    self.admin_username = new_user.strip()
                    self.admin_password = new_pass.strip()
                    self.save_to_storage()
                    messagebox.showinfo("Başarılı", "Giriş bilgileriniz güncellendi ve kaydedildi.")
        elif old_pass is not None:
            messagebox.showerror("Hata", "Mevcut şifre yanlış!")

    def load_monthly_payments(self):
        if not self.is_payment_unlocked:
            return

        for row in self.tree_pay.get_children():
            self.tree_pay.delete(row)

        for _, row in self.df.iterrows():
            student_id = str(row["ID"])
            fee_val = str(row.get("Aylık Tutar", "0")) + " TL"
            row_values = [student_id, row["Ad Soyad"], row["Grup / Branş"], fee_val]
            
            for month in self.months_list:
                key = (student_id, month)
                status = self.monthly_payments.get(key, "Ödenmedi")
                row_values.append(status)

            self.tree_pay.insert("", "end", values=row_values)

    def sort_unpaid_students_first(self):
        current_month_idx = datetime.now().month - 1
        
        for row in self.tree_pay.get_children():
            self.tree_pay.delete(row)

        all_rows_data = []

        for _, row in self.df.iterrows():
            student_id = str(row["ID"])
            fee_val = str(row.get("Aylık Tutar", "0")) + " TL"
            row_values = [student_id, row["Ad Soyad"], row["Grup / Branş"], fee_val]
            
            unpaid_count = 0
            for idx, month in enumerate(self.months_list):
                key = (student_id, month)
                status = self.monthly_payments.get(key, "Ödenmedi")
                row_values.append(status)
                
                if idx <= current_month_idx and status == "Ödenmedi":
                    unpaid_count += 1

            all_rows_data.append((unpaid_count, row_values))

        all_rows_data.sort(key=lambda x: x[0], reverse=True)

        for _, row_vals in all_rows_data:
            self.tree_pay.insert("", "end", values=row_vals)

        messagebox.showinfo("Sıralama Tamamlandı", "Borcu olan öğrenciler en üste sıralandı.")

    def filter_monthly_payments(self, *args):
        if not self.is_payment_unlocked:
            return

        query = self.search_pay_var.get().strip().lower()
        for row in self.tree_pay.get_children():
            self.tree_pay.delete(row)

        for _, row in self.df.iterrows():
            student_id = str(row["ID"])
            name = str(row["Ad Soyad"]).lower()
            fee_val = str(row.get("Aylık Tutar", "0")) + " TL"
            
            if not query or query in name:
                row_values = [student_id, row["Ad Soyad"], row["Grup / Branş"], fee_val]
                for month in self.months_list:
                    key = (student_id, month)
                    status = self.monthly_payments.get(key, "Ödenmedi")
                    row_values.append(status)
                self.tree_pay.insert("", "end", values=row_values)

    def toggle_monthly_payment(self, event):
        region = self.tree_pay.identify("region", event.x, event.y)
        if region != "cell":
            return

        column = self.tree_pay.identify_column(event.x)
        col_idx = int(column.replace("#", "")) - 1
        
        if col_idx < 4:
            return

        month_name = self.months_list[col_idx - 4]
        selected = self.tree_pay.selection()
        if not selected:
            return

        item = selected[0]
        values = list(self.tree_pay.item(item, 'values'))
        student_id = values[0]
        current_status = values[col_idx]

        new_status = "Ödenmedi" if current_status == "Ödendi" else "Ödendi"
        values[col_idx] = new_status
        self.tree_pay.item(item, values=values)

        self.monthly_payments[(student_id, month_name)] = new_status
        self.save_to_storage()

    def mark_monthly_payment(self, status_val):
        selected = self.tree_pay.selection()
        if not selected:
            messagebox.showwarning("Seçim Yapılmadı", "Lütfen listeden bir öğrenci seçin.")
            return

        item = selected[0]
        values = list(self.tree_pay.item(item, 'values'))
        student_id = values[0]

        for idx, month in enumerate(self.months_list):
            values[idx + 4] = status_val
            self.monthly_payments[(student_id, month)] = status_val

        self.tree_pay.item(item, values=values)
        self.save_to_storage()
        messagebox.showinfo("Başarılı", f"Öğrencinin tüm aylık ödemeleri '{status_val}' olarak güncellendi ve kaydedildi.")

    def filter_students(self, *args):
        query = self.search_var.get().strip().lower()
        for row in self.tree.get_children():
            self.tree.delete(row)

        for _, row in self.df.iterrows():
            name = str(row["Ad Soyad"]).lower()
            if not query or query in name:
                student_id = str(row["ID"])
                checkbox_val = "[X]" if student_id in self.selected_student_ids else "[ ]"
                row_list = [checkbox_val] + list(row)
                self.tree.insert("", "end", values=row_list)

    def refresh_group_tab(self, group_name):
        tree_g, combo_day, combo_ses = self.group_trees[group_name]

        for row in tree_g.get_children():
            tree_g.delete(row)

        sel_day = combo_day.get()
        sel_ses = combo_ses.get()

        filtered_df = self.df[self.df["Grup / Branş"] == group_name]

        if sel_day != "Tüm Günler":
            filtered_df = filtered_df[filtered_df["Haftanın Günleri"].str.contains(sel_day, na=False)]

        if sel_ses != "Tüm Seanslar":
            filtered_df = filtered_df[filtered_df["Seans / Saat"] == sel_ses]

        for _, row in filtered_df.iterrows():
            tree_g.insert("", "end", values=[
                row["ID"], row["Ad Soyad"], row["TC No"], row["Haftanın Günleri"],
                row["Seans / Saat"], row["Üyelik Süresi"], row["Üyelik Durumu"], row["İletişim 1"], row["Veli Ad Soyad"]
            ])

    def refresh_all_groups(self):
        for g in self.groups:
            self.refresh_group_tab(g)
        self.refresh_weekly_schedule()
        if self.is_payment_unlocked:
            self.load_monthly_payments()

    def add_or_update_student(self):
        name = self.form_vars["txt_name"].get().strip()
        if not name:
            messagebox.showwarning("Eksik Bilgi", "Lütfen en az Ad Soyad alanını doldurun.")
            return

        selected_indices = self.listbox_days.curselection()
        if not selected_indices:
            messagebox.showwarning("Eksik Bilgi", "Lütfen haftanın en az bir gününü seçin.")
            return
        selected_days_list = [self.listbox_days.get(i).strip() for i in selected_indices]
        days_str = ", ".join(selected_days_list)

        duration_val = self.combo_duration.get().strip()
        if not duration_val:
            duration_val = "12 Ay (1 Yıl)"

        if self.editing_student_id:
            item_id = str(self.editing_student_id)
        else:
            if not self.df.empty:
                try:
                    max_id = int(self.df['ID'].max())
                    item_id = str(max_id + 1).zfill(4)
                except Exception:
                    item_id = str(len(self.df) + 1).zfill(4)
            else:
                item_id = "0001"

        new_data = {
            "ID": str(item_id),
            "Ad Soyad": name,
            "TC No": self.form_vars["txt_tc"].get().strip(),
            "Doğum Tarihi": self.form_vars["txt_birth"].get().strip(),
            "İletişim 1": self.form_vars["txt_phone1"].get().strip(),
            "İletişim 2": self.form_vars["txt_phone2"].get().strip(),
            "Kayıt Tarihi": self.form_vars["txt_reg"].get().strip(),
            "Kronik Hastalık": self.form_vars["txt_chronic"].get().strip(),
            "Veli Ad Soyad": self.form_vars["txt_parent_name"].get().strip(),
            "Veli Meslek": self.form_vars["txt_parent_job"].get().strip(),
            "Veli İletişim 1": self.form_vars["txt_parent_phone1"].get().strip(),
            "Veli İletişim 2": self.form_vars["txt_parent_phone2"].get().strip(),
            "Grup / Branş": self.combo_group.get(),
            "Seans / Saat": self.combo_session.get(),
            "Haftanın Günleri": days_str,
            "Üyelik Süresi": duration_val,
            "Üyelik Durumu": self.combo_membership_status.get(),
            "Aylık Tutar": self.form_vars["txt_fee"].get().strip() or "0",
            "Son Ödeme Tarihi": self.form_vars["txt_pay_date"].get().strip(),
            "Ödeme Durumu": self.combo_pay_status.get()
        }

        if self.editing_student_id:
            match_idx = self.df[self.df['ID'] == str(self.editing_student_id)].index
            if not match_idx.empty:
                idx = match_idx[0]
                for k, v in new_data.items():
                    self.df.loc[idx, k] = v
            else:
                self.df = pd.concat([self.df, pd.DataFrame([new_data])], ignore_index=True)
        else:
            self.df = pd.concat([self.df, pd.DataFrame([new_data])], ignore_index=True)

        self.save_to_storage()

        self.refresh_main_table()
        self.refresh_all_groups()
        self.clear_form()
        messagebox.showinfo("Başarılı", "Öğrenci kaydı kalıcı olarak kaydedildi / güncellendi.")

    def delete_student_by_id(self, student_ids):
        if not student_ids:
            return

        str_ids = [str(sid) for sid in student_ids]
        
        self.df = self.df[~self.df['ID'].isin(str_ids)]
        
        for sid in str_ids:
            self.selected_student_ids.discard(sid)
            keys_to_del_att = [k for k in self.attendance_records.keys() if k[0] == sid]
            for k in keys_to_del_att:
                del self.attendance_records[k]
                
            keys_to_del_pay = [k for k in self.monthly_payments.keys() if k[0] == sid]
            for k in keys_to_del_pay:
                del self.monthly_payments[k]

        self.save_to_storage()

        self.refresh_main_table()
        self.refresh_all_groups()

    def delete_current_form_student(self):
        if not self.editing_student_id:
            messagebox.showwarning("Uyarı", "Şu anda formda kayıtlı veya düzenlenecek bir üye seçili değil.")
            return

        if messagebox.askyesno("Onay", f"ID: {self.editing_student_id} olan bu üyenin kaydını tamamen silmek istediğinizden emin misiniz?"):
            target_id = self.editing_student_id
            self.clear_form()
            self.delete_student_by_id([target_id])
            messagebox.showinfo("Başarılı", "Üye kaydı sistemden başarıyla silindi.")

    def delete_selected_students(self):
        if not self.selected_student_ids:
            selected = self.tree.selection()
            if selected:
                for item in selected:
                    vals = self.tree.item(item)['values']
                    if vals:
                        self.selected_student_ids.add(str(vals[1]))

        if not self.selected_student_ids:
            messagebox.showwarning("Seçim Yapılmadı", "Lütfen silmek istediğiniz öğrencilerin yanındaki kutucukları işaretleyin.")
            return

        count = len(self.selected_student_ids)
        if messagebox.askyesno("Onay", f"İşaretlenen {count} öğrenci kaydını silmek istediğinizden emin misiniz?"):
            ids_to_remove = list(self.selected_student_ids)
            self.selected_student_ids.clear()
            self.delete_student_by_id(ids_to_remove)
            messagebox.showinfo("Başarılı", "Seçilen öğrenci kayıtları sistemden silindi.")

    def refresh_main_table(self):
        self.filter_students()

    def clear_form(self):
        self.editing_student_id = None
        for entry in self.form_vars.values():
            if isinstance(entry, ttk.Entry):
                entry.delete(0, tk.END)
        self.form_vars["txt_fee"].insert(0, "0")
        self.form_vars["txt_birth"].insert(0, datetime.now().strftime('%d/%m/%Y'))
        self.form_vars["txt_reg"].insert(0, datetime.now().strftime('%d/%m/%Y'))
        self.form_vars["txt_pay_date"].insert(0, datetime.now().strftime('%d/%m/%Y'))
        self.combo_group.current(0)
        self.combo_session.current(0)
        self.combo_duration.current(0)
        self.combo_membership_status.current(0)
        self.combo_pay_status.current(1)
        self.listbox_days.selection_clear(0, tk.END)
        if self.tree.selection():
            self.tree.selection_remove(self.tree.selection())

    def load_student_to_form(self, item_values):
        if not item_values or len(item_values) < 2:
            return
        
        self.editing_student_id = str(item_values[1])

        self.form_vars["txt_name"].delete(0, tk.END)
        self.form_vars["txt_name"].insert(0, str(item_values[2]))
        
        self.form_vars["txt_tc"].delete(0, tk.END)
        self.form_vars["txt_tc"].insert(0, str(item_values[3]))
        
        self.form_vars["txt_birth"].delete(0, tk.END)
        self.form_vars["txt_birth"].insert(0, str(item_values[4]))

        self.form_vars["txt_phone1"].delete(0, tk.END)
        self.form_vars["txt_phone1"].insert(0, str(item_values[5]))
        
        self.form_vars["txt_phone2"].delete(0, tk.END)
        self.form_vars["txt_phone2"].insert(0, str(item_values[6]))

        self.form_vars["txt_reg"].delete(0, tk.END)
        self.form_vars["txt_reg"].insert(0, str(item_values[7]))

        self.form_vars["txt_chronic"].delete(0, tk.END)
        self.form_vars["txt_chronic"].insert(0, str(item_values[8]))

        self.form_vars["txt_parent_name"].delete(0, tk.END)
        self.form_vars["txt_parent_name"].insert(0, str(item_values[9]))
        
        self.form_vars["txt_parent_job"].delete(0, tk.END)
        self.form_vars["txt_parent_job"].insert(0, str(item_values[10]))
        
        self.form_vars["txt_parent_phone1"].delete(0, tk.END)
        self.form_vars["txt_parent_phone1"].insert(0, str(item_values[11]))
        
        self.form_vars["txt_parent_phone2"].delete(0, tk.END)
        self.form_vars["txt_parent_phone2"].insert(0, str(item_values[12]))

        self.form_vars["txt_fee"].delete(0, tk.END)
        self.form_vars["txt_fee"].insert(0, str(item_values[18]))

        self.form_vars["txt_pay_date"].delete(0, tk.END)
        self.form_vars["txt_pay_date"].insert(0, str(item_values[19]))

        if item_values[13] in self.groups:
            self.combo_group.set(item_values[13])
        if item_values[14] in self.sessions:
            self.combo_session.set(item_values[14])
        
        self.listbox_days.selection_clear(0, tk.END)
        days_in_item = [d.strip() for d in str(item_values[15]).split(",")]
        for idx, day in enumerate(self.days_list):
            if day in days_in_item:
                self.listbox_days.select_set(idx)

        if item_values[16] in self.duration_options:
            self.combo_duration.set(item_values[16])
        if item_values[17] in ["Aktif", "Donduruldu"]:
            self.combo_membership_status.set(item_values[17])
        if item_values[20] in ["Ödendi", "Ödenmedi / Gecikti"]:
            self.combo_pay_status.set(item_values[20])

    def on_student_double_click(self, event):
        selected = self.tree.selection()
        if selected:
            item_values = self.tree.item(selected[0])['values']
            self.load_student_to_form(item_values)
            self.main_notebook.select(self.tab_register)

    def go_to_edit_student(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Seçim Yapılmadı", "Lütfen listeden düzenlenecek öğrenciyi seçin.")
            return
        item_values = self.tree.item(selected[0])['values']
        self.load_student_to_form(item_values)
        self.main_notebook.select(self.tab_register)

    def export_excel(self):
        if self.df.empty:
            messagebox.showwarning("Uyarı", "Dışa aktarılacak veri bulunamadı.")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel Dosyası", "*.xlsx")])
        if file_path:
            try:
                self.df.to_excel(file_path, index=False)
                messagebox.showinfo("Başarılı", f"Veriler Excel'e aktarıldı:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Hata", f"Excel kaydedilemedi: {str(e)}")

    def import_excel(self):
        file_path = filedialog.askopenfilename(filetypes=[("Excel Dosyası", "*.xlsx *.xls")])
        if file_path:
            try:
                imported_df = pd.read_excel(file_path, dtype=str)
                for col in self.df.columns:
                    if col not in imported_df.columns:
                        imported_df[col] = ""
                self.df = imported_df[self.df.columns]
                
                self.save_to_storage()
                self.refresh_main_table()
                self.refresh_all_groups()
                messagebox.showinfo("Başarılı", "Excel verileri yüklendi ve kalıcı olarak depolandı.")
            except Exception as e:
                messagebox.showerror("Hata", f"Excel okunamadı: {str(e)}")

    def generate_pdf_form(self):
        if not REPORTLAB_AVAILABLE:
            messagebox.showerror("Eksik Kütüphane", "reportlab kütüphanesi gerekli.")
            return

        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Seçim Yapılmadı", "Lütfen genel listeden formu yazdırılacak öğrenciyi seçin.")
            return

        item = self.tree.item(selected[0])['values']
        file_path = filedialog.asksaveasfilename(defaultextension=".pdf", initialfile=f"Uye_Formu_{item[1]}.pdf", filetypes=[("PDF Dosyası", "*.pdf")])

        if not file_path:
            return

        try:
            doc = SimpleDocTemplate(file_path, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
            styles = getSampleStyleSheet()

            font_name = FONT_NAME

            title_style = ParagraphStyle(
                'TitleStyle',
                parent=styles['Heading1'],
                fontName=font_name,
                fontSize=18,
                alignment=1,
                spaceAfter=15
            )

            normal_style = styles['Normal']
            normal_style.fontName = font_name
            normal_style.fontSize = 8.5

            heading_style = ParagraphStyle(
                'Heading3Custom',
                parent=styles['Heading3'],
                fontName=font_name
            )

            story = []

            story.append(Paragraph(fix_tr("<b>SPOR KULÜBÜ KAYIT VE ÜYELİK FORMU</b>"), title_style))
            story.append(HRFlowable(width="100%", thickness=1.5, color=colors.navy, spaceAfter=15))

            student_data = [
                [fix_tr("Öğrenci ID:"), fix_tr(str(item[1])), fix_tr("Kayıt Tarihi:"), fix_tr(str(item[7]))],
                [fix_tr("Ad Soyad:"), fix_tr(str(item[2])), fix_tr("Doğum Tarihi:"), fix_tr(str(item[4]))],
                [fix_tr("TC Kimlik No:"), fix_tr(str(item[3])), fix_tr("Grup / Branş:"), fix_tr(str(item[13]))],
                [fix_tr("İletişim 1:"), fix_tr(str(item[5])), fix_tr("Seans / Saat:"), fix_tr(str(item[14]))],
                [fix_tr("Haftanın Günleri:"), fix_tr(str(item[15])), fix_tr("Üyelik Süresi:"), fix_tr(str(item[16]))],
                [fix_tr("Üyelik Durumu:"), fix_tr(str(item[17])), fix_tr("Kronik Hastalık:"), fix_tr(str(item[8]))]
            ]

            t1 = Table(student_data, colWidths=[100, 160, 100, 160])
            t1.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.whitesmoke),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
                ('FONTNAME', (0, 0), (-1, -1), font_name),
                ('PADDING', (0, 0), (-1, -1), 5),
            ]))
            story.append(Paragraph(fix_tr("<b>ÖĞRENCİ BİLGİLERİ</b>"), heading_style))
            story.append(Spacer(1, 5))
            story.append(t1)
            story.append(Spacer(1, 15))

            parent_data = [
                [fix_tr("Veli Ad Soyad:"), fix_tr(str(item[9])), fix_tr("Veli Meslek:"), fix_tr(str(item[10]))],
                [fix_tr("Veli İletişim 1:"), fix_tr(str(item[11])), fix_tr("Veli İletişim 2:"), fix_tr(str(item[12]))],
            ]

            t2 = Table(parent_data, colWidths=[100, 160, 100, 160])
            t2.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.whitesmoke),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
                ('FONTNAME', (0, 0), (-1, -1), font_name),
                ('PADDING', (0, 0), (-1, -1), 5),
            ]))
            story.append(Paragraph(fix_tr("<b>VELİ BİLGİLERİ</b>"), heading_style))
            story.append(Spacer(1, 5))
            story.append(t2)
            story.append(Spacer(1, 15))

            rules_text = """
            1. Sporcunun idmanlara düzenli katılım sağlaması ve kulüp kurallarına uyması gerekmektedir.<br/>
            2. Yukarıda belirtilen sağlık ve kronik hastalık bilgilerinin doğruluğu veli/öğrenci tarafından beyan edilmiştir.<br/>
            3. Tesis içinde kaybolan kişisel eşyalardan kulüp yönetimi sorumlu tutulamaz.<br/>
            4. Kulüp tarafından düzenlenen antrenman, etkinlik, müsabaka ve organizasyonlarda sporcunun fotoğraf, video ve ses kayıtlarının alınmasına; bu görsel ve işitsel materyallerin kulübün sosyal medya hesaplarında, web sitesinde, basılı ve dijital reklam/tanıtım mecralarında yayınlanmasına velisi/yasal vasisi olarak onay veriyorum.
            """
            story.append(Paragraph(fix_tr("<b>TAAHHÜT VE İZİN BEYANI</b>"), heading_style))
            story.append(Spacer(1, 5))
            story.append(Paragraph(fix_tr(rules_text), normal_style))
            story.append(Spacer(1, 20))

            sig_data = [
                [fix_tr("Veli / Öğrenci İmza:"), fix_tr("Kulüp / Antrenör Onay:")],
                ["\n\n_______________________", "\n\n_______________________"]
            ]
            sig_table = Table(sig_data, colWidths=[260, 260])
            sig_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, -1), font_name),
            ]))
            story.append(sig_table)

            doc.build(story)
            messagebox.showinfo("Başarılı", f"PDF Formu sorunsuz oluşturuldu:\n{file_path}")

        except Exception as e:
            messagebox.showerror("Hata", f"PDF oluşturulamadı: {str(e)}")

    def export_group_pdf(self):
        if not REPORTLAB_AVAILABLE:
            messagebox.showerror("Hata", "reportlab kütüphanesi gerekli.")
            return
        
        active_tab_idx = self.group_notebook.index(self.group_notebook.select())
        group_name = self.groups[active_tab_idx]
        tree_g, _, _ = self.group_trees[group_name]

        file_path = filedialog.asksaveasfilename(defaultextension=".pdf", initialfile=f"Brans_Listesi_{group_name}.pdf", filetypes=[("PDF Dosyası", "*.pdf")])
        if not file_path:
            return

        try:
            doc = SimpleDocTemplate(file_path, pagesize=landscape(letter), rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
            styles = getSampleStyleSheet()
            font_name = FONT_NAME

            story = [Paragraph(fix_tr(f"<b>{group_name} - Branş Öğrenci Listesi</b>"), styles['Heading1']), Spacer(1, 10)]
            
            table_data = [["ID", "Ad Soyad", "TC No", "Haftanın Günleri", "Seans / Saat", "Üyelik Süresi", "Üyelik", "İletişim 1", "Veli Ad Soyad"]]
            for item in tree_g.get_children():
                table_data.append([fix_tr(str(x)) for x in tree_g.item(item)['values']])

            t = Table(table_data, colWidths=[45, 110, 85, 100, 95, 80, 65, 95, 110])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.navy),
                ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                ('FONTNAME', (0,0), (-1,-1), font_name),
                ('FONTSIZE', (0,0), (-1,-1), 8),
                ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('PADDING', (0,0), (-1,-1), 4),
            ]))
            story.append(t)
            doc.build(story)
            messagebox.showinfo("Başarılı", f"PDF Kaydedildi:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Hata", f"PDF oluşturulamadı: {str(e)}")

    def export_schedule_pdf(self):
        if not REPORTLAB_AVAILABLE: return
        file_path = filedialog.asksaveasfilename(defaultextension=".pdf", initialfile="Haftalik_Program.pdf", filetypes=[("PDF Dosyası", "*.pdf")])
        if not file_path: return

        try:
            doc = SimpleDocTemplate(file_path, pagesize=landscape(letter), rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
            styles = getSampleStyleSheet()
            font_name = FONT_NAME

            story = [Paragraph(fix_tr("<b>Haftalık Günlük Seans Programı</b>"), styles['Heading1']), Spacer(1, 10)]
            
            table_data = [["Gün", "Seans / Saat", "Ad Soyad", "Branş", "İletişim"]]
            for day, tree in self.day_boxes.items():
                for item in tree.get_children():
                    vals = tree.item(item)['values']
                    table_data.append([fix_tr(day), fix_tr(str(vals[0])), fix_tr(str(vals[1])), fix_tr(str(vals[2])), fix_tr(str(vals[3]))])

            t = Table(table_data, colWidths=[100, 110, 150, 130, 110])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.darkblue),
                ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                ('FONTNAME', (0,0), (-1,-1), font_name),
                ('FONTSIZE', (0,0), (-1,-1), 9),
                ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('PADDING', (0,0), (-1,-1), 5),
            ]))
            story.append(t)
            doc.build(story)
            messagebox.showinfo("Başarılı", f"Haftalık Program PDF olarak kaydedildi.")
        except Exception as e:
            messagebox.showerror("Hata", f"PDF oluşturulamadı: {str(e)}")

    def export_attendance_pdf(self):
        if not REPORTLAB_AVAILABLE: return
        file_path = filedialog.asksaveasfilename(defaultextension=".pdf", initialfile="Yoklama_Raporu.pdf", filetypes=[("PDF Dosyası", "*.pdf")])
        if not file_path: return

        try:
            doc = SimpleDocTemplate(file_path, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
            styles = getSampleStyleSheet()
            font_name = FONT_NAME

            sel_date = self.entry_att_date.get().strip() or datetime.now().strftime('%d/%m/%Y')
            sel_day = self.combo_att_day.get()

            story = [Paragraph(fix_tr(f"<b>Yoklama Raporu - Tarih: {sel_date} ({sel_day})</b>"), styles['Heading1']), Spacer(1, 10)]
            
            table_data = [["ID", "Ad Soyad", "Branş", "Seans / Saat", "Yoklama Durumu"]]
            for item in self.tree_att.get_children():
                table_data.append([fix_tr(str(x)) for x in self.tree_att.item(item)['values']])

            t = Table(table_data, colWidths=[60, 150, 110, 110, 100])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.darkcyan),
                ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                ('FONTNAME', (0,0), (-1,-1), font_name),
                ('FONTSIZE', (0,0), (-1,-1), 9),
                ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('PADDING', (0,0), (-1,-1), 6),
            ]))
            story.append(t)
            doc.build(story)
            messagebox.showinfo("Başarılı", f"Yoklama PDF olarak kaydedildi.")
        except Exception as e:
            messagebox.showerror("Hata", f"PDF oluşturulamadı: {str(e)}")

    def export_payments_pdf(self):
        if not REPORTLAB_AVAILABLE or not self.is_payment_unlocked: return
        file_path = filedialog.asksaveasfilename(defaultextension=".pdf", initialfile="Ay_Ay_Odeme_Raporu.pdf", filetypes=[("PDF Dosyası", "*.pdf")])
        if not file_path: return

        try:
            doc = SimpleDocTemplate(file_path, pagesize=landscape(letter), rightMargin=20, leftMargin=20, topMargin=30, bottomMargin=30)
            styles = getSampleStyleSheet()
            font_name = FONT_NAME

            story = [Paragraph(fix_tr("<b>Ay Ay Ödeme & Aidat Takip Raporu</b>"), styles['Heading1']), Spacer(1, 10)]
            
            table_data = [["ID", "Ad Soyad", "Branş", "Ücret"] + self.months_list]
            for item in self.tree_pay.get_children():
                table_data.append([fix_tr(str(x)) for x in self.tree_pay.item(item)['values']])

            col_w = [30, 105, 85, 55] + [43] * 12
            t = Table(table_data, colWidths=col_w)
            t.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.darkred),
                ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                ('FONTNAME', (0,0), (-1,-1), font_name),
                ('FONTSIZE', (0,0), (-1,-1), 7.5),
                ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('PADDING', (0,0), (-1,-1), 4),
            ]))
            story.append(t)
            doc.build(story)
            messagebox.showinfo("Başarılı", f"Ödeme Raporu PDF olarak kaydedildi.")
        except Exception as e:
            messagebox.showerror("Hata", f"PDF oluşturulamadı: {str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = SportsClubApp(root)
    root.mainloop()
