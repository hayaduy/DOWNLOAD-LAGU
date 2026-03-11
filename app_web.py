import streamlit as st
import yt_dlp
import os
from datetime import datetime, timedelta

st.set_page_config(page_title="Music Finder Pro", page_icon="🎵", layout="wide")

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    .main-button>button { width: 100%; border-radius: 12px; height: 3.5em; background-color: #e67e22; color: white; font-weight: bold; border: none; }
    .stDownloadButton>button { background-color: #00b4d8; color: white; width: 100%; border-radius: 12px; height: 3em; }
    div[data-testid="stExpander"] { border-radius: 10px; border: 1px solid #2b2b2b; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎵 Music Finder Pro")
st.caption("Pilih lagu secara spesifik dan download ke server/lokal")

# Session State untuk menyimpan hasil scan agar tidak hilang saat checkbox diklik
if 'results' not in st.session_state:
    st.session_state.results = []

# --- SIDEBAR SETTINGS ---
with st.sidebar:
    st.header("⚙️ Settings")
    keyword = st.text_input("Artis atau Judul Lagu", placeholder="Contoh: Denny Caknan")
    genre = st.selectbox("Genre", ["Semua Genre", "Pop", "Dangdut", "Koplo", "Rock", "EDM", "Remix Viral"])
    
    time_sel = st.selectbox("Rentang Waktu", [
        "24 Jam Terakhir", "1 Minggu Terakhir", "1 Bulan Terakhir", 
        "3 Bulan Terakhir", "1 Tahun Terakhir", "3 Tahun Terakhir", "Semua Waktu"
    ], index=2)
    
    dur_sel = st.selectbox("Maksimal Durasi", ["5 Menit", "10 Menit", "20 Menit", "1 Jam", "Tanpa Batas"], index=1)
    min_views = st.number_input("Minimal Views", value=5000)
    scan_limit = st.slider("Batas Scan Video", 10, 100, 50)

# --- LOGIC FILTER ---
def get_date_limit(selection):
    now = datetime.now()
    days_map = {"24 Jam Terakhir": 1, "1 Minggu Terakhir": 7, "1 Bulan Terakhir": 30, 
                "3 Bulan Terakhir": 90, "1 Tahun Terakhir": 365, "3 Tahun Terakhir": 1095}
    if selection in days_map:
        return (now - timedelta(days=days_map[selection])).strftime('%Y%m%d')
    return None

# --- TOMBOL SCAN ---
if st.button("🚀 START SCANNING", key="scan_btn"):
    if not keyword:
        st.error("Masukkan keyword terlebih dahulu!")
    else:
        date_limit = get_date_limit(time_sel)
        query = f"{keyword} {genre}" if genre != "Semua Genre" else keyword
        dur_map = {"5 Menit": 300, "10 Menit": 600, "20 Menit": 1200, "1 Jam": 3600}
        max_sec = dur_map.get(dur_sel, 999999)

        opts = {'extract_flat': True, 'quiet': True, 'dateafter': date_limit, 'ignoreerrors': True}
        
        with st.spinner("Mencari lagu di YouTube..."):
            try:
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
                st.error(f"Error: {e}")

# --- TAMPILAN HASIL & CHECKLIST ---
if st.session_state.results:
    st.subheader("✅ Pilih Lagu yang Ingin Didownload")
    
    selected_urls = []
    
    # Checkbox "Pilih Semua"
    select_all = st.checkbox("Pilih Semua Lagu")
    
    for i, item in enumerate(st.session_state.results):
        col1, col2 = st.columns([0.05, 0.95])
        with col1:
            # Jika "Pilih Semua" dicentang, maka semua checkbox tercentang
            is_selected = st.checkbox("", value=select_all, key=f"check_{item['id']}_{i}")
            if is_selected:
                selected_urls.append(item['Link'])
        with col2:
            t = item['Tanggal']
            fmt_date = f"{t[6:8]}-{t[4:6]}-{t[0:4]}" if len(t) == 8 else "Unknown"
            st.markdown(f"**{item['Judul']}** \n📅 {fmt_date} | 🔥 {item['Views']:,} views")

    st.divider()
    
    # --- TOMBOL DOWNLOAD UNTUK YANG DICHECKLIST ---
    if selected_urls:
        st.write(f"Total terpilih: **{len(selected_urls)} lagu**")
        if st.button("📥 PROSES DOWNLOAD (MP3)", type="primary"):
            # Note: Di Streamlit Cloud, download file besar ke client butuh proses buffering.
            # Kode ini akan mendownload ke temporary folder di server.
            with st.spinner(f"Sedang mengunduh {len(selected_urls)} lagu..."):
                try:
                    save_path = "downloads"
                    if not os.path.exists(save_path): os.makedirs(save_path)
                    
                    dl_opts = {
                        'format': 'bestaudio/best',
                        'outtmpl': f'{save_path}/%(title)s.%(ext)s',
                        'postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '192'}],
                    }
                    with yt_dlp.YoutubeDL(dl_opts) as ydl:
                        ydl.download(selected_urls)
                    
                    st.success("Berhasil didownload ke folder server! Cek folder 'downloads'.")
                    st.info("Catatan: Jika dijalankan di Streamlit Cloud, file ada di server. Untuk download ke HP/PC lokal, gunakan versi Desktop.")
                except Exception as e:
                    st.error(f"Gagal download: {e}")
    else:
        st.info("Silakan checklist lagu di atas untuk memunculkan tombol download.")
