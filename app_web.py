import streamlit as st
import yt_dlp
import os
from datetime import datetime, timedelta

st.set_page_config(page_title="Music Finder Pro", page_icon="🎵", layout="wide")

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 12px; height: 3.5em; background-color: #e67e22; color: white; font-weight: bold; border: none; }
    .stButton>button:hover { background-color: #d35400; border: none; }
    div[data-testid="stExpander"] { border-radius: 10px; border: 1px solid #2b2b2b; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎵 Music Finder Pro")
st.caption("Precise Time Filtering & Smart Discovery (Web Version)")

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

# --- LOGIC ---
def get_date_limit(selection):
    now = datetime.now()
    days_map = {"24 Jam Terakhir": 1, "1 Minggu Terakhir": 7, "1 Bulan Terakhir": 30, 
                "3 Bulan Terakhir": 90, "1 Tahun Terakhir": 365, "3 Tahun Terakhir": 1095}
    if selection in days_map:
        return (now - timedelta(days=days_map[selection])).strftime('%Y%m%d')
    return None

if st.button("🚀 START SCANNING"):
    if not keyword:
        st.error("Masukkan keyword terlebih dahulu!")
    else:
        date_limit = get_date_limit(time_sel)
        query = f"{keyword} {genre}" if genre != "Semua Genre" else keyword
        
        dur_map = {"5 Menit": 300, "10 Menit": 600, "20 Menit": 1200, "1 Jam": 3600}
        max_sec = dur_map.get(dur_sel, 999999)

        # Gunakan extract_flat agar cepat
        opts = {
            'extract_flat': True, 
            'quiet': True, 
            'dateafter': date_limit if date_limit else None, 
            'ignoreerrors': True,
            'no_warnings': True
        }
        
        with st.spinner("Searching YouTube..."):
            try:
                with yt_dlp.YoutubeDL(opts) as ydl:
                    results = ydl.extract_info(f"ytsearch{scan_limit}:{query}", download=False)
                    
                    found_data = []
                    if results and 'entries' in results:
                        for v in results['entries']:
                            if not v: continue
                            
                            # PROTEKSI DATA KOSONG
                            v_views = v.get('view_count') or 0
                            v_dur = v.get('duration') or 0
                            v_date = v.get('upload_date') or "00000000" # Kasih default string
                            
                            if v_views >= min_views and v_dur <= max_sec:
                                found_data.append({
                                    "Tanggal": v_date,
                                    "Views": v_views,
                                    "Judul": v.get('title') or "No Title",
                                    "Link": f"https://www.youtube.com/watch?v={v.get('id')}"
                                })

                    if found_data:
                        # SORTING SEKARANG AMAN
                        found_data.sort(key=lambda x: x['Tanggal'], reverse=True)
                        
                        st.success(f"Ditemukan {len(found_data)} video!")
                        
                        for item in found_data:
                            t = item['Tanggal']
                            fmt_date = f"{t[6:8]}-{t[4:6]}-{t[0:4]}" if len(t) == 8 else "Unknown Date"
                            
                            with st.expander(f"📅 {fmt_date} | 🔥 {item['Views']:,} views | {item['Judul']}"):
                                st.write(f"**Link Video:** {item['Link']}")
                                st.video(item['Link']) # Streamlit bisa langsung nampilin video
                    else:
                        st.warning("Tidak ada video yang cocok dengan filter atau views terlalu kecil.")
            except Exception as e:
                st.error(f"Terjadi kesalahan teknis: {str(e)}")
