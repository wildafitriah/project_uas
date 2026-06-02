import streamlit as st
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import random
import string
import os

# =========================================================
# OPTIONAL IMPORT HANDLING
# =========================================================
try:
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    PDF_READY = True
except:
    PDF_READY = False

# =========================================================
# CONFIG
# =========================================================
st.set_page_config(page_title="Smart Parking System", page_icon="🚗", layout="wide")

# =========================================================
# SESSION INIT
# =========================================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "kendaraan" not in st.session_state:
    st.session_state.kendaraan = None

if "riwayat" not in st.session_state:
    st.session_state.riwayat = []

if "pendapatan" not in st.session_state:
    st.session_state.pendapatan = []

# =========================================================
# LINKED LIST NODE
# =========================================================
class Node:
    def __init__(self, plat, jenis):
        self.plat = plat.upper()
        self.jenis = jenis
        self.jam_masuk = datetime.now()
        self.next = None

# =========================================================
# LINKED LIST
# =========================================================
class LinkedList:
    def __init__(self):
        self.head = None

    def tambah(self, plat, jenis):
        node = Node(plat, jenis)
        node.next = self.head
        self.head = node
        return node

    def cari(self, plat):
        temp = self.head
        while temp:
            if temp.plat == plat.upper():
                return temp
            temp = temp.next
        return None

    def hapus(self, plat):
        temp = self.head
        prev = None
        while temp:
            if temp.plat == plat.upper():
                if prev:
                    prev.next = temp.next
                else:
                    self.head = temp.next
                return temp
            prev = temp
            temp = temp.next
        return None

    def tampil(self):
        data = []
        temp = self.head
        while temp:
            data.append({
                "Plat": temp.plat,
                "Jenis": temp.jenis,
                "Masuk": temp.jam_masuk
            })
            temp = temp.next
        return data

    def sort_asc(self):
        data = sorted(self.tampil(), key=lambda x: x["Plat"])
        return data

# =========================================================
# INIT LIST
# =========================================================
if "list" not in st.session_state:
    st.session_state.list = LinkedList()

# =========================================================
# LOGIN
# =========================================================
def login():
    st.title("🔐 LOGIN ADMIN PARKIR")

    user = st.text_input("Username")
    pw = st.text_input("Password", type="password")

    if st.button("LOGIN"):
        if user == "admin" and pw == "123":
            st.session_state.logged_in = True
            st.success("Login berhasil!")
        else:
            st.error("Login gagal!")

# =========================================================
# TARIF
# =========================================================
def hitung_tarif(jenis, jam):
    if jenis == "Motor":
        return jam * 2000
    else:
        return jam * 5000

# =========================================================
# KARcis
# =========================================================
def generate_ticket():
    return "TKT-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

# =========================================================
# PDF STRUK
# =========================================================
def buat_pdf(data):
    if not PDF_READY:
        return None

    file = f"struk_{data['plat']}.pdf"
    doc = SimpleDocTemplate(file)
    styles = getSampleStyleSheet()

    isi = []
    isi.append(Paragraph("STRUK PARKIR", styles["Title"]))
    isi.append(Spacer(1, 10))

    for k, v in data.items():
        isi.append(Paragraph(f"{k}: {v}", styles["Normal"]))

    doc.build(isi)
    return file

# =========================================================
# MAIN APP
# =========================================================
if not st.session_state.logged_in:
    login()
    st.stop()

st.sidebar.title("🚗 SMART PARKING")

menu = st.sidebar.radio("Menu", [
    "Dashboard",
    "Masuk Kendaraan",
    "Keluar Kendaraan",
    "Data Aktif",
    "Searching",
    "Sorting",
    "Grafik Pendapatan"
])

ll = st.session_state.list

# =========================================================
# DASHBOARD
# =========================================================
if menu == "Dashboard":
    st.title("🏢 Sistem Parkir Pintar")
    st.info("Linked List + Payment System + QRIS/Cash/Transfer + PDF + Grafik")

# =========================================================
# MASUK KENDARAAN
# =========================================================
elif menu == "Masuk Kendaraan":
    st.title("🚗 Kendaraan Masuk")

    plat = st.text_input("Plat Nomor")
    jenis = st.selectbox("Jenis", ["Motor", "Mobil"])

    if st.button("Masuk"):
        node = ll.tambah(plat, jenis)
        tiket = generate_ticket()

        st.success("Kendaraan masuk berhasil!")
        st.write("🎫 KARCIS PARKIR")
        st.code(f"""
        TICKET : {tiket}
        PLAT   : {node.plat}
        JENIS  : {node.jenis}
        JAM    : {node.jam_masuk}
        """)

# =========================================================
# KELUAR KENDARAAN
# =========================================================
elif menu == "Keluar Kendaraan":
    st.title("🚪 Kendaraan Keluar")

    plat = st.text_input("Plat Keluar")

    if st.button("Proses Keluar"):
        data = ll.cari(plat)

        if data:
            keluar = datetime.now()
            lama = max(1, int((keluar - data.jam_masuk).seconds / 3600))

            total = hitung_tarif(data.jenis, lama)

            st.subheader("💰 Pembayaran")
            metode = st.selectbox("Metode", ["QRIS", "Cash", "Transfer Bank"])

            st.write(f"Total: Rp {total}")

            if st.button("Bayar"):
                ll.hapus(plat)

                transaksi = {
                    "plat": plat,
                    "jenis": data.jenis,
                    "jam_masuk": data.jam_masuk,
                    "jam_keluar": keluar,
                    "lama": lama,
                    "total": total,
                    "metode": metode
                }

                st.session_state.riwayat.append(transaksi)
                st.session_state.pendapatan.append(total)

                pdf = buat_pdf(transaksi)

                st.success("Pembayaran berhasil!")

                if pdf:
                    st.write(f"📄 PDF dibuat: {pdf}")

        else:
            st.error("Kendaraan tidak ditemukan!")

# =========================================================
# DATA AKTIF
# =========================================================
elif menu == "Data Aktif":
    st.title("📋 Kendaraan Aktif")

    df = pd.DataFrame(ll.tampil())
    st.dataframe(df)

# =========================================================
# SEARCHING
# =========================================================
elif menu == "Searching":
    st.title("🔍 Cari Kendaraan")

    plat = st.text_input("Cari Plat")

    if st.button("Cari"):
        res = ll.cari(plat)
        if res:
            st.success(f"Ditemukan: {res.plat} ({res.jenis})")
        else:
            st.error("Tidak ditemukan")

# =========================================================
# SORTING
# =========================================================
elif menu == "Sorting":
    st.title("🔤 Sorting Plat A-Z")

    df = pd.DataFrame(ll.sort_asc())
    st.dataframe(df)

# =========================================================
# GRAFIK
# =========================================================
elif menu == "Grafik Pendapatan":
    st.title("📈 Pendapatan Parkir")

    if st.session_state.pendapatan:
        fig, ax = plt.subplots()
        ax.plot(st.session_state.pendapatan, marker="o")
        ax.set_title("Pendapatan per Transaksi")
        ax.set_xlabel("Transaksi")
        ax.set_ylabel("Rupiah")
        st.pyplot(fig)
    else:
        st.info("Belum ada transaksi")