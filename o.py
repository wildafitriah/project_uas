import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import random
import string
import os

# =========================================================
# CONFIG
# =========================================================
st.set_page_config(page_title="Smart Parking PRO", page_icon="🚗", layout="wide")

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
    metode TEXT
)
""")
conn.commit()

# =========================================================
# SESSION INIT
# =========================================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# =========================================================
# LOGIN
# =========================================================
def login():
    st.title("🔐 ADMIN LOGIN")

    user = st.text_input("Username")
    pw = st.text_input("Password", type="password")

    if st.button("Login"):
        if user == "admin" and pw == "123":
            st.session_state.logged_in = True
            st.success("Login sukses")
        else:
            st.error("Login gagal")

if not st.session_state.logged_in:
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
# INSERT MASUK
# =========================================================
def kendaraan_masuk(plat, jenis):
    c.execute("""
    INSERT INTO parkir (plat, jenis, masuk)
    VALUES (?, ?, ?)
    """, (plat.upper(), jenis, datetime.now().isoformat()))
    conn.commit()

# =========================================================
# PROSES KELUAR
# =========================================================
def kendaraan_keluar(plat):
    c.execute("SELECT * FROM parkir WHERE plat=? AND keluar IS NULL", (plat.upper(),))
    data = c.fetchone()

    return data

# =========================================================
# UPDATE KELUAR
# =========================================================
def update_keluar(id, keluar, lama, total, metode):
    c.execute("""
    UPDATE parkir
    SET keluar=?, lama=?, total=?, metode=?
    WHERE id=?
    """, (keluar, lama, total, metode, id))
    conn.commit()

# =========================================================
# MENU
# =========================================================
st.sidebar.title("🚗 SMART PARKING PRO")

menu = st.sidebar.radio("Menu", [
    "Dashboard",
    "Masuk Kendaraan",
    "Keluar Kendaraan",
    "Data Aktif",
    "Riwayat",
    "Search",
    "Sorting",
    "Grafik Pendapatan"
])

# =========================================================
# DASHBOARD
# =========================================================
if menu == "Dashboard":
    st.title("🏢 SMART PARKING PRO SYSTEM")
    st.success("SQLite + Linked System + Payment + Dashboard")

# =========================================================
# MASUK
# =========================================================
elif menu == "Masuk Kendaraan":
    st.title("🚗 Kendaraan Masuk")

    plat = st.text_input("Plat Nomor")
    jenis = st.selectbox("Jenis", ["Motor", "Mobil"])

    if st.button("Generate Tiket & Masuk"):
        kendaraan_masuk(plat, jenis)

        st.success("Kendaraan masuk berhasil")
        st.code(f"""
TICKET : {ticket()}
PLAT   : {plat.upper()}
JENIS  : {jenis}
WAKTU  : {datetime.now()}
""")

# =========================================================
# KELUAR
# =========================================================
elif menu == "Keluar Kendaraan":
    st.title("🚪 Kendaraan Keluar")

    plat = st.text_input("Plat Keluar")

    if st.button("Cek Kendaraan"):
        data = kendaraan_keluar(plat)

        if data:
            st.success("Data ditemukan")

            id, plat, jenis, masuk, keluar, lama, total, metode = data

            masuk_time = datetime.fromisoformat(masuk)
            now = datetime.now()

            lama_jam = max(1, int((now - masuk_time).seconds / 3600))
            total_bayar = tarif(jenis, lama_jam)

            metode_bayar = st.selectbox("Metode", ["QRIS", "Cash", "Transfer Bank"])

            st.metric("Total Bayar", f"Rp {total_bayar}")

            if st.button("Bayar & Keluar"):
                update_keluar(id, now.isoformat(), lama_jam, total_bayar, metode_bayar)
                st.success("Transaksi selesai")

        else:
            st.error("Kendaraan tidak ditemukan")

# =========================================================
# DATA AKTIF
# =========================================================
elif menu == "Data Aktif":
    st.title("📋 Kendaraan Aktif")

    df = pd.read_sql("SELECT * FROM parkir WHERE keluar IS NULL", conn)
    st.dataframe(df, use_container_width=True)

# =========================================================
# RIWAYAT
# =========================================================
elif menu == "Riwayat":
    st.title("🧾 Riwayat Parkir")

    df = pd.read_sql("SELECT * FROM parkir WHERE keluar IS NOT NULL", conn)
    st.dataframe(df, use_container_width=True)

# =========================================================
# SEARCH
# =========================================================
elif menu == "Search":
    st.title("🔍 Search Plat")

    plat = st.text_input("Masukkan Plat")

    if st.button("Cari"):
        df = pd.read_sql("SELECT * FROM parkir WHERE plat=?", conn, params=(plat.upper(),))

        if len(df) > 0:
            st.dataframe(df)
        else:
            st.error("Tidak ditemukan")

# =========================================================
# SORTING
# =========================================================
elif menu == "Sorting":
    st.title("🔤 Sorting Plat A-Z")

    df = pd.read_sql("SELECT * FROM parkir", conn)
    df = df.sort_values("plat")

    st.dataframe(df)

# =========================================================
# GRAFIK (STREAMLIT NATURAL)
# =========================================================
elif menu == "Grafik Pendapatan":
    st.title("📈 Grafik Pendapatan")

    df = pd.read_sql("SELECT total FROM parkir WHERE total IS NOT NULL", conn)

    if len(df) > 0:
        st.line_chart(df)
        st.bar_chart(df)
    else:
        st.info("Belum ada transaksi")