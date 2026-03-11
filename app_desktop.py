import customtkinter as ctk
import yt_dlp
import os
import threading
from datetime import datetime, timedelta
from tkinter import messagebox, filedialog

# Konfigurasi Tema Global
ctk.set_appearance_mode("dark")

class MusicDownloaderApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Music Finder Pro - Precise Time v27")
        self.geometry("800x1000")
        self.configure(fg_color="#121212") 
        self.urls_found = [] 

        # --- HEADER ---
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(pady=(30, 15))
        
        self.label_title = ctk.CTkLabel(self.header_frame, text="MUSIC FINDER PRO", 
                                       font=ctk.CTkFont(size=32, weight="bold", family="Inter"))
        self.label_title.pack()
        self.label_subtitle = ctk.CTkLabel(self.header_frame, text="Precise Time Filtering & Smart Discovery", 
                                          font=ctk.CTkFont(size=13), text_color="#777777")
        self.label_subtitle.pack()

        # --- MAIN CONTAINER ---
        self.main_container = ctk.CTkFrame(self, fg_color="#1e1e1e", corner_radius=20, border_width=1, border_color="#2b2b2b")
        self.main_container.pack(pady=10, padx=30, fill="both", expand=True)

        # 1. INPUT SECTION
        self.input_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.input_frame.pack(pady=20, padx=30, fill="x")

        self.entry_keyword = ctk.CTkEntry(self.input_frame, placeholder_text="Ketik Artis atau Judul Lagu...", 
                                        height=50, corner_radius=12, fg_color="#262626", border_color="#333333")
        self.entry_keyword.pack(fill="x", pady=(0, 15))

        # 2. SELECTORS GRID
        self.grid_frame = ctk.CTkFrame(self.input_frame, fg_color="transparent")
        self.grid_frame.pack(fill="x")
        self.grid_frame.grid_columnconfigure((0, 1), weight=1)

        # Baris 1: Genre & Batas Waktu (DIPERLENGKAP)
        self.genre_filter = self.create_styled_menu(self.grid_frame, "Pilih Genre", [
            "Semua Genre", "Pop", "Dangdut", "Koplo", "Rock", "R&B", "EDM", "Lofi", "Remix Viral"
        ], 0, 0)
        
        self.time_filter = self.create_styled_menu(self.grid_frame, "Rentang Waktu Upload", [
            "24 Jam Terakhir", "1 Minggu Terakhir", "1 Bulan Terakhir", 
            "3 Bulan Terakhir", "1 Tahun Terakhir", "3 Tahun Terakhir", "Semua Waktu"
        ], 0, 1)
        self.time_filter.set("1 Bulan Terakhir")

        # Baris 2: Duration & Batas Scan
        self.duration_filter = self.create_styled_menu(self.grid_frame, "Maksimal Durasi", [
            "5 Menit", "10 Menit", "20 Menit", "1 Jam", "Tanpa Batas"
        ], 1, 0)

        self.entry_count = ctk.CTkEntry(self.grid_frame, placeholder_text="Batas Scan", height=40, corner_radius=10)
        self.entry_count.insert(0, "50")
        self.entry_count.grid(row=1, column=1, padx=5, pady=10, sticky="ew")

        # Baris 3: Views
        self.entry_views = ctk.CTkEntry(self.grid_frame, placeholder_text="Min. Views (Misal: 10000)", height=40, corner_radius=10)
        self.entry_views.insert(0, "10000")
        self.entry_views.grid(row=2, column=0, columnspan=2, padx=5, pady=10, sticky="ew")

        # 3. PATH SECTION
        self.path_frame = ctk.CTkFrame(self.input_frame, fg_color="#262626", corner_radius=10, height=45)
        self.path_frame.pack(fill="x", pady=15)
        
        self.entry_path = ctk.CTkEntry(self.path_frame, fg_color="transparent", border_width=0, width=500)
        self.entry_path.insert(0, os.path.join(os.path.expanduser("~"), "Downloads"))
        self.entry_path.pack(side="left", padx=15, pady=10)
        
        self.btn_browse = ctk.CTkButton(self.path_frame, text="BROWSE", width=90, height=30, corner_radius=8,
                                       fg_color="#333333", hover_color="#444444", command=self.browse_folder)
        self.btn_browse.pack(side="right", padx=10)

        # --- LOG & PROGRESS ---
        self.text_log = ctk.CTkTextbox(self.main_container, fg_color="#121212", corner_radius=15, 
                                      font=("Consolas", 11), border_width=1, border_color="#2b2b2b")
        self.text_log.pack(pady=10, padx=30, fill="both", expand=True)

        self.progressbar = ctk.CTkProgressBar(self.main_container, height=6, progress_color="#ff8c00", fg_color="#2b2b2b")
        self.progressbar.set(0)
        self.progressbar.pack(fill="x", padx=30, pady=(10, 25))

        # --- ACTION BUTTONS ---
        # Tombol Scan: ORANYE
        self.btn_check = ctk.CTkButton(self, text="START SCANNING", font=ctk.CTkFont(weight="bold", size=14), 
                                       height=55, corner_radius=12, 
                                       fg_color="#e67e22", hover_color="#d35400", 
                                       text_color="white", command=lambda: self.start_thread("scan"))
        self.btn_check.pack(pady=(10, 5), padx=30, fill="x")

        # Tombol Download: CERAH (Cyan-Blue)
        self.btn_download = ctk.CTkButton(self, text="DOWNLOAD SELECTED MP3", font=ctk.CTkFont(weight="bold", size=14), 
                                         height=55, corner_radius=12, 
                                         fg_color="#00b4d8", hover_color="#0077b6", 
                                         text_color="white", state="disabled", command=lambda: self.start_thread("download"))
        self.btn_download.pack(pady=(5, 30), padx=30, fill="x")

    def create_styled_menu(self, parent, label, values, row, col):
        menu = ctk.CTkOptionMenu(parent, values=values, height=40, corner_radius=10, 
                                 fg_color="#262626", button_color="#333333", button_hover_color="#444444")
        menu.grid(row=row, column=col, padx=5, pady=10, sticky="ew")
        menu.set(values[0])
        return menu

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.entry_path.delete(0, "end")
            self.entry_path.insert(0, folder)

    def log(self, message):
        self.text_log.insert("end", f" • {message}\n")
        self.text_log.see("end")

    def get_date_limit(self):
        """Menghitung mundur tanggal berdasarkan pilihan user"""
        selection = self.time_filter.get()
        now = datetime.now()
        
        if selection == "24 Jam Terakhir":
            d = now - timedelta(days=1)
        elif selection == "1 Minggu Terakhir":
            d = now - timedelta(weeks=1)
        elif selection == "1 Bulan Terakhir":
            d = now - timedelta(days=30)
        elif selection == "3 Bulan Terakhir":
            d = now - timedelta(days=90)
        elif selection == "1 Tahun Terakhir":
            d = now - timedelta(days=365)
        elif selection == "3 Tahun Terakhir":
            d = now - timedelta(days=1095)
        else: # Semua Waktu
            return None
            
        return d.strftime('%Y%m%d') # Format YYYYMMDD untuk yt-dlp

    def start_thread(self, mode):
        threading.Thread(target=self.proses_utama, args=(mode,), daemon=True).start()

    def proses_utama(self, mode):
        kw = self.entry_keyword.get()
        genre = self.genre_filter.get()
        dur_sel = self.duration_filter.get()
        
        # Ambil batas tanggal kalkulasi terbaru
        date_limit = self.get_date_limit()
        
        # Map durasi
        dur_map = {"5 Menit": 300, "10 Menit": 600, "20 Menit": 1200, "1 Jam": 3600}
        max_sec = dur_map.get(dur_sel, 999999)

        if mode == "scan":
            if not kw: messagebox.showwarning("Peringatan", "Isi keyword dulu!"); return
            
            self.urls_found = []
            temp_list = []
            self.text_log.delete("0.0", "end")
            self.progressbar.start()

            scan_count = self.entry_count.get() or "50"
            query = f"{kw} {genre}" if genre != "Semua Genre" else kw
            
            # Parameter dateafter akan memfilter video yang diupload SETELAH tanggal limit
            opts = {
                'extract_flat': True, 
                'quiet': True, 
                'dateafter': date_limit if date_limit else None,
                'ignoreerrors': True
            }
            
            try:
                with yt_dlp.YoutubeDL(opts) as ydl:
                    self.log(f"Mencari sejak: {self.time_filter.get()}")
                    self.log(f"Query: {query}...")
                    
                    results = ydl.extract_info(f"ytsearch{scan_count}:{query}", download=False)
                    
                    if 'entries' in results:
                        for v in results['entries']:
                            if not v: continue
                            views = v.get('view_count', 0) or 0
                            dur = v.get('duration', 0) or 0
                            u_date = v.get('upload_date', '00000000')
                            
                            # Filter View & Durasi
                            if views >= int(self.entry_views.get() or 0) and dur <= max_sec:
                                temp_list.append({
                                    'date': u_date,
                                    'title': v.get('title', 'Unknown'),
                                    'url': f"https://www.youtube.com/watch?v={v.get('id')}",
                                    'views': views
                                })
                
                # Urutkan berdasarkan tanggal terbaru
                temp_list.sort(key=lambda x: x['date'], reverse=True)
                
                for item in temp_list:
                    d = item['date']
                    self.log(f"[{d[6:8]}-{d[4:6]}-{d[0:4]}] {item['title'][:55]} ({item['views']:,} views)")
                    self.urls_found.append(item['url'])
                
                self.log(f"\nSelesai! Ditemukan {len(self.urls_found)} video sesuai filter.")
                if self.urls_found: self.btn_download.configure(state="normal")
            except Exception as e:
                self.log(f"Error: {e}")
            
            self.progressbar.stop()
            self.progressbar.set(1)

        elif mode == "download":
            self.btn_download.configure(state="disabled")
            dl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': f'{self.entry_path.get()}/%(title)s.%(ext)s',
                'postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '192'}],
            }
            try:
                with yt_dlp.YoutubeDL(dl_opts) as ydl:
                    ydl.download(self.urls_found)
                messagebox.showinfo("Success", "Semua lagu berhasil didownload!")
            except Exception as e:
                self.log(f"Download Error: {e}")
            self.btn_download.configure(state="normal")

if __name__ == "__main__":
    app = MusicDownloaderApp()
    app.mainloop()
