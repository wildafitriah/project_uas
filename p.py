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
    page_title="Smart Parking Ultra Pro",
    page_icon="🚗",
    layout="wide"
)

# =========================================================
# DATABASE
# =========================================================
conn = sqlite3.connect("parking_ultra.db", check_same_thread=False)
c = conn.cursor()

# USERS TABLE
c.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    password TEXT
)
""")

# PARKING TABLE
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

# default admin
c.execute("SELECT * FROM users WHERE username='admin'")
if not c.fetchone():
    c.execute("INSERT INTO users (username, password) VALUES ('admin','123')")
conn.commit()

# =========================================================
# SESSION
# =========================================================
if "login" not in st.session_state:
    st.session_state.login = False

# =========================================================
# AUTH
# =========================================================
def login_page():
    st.title("🔐 SMART PARKING LOGIN")

    col1, col2 = st.columns(2)

    with col1:
        user = st.text_input("Username")

    with col2:
        pw = st.text_input("Password", type="password")

    if st.button("LOGIN"):
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (user, pw))
        if c.fetchone():
            st.session_state.login = True
            st.success("Login sukses")
        else:
            st.error("Login gagal")

if not st.session_state.login:
    login_page()
    st.stop()

# =========================================================
# UTIL
# =========================================================
def ticket():
    return "PK-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=7))

def tarif(jenis, jam):
    return jam * (2000 if jenis == "Motor" else 5000)

# =========================================================
# SIDEBAR
# =========================================================
st.sidebar.title("🚗 ULTRA PARKING")

menu = st.sidebar.radio("Menu", [
    "Dashboard",
    "Masuk Kendaraan",
    "Keluar Kendaraan",
    "Data Aktif",
    "Riwayat",
    "Search",
    "Sorting",
    "Analytics"
])

# =========================================================
# DASHBOARD
# =========================================================
if menu == "Dashboard":
    st.title("🏢 SMART PARKING ULTRA PRO")

    c.execute("SELECT COUNT(*) FROM parkir WHERE keluar IS NULL")
    aktif = c.fetchone()[0]

    c.execute("SELECT SUM(total) FROM parkir WHERE total IS NOT NULL")
    income = c.fetchone()[0] or 0

    col1, col2, col3 = st.columns(3)

    col1.metric("🚗 Kendaraan Aktif", aktif)
    col2.metric("💰 Total Income", f"Rp {income}")
    col3.metric("🧾 System", "ONLINE")

# =========================================================
# MASUK
# =========================================================
elif menu == "Masuk Kendaraan":
    st.title("🚗 ENTRY SYSTEM")

    col1, col2 = st.columns(2)

    with col1:
        plat = st.text_input("Plat Nomor")

    with col2:
        jenis = st.selectbox("Jenis", ["Motor", "Mobil"])

    if st.button("GENERATE TICKET & MASUK"):
        tkt = ticket()
        now = datetime.now().isoformat()

        c.execute("""
        INSERT INTO parkir (plat, jenis, masuk, ticket)
        VALUES (?, ?, ?, ?)
        """, (plat.upper(), jenis, now, tkt))

        conn.commit()

        st.success("Kendaraan masuk berhasil")

        st.code(f"""
TICKET : {tkt}
PLAT   : {plat.upper()}
JENIS  : {jenis}
WAKTU  : {now}
""")

# =========================================================
# KELUAR
# =========================================================
elif menu == "Keluar Kendaraan":
    st.title("🚪 EXIT SYSTEM")

    plat = st.text_input("Plat Keluar")

    if st.button("CHECK"):
        c.execute("SELECT * FROM parkir WHERE plat=? AND keluar IS NULL", (plat.upper(),))
        data = c.fetchone()

        if data:
            id, plat, jenis, masuk, keluar, lama, total, metode, ticket_code = data

            masuk_dt = datetime.fromisoformat(masuk)
            now = datetime.now()

            jam = max(1, int((now - masuk_dt).seconds / 3600))
            total_bayar = tarif(jenis, jam)

            metode = st.selectbox("Metode Pembayaran", ["QRIS", "Cash", "Transfer Bank"])

            st.metric("TOTAL BAYAR", f"Rp {total_bayar}")

            if st.button("BAYAR & KELUAR"):
                c.execute("""
                UPDATE parkir
                SET keluar=?, lama=?, total=?, metode=?
                WHERE id=?
                """, (now.isoformat(), jam, total_bayar, metode, id))

                conn.commit()
                st.success("Transaksi selesai")

        else:
            st.error("Kendaraan tidak ditemukan")

# =========================================================
# DATA AKTIF
# =========================================================
elif menu == "Data Aktif":
    st.title("📋 ACTIVE VEHICLES")

    df = pd.read_sql("SELECT * FROM parkir WHERE keluar IS NULL", conn)
    st.dataframe(df, use_container_width=True)

# =========================================================
# RIWAYAT
# =========================================================
elif menu == "Riwayat":
    st.title("🧾 TRANSACTION HISTORY")

    df = pd.read_sql("SELECT * FROM parkir WHERE keluar IS NOT NULL", conn)
    st.dataframe(df, use_container_width=True)

# =========================================================
# SEARCH
# =========================================================
elif menu == "Search":
    st.title("🔍 SEARCH SYSTEM")

    plat = st.text_input("Cari Plat")

    if st.button("SEARCH"):
        df = pd.read_sql("SELECT * FROM parkir WHERE plat=?", conn, params=(plat.upper(),))
        st.dataframe(df)

# =========================================================
# SORTING
# =========================================================
elif menu == "Sorting":
    st.title("🔤 SORTING SYSTEM")

    df = pd.read_sql("SELECT * FROM parkir", conn)
    df = df.sort_values("plat")

    st.dataframe(df)

# =========================================================
# ANALYTICS (NO MATPLOTLIB)
# =========================================================
elif menu == "Analytics":
    st.title("📊 ANALYTICS DASHBOARD")

    df = pd.read_sql("SELECT total FROM parkir WHERE total IS NOT NULL", conn)

    if len(df) > 0:
        st.subheader("Income Trend")
        st.line_chart(df)

        st.subheader("Income Distribution")
        st.bar_chart(df)
    else:
        st.info("Belum ada data transaksi")