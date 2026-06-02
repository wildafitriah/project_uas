import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import random
import string

# =========================================================
# CONFIG
# =========================================================
st.set_page_config(
    page_title="Smart Parking Pro",
    page_icon="🚗",
    layout="wide"
)

# =========================================================
# UI STYLE (BIAR GA POLOS)
# =========================================================
st.markdown("""
<style>
    .main {
        background-color: #0b1220;
        color: white;
    }

    h1, h2, h3 {
        color: #38bdf8;
    }

    .card {
        background: linear-gradient(135deg, #1e293b, #0f172a);
        padding: 18px;
        border-radius: 14px;
        border: 1px solid #334155;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.4);
        margin-bottom: 10px;
    }

    .success-box {
        background-color: #16a34a;
        padding: 12px;
        border-radius: 10px;
        color: white;
        font-weight: bold;
        text-align: center;
    }

    .stButton>button {
        background: linear-gradient(90deg, #06b6d4, #3b82f6);
        color: white;
        border-radius: 10px;
        border: none;
        padding: 10px 15px;
        font-weight: bold;
    }

    .stButton>button:hover {
        transform: scale(1.03);
        transition: 0.2s;
    }
</style>
""", unsafe_allow_html=True)

# =========================================================
# DATABASE
# =========================================================
conn = sqlite3.connect("parking.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS parkir (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plat TEXT,
    jenis TEXT,
    masuk TEXT,
    keluar TEXT,
    lama INTEGER,
    total INTEGER,
    metode TEXT,
    ticket TEXT
)
""")
conn.commit()

# =========================================================
# SESSION
# =========================================================
if "login" not in st.session_state:
    st.session_state.login = False

# =========================================================
# LOGIN
# =========================================================
def login():
    st.title("🔐 LOGIN ADMIN PARKING")

    col1, col2 = st.columns(2)

    with col1:
        user = st.text_input("Username")

    with col2:
        pw = st.text_input("Password", type="password")

    if st.button("LOGIN"):
        if user == "admin" and pw == "123":
            st.session_state.login = True
            st.success("Login berhasil 🚀")
        else:
            st.error("Login gagal")

if not st.session_state.login:
    login()
    st.stop()

# =========================================================
# UTIL
# =========================================================
def ticket():
    return "TKT-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

def tarif(jenis, jam):
    return jam * (2000 if jenis == "Motor" else 5000)

# =========================================================
# MENU
# =========================================================
st.sidebar.title("🚗 PARKING MENU")

menu = st.sidebar.radio("", [
    "Dashboard",
    "Masuk Kendaraan",
    "Keluar Kendaraan",
    "Data Aktif",
    "Riwayat",
    "Analytics"
])

# =========================================================
# DASHBOARD
# =========================================================
if menu == "Dashboard":
    st.title("🚗 SMART PARKING SYSTEM")

    c.execute("SELECT COUNT(*) FROM parkir WHERE keluar IS NULL")
    aktif = c.fetchone()[0]

    c.execute("SELECT SUM(total) FROM parkir WHERE total IS NOT NULL")
    income = c.fetchone()[0] or 0

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f'<div class="card"><h3>🚗 Aktif</h3><h2>{aktif}</h2></div>', unsafe_allow_html=True)

    with col2:
        st.markdown(f'<div class="card"><h3>💰 Income</h3><h2>Rp {income}</h2></div>', unsafe_allow_html=True)

    with col3:
        st.markdown('<div class="card"><h3>🟢 Status</h3><h2>ONLINE</h2></div>', unsafe_allow_html=True)

# =========================================================
# MASUK
# =========================================================
elif menu == "Masuk Kendaraan":
    st.title("🚗 ENTRY SYSTEM")

    col1, col2 = st.columns(2)

    with col1:
        plat = st.text_input("🚘 Plat Nomor")

    with col2:
        jenis = st.selectbox("🚦 Jenis", ["Motor", "Mobil"])

    if st.button("🎫 MASUK & GENERATE TICKET"):
        tkt = ticket()
        now = datetime.now().isoformat()

        c.execute("""
        INSERT INTO parkir (plat, jenis, masuk, ticket)
        VALUES (?, ?, ?, ?)
        """, (plat.upper(), jenis, now, tkt))
        conn.commit()

        st.markdown(f"""
        <div class="card">
            <h3>🎫 TICKET PARKIR</h3>
            <p><b>{tkt}</b></p>
            <p>Plat: {plat.upper()}</p>
            <p>Jenis: {jenis}</p>
        </div>
        """, unsafe_allow_html=True)

# =========================================================
# KELUAR
# =========================================================
elif menu == "Keluar Kendaraan":
    st.title("🚪 EXIT SYSTEM")

    plat = st.text_input("Plat Keluar")

    if st.button("CHECK KENDARAAN"):
        c.execute("SELECT * FROM parkir WHERE plat=? AND keluar IS NULL", (plat.upper(),))
        data = c.fetchone()

        if data:
            id, plat, jenis, masuk, keluar, lama, total, metode, ticket_code = data

            masuk_dt = datetime.fromisoformat(masuk)
            now = datetime.now()

            jam = max(1, int((now - masuk_dt).seconds / 3600))
            total_bayar = tarif(jenis, jam)

            metode = st.selectbox("Metode Pembayaran", ["QRIS", "Cash", "Transfer Bank"])

            st.markdown(f'<div class="card"><h3>Total: Rp {total_bayar}</h3></div>', unsafe_allow_html=True)

            if st.button("💳 BAYAR"):
                c.execute("""
                UPDATE parkir
                SET keluar=?, lama=?, total=?, metode=?
                WHERE id=?
                """, (now.isoformat(), jam, total_bayar, metode, id))
                conn.commit()

                st.markdown("""
                <div class="success-box">
                    🎉 PEMBAYARAN BERHASIL!
                </div>
                """, unsafe_allow_html=True)

        else:
            st.error("Kendaraan tidak ditemukan")

# =========================================================
# DATA AKTIF
# =========================================================
elif menu == "Data Aktif":
    st.title("📋 DATA AKTIF")

    df = pd.read_sql("SELECT * FROM parkir WHERE keluar IS NULL", conn)
    st.dataframe(df, use_container_width=True)

# =========================================================
# RIWAYAT
# =========================================================
elif menu == "Riwayat":
    st.title("🧾 RIWAYAT")

    df = pd.read_sql("SELECT * FROM parkir WHERE keluar IS NOT NULL", conn)
    st.dataframe(df, use_container_width=True)

# =========================================================
# ANALYTICS
# =========================================================
elif menu == "Analytics":
    st.title("📊 ANALYTICS")

    df = pd.read_sql("SELECT total FROM parkir WHERE total IS NOT NULL", conn)

    if len(df) > 0:
        st.line_chart(df)
        st.bar_chart(df)
    else:
        st.info("Belum ada transaksi")