import streamlit as st
import yt_dlp
import os
from datetime import datetime, timedelta

st.set_page_config(page_title="Music Finder Pro - Bypass Mode", page_icon="🎵", layout="wide")

# --- UI STYLE ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 12px; height: 3.5em; background-color: #e67e22; color: white; font-weight: bold; }
    .stDownloadButton>button { background-color: #00b4d8; color: white; width: 100%; border-radius: 12px; }
    .status-box { padding: 10px; border-radius: 10px; background-color: #1e1e1e; border: 1px solid #333; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎵 Music Finder Pro (Web Version)")
st.caption("Bypass Mode Aktif: Menggunakan Cookies untuk menghindari HTTP 403 Forbidden")

# Inisialisasi Session State
if 'results' not in st.session_state:
    st.session_state.results = []

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Filter & Settings")
    keyword = st.text_input("Artis atau Judul", placeholder="Contoh: Denny Caknan")
    genre = st.selectbox("Genre", ["Semua Genre", "Pop", "Dangdut", "Koplo", "Rock", "EDM", "Remix Viral"])
    
    time_sel = st.selectbox("Rentang Waktu", [
        "24 Jam Terakhir", "1 Minggu Terakhir", "1 Bulan Terakhir", 
        "3 Bulan Terakhir", "1 Tahun Terakhir", "Semua Waktu"
    ], index=2)
    
    dur_sel = st.selectbox("Maksimal Durasi", ["5 Menit", "10 Menit", "20 Menit", "1 Jam", "Tanpa Batas"], index=1)
    min_views = st.number_input("Minimal Views", value=1000)
    scan_limit = st.slider("Batas Scan Video", 10, 100, 40)

# --- FUNGSI TANGGAL ---
def get_date_limit(selection):
    now = datetime.now()
    days_map = {"24 Jam Terakhir": 1, "1 Minggu Terakhir": 7, "1 Bulan Terakhir": 30, "3 Bulan Terakhir": 90, "1 Tahun Terakhir": 365}
    return (now - timedelta(days=days_map[selection])).strftime('%Y%m%d') if selection in days_map else None

# --- TOMBOL SCAN ---
if st.button("🚀 START SCANNING"):
    if not keyword:
        st.error("Isi keyword dulu Bang!")
    else:
        date_limit = get_date_limit(time_sel)
        query = f"{keyword} {genre}" if genre != "Semua Genre" else keyword
        dur_map = {"5 Menit": 300, "10 Menit": 600, "20 Menit": 1200, "1 Jam": 3600}
        max_sec = dur_map.get(dur_sel, 999999)

        # Path file cookies
        cookie_file = "youtube_cookies.txt"
        
        opts = {
            'extract_flat': False, # Diubah ke False agar data upload_date lebih akurat
            'quiet': True,
            'dateafter': date_limit,
            'ignoreerrors': True,
            'cookiefile': cookie_file if os.path.exists(cookie_file) else None
        }
        
        with st.spinner("Menembus blokir YouTube... Mohon tunggu..."):
            try:
                if not os.path.exists(cookie_file):
                    st.warning("⚠️ File 'youtube_cookies.txt' tidak ditemukan di GitHub. Resiko error 403 tinggi.")
                
                with yt_dlp.YoutubeDL(opts) as ydl:
                    data = ydl.extract_info(f"ytsearch{scan_limit}:{query}", download=False)
                    temp_list = []
                    if data and 'entries' in data:
                        for v in data['entries']:
                            if not v: continue
                            views = v.get('view_count') or 0
                            dur = v.get('duration') or 0
                            date = v.get('upload_date') or "00000000"
                            if views >= min_views and dur <= max_sec:
                                temp_list.append({
                                    "id": v.get('id'),
                                    "Tanggal": date,
                                    "Views": views,
                                    "Judul": v.get('title') or "No Title",
                                    "Link": f"https://www.youtube.com/watch?v={v.get('id')}"
                                })
                        temp_list.sort(key=lambda x: x['Tanggal'], reverse=True)
                        st.session_state.results = temp_list
            except Exception as e:
                st.error(f"Scan Gagal: {e}")

# --- TAMPILAN CHECKLIST ---
if st.session_state.results:
    st.subheader("✅ Hasil Temuan (Urut Terbaru)")
    
    selected_urls = []
    select_all = st.checkbox("Pilih Semua")
    
    for i, item in enumerate(st.session_state.results):
        col1, col2 = st.columns([0.1, 0.9])
        with col1:
            is_selected = st.checkbox("", value=select_all, key=f"chk_{item['id']}")
            if is_selected:
                selected_urls.append(item['Link'])
        with col2:
            t = item['Tanggal']
            fmt_date = f"{t[6:8]}-{t[4:6]}-{t[0:4]}"
            st.markdown(f"**{item['Judul']}** \n📅 {fmt_date} | 🔥 {item['Views']:,} views")

    st.divider()

    # --- PROSES DOWNLOAD ---
    if selected_urls:
        st.write(f"Terpilih: **{len(selected_urls)} lagu**")
        if st.button("📥 DOWNLOAD KE SERVER (MP3)", type="primary"):
            with st.spinner("Proses konversi sedang berjalan..."):
                save_path = "downloads"
                if not os.path.exists(save_path): os.makedirs(save_path)
                
                dl_opts = {
                    'format': 'bestaudio/best',
                    'outtmpl': f'{save_path}/%(title)s.%(ext)s',
                    'postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '192'}],
                    'cookiefile': 'youtube_cookies.txt' if os.path.exists('youtube_cookies.txt') else None,
                    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                }
                
                try:
                    with yt_dlp.YoutubeDL(dl_opts) as ydl:
                        ydl.download(selected_urls)
                    st.success(f"Berhasil! {len(selected_urls)} lagu tersimpan di folder 'downloads' server.")
                except Exception as e:
                    st.error(f"Download Gagal: {e}")
