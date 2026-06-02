import streamlit as st
import pandas as pd
from datetime import datetime
import random
import string

# =========================================================
# CONFIG
# =========================================================
st.set_page_config(page_title="Smart Parking System", page_icon="🚗", layout="wide")

# =========================================================
# SESSION INIT
# =========================================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "riwayat" not in st.session_state:
    st.session_state.riwayat = []

if "pendapatan" not in st.session_state:
    st.session_state.pendapatan = []

if "kendaraan" not in st.session_state:
    st.session_state.kendaraan = None

# =========================================================
# LINKED LIST NODE
# =========================================================
class Node:
    def __init__(self, plat, jenis):
        self.plat = plat.upper()
        self.jenis = jenis
        self.masuk = datetime.now()
        self.next = None

# =========================================================
# LINKED LIST
# =========================================================
class LinkedList:
    def __init__(self):
        self.head = None

    def add(self, plat, jenis):
        node = Node(plat, jenis)
        node.next = self.head
        self.head = node

    def find(self, plat):
        temp = self.head
        while temp:
            if temp.plat == plat.upper():
                return temp
            temp = temp.next
        return None

    def delete(self, plat):
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

    def all(self):
        data = []
        temp = self.head
        while temp:
            data.append({
                "Plat": temp.plat,
                "Jenis": temp.jenis,
                "Masuk": temp.masuk
            })
            temp = temp.next
        return data

# init list
if "ll" not in st.session_state:
    st.session_state.ll = LinkedList()

ll = st.session_state.ll

# =========================================================
# LOGIN
# =========================================================
def login():
    st.title("🔐 LOGIN ADMIN")

    user = st.text_input("Username")
    pw = st.text_input("Password", type="password")

    if st.button("Login"):
        if user == "admin" and pw == "123":
            st.session_state.logged_in = True
            st.success("Login berhasil")
        else:
            st.error("Login gagal")

if not st.session_state.logged_in:
    login()
    st.stop()

# =========================================================
# TARIF
# =========================================================
def tarif(jenis, jam):
    if jenis == "Motor":
        return jam * 2000
    return jam * 5000

# =========================================================
# TICKET
# =========================================================
def ticket():
    return "TKT-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

# =========================================================
# MENU
# =========================================================
st.sidebar.title("🚗 PARKING SYSTEM")

menu = st.sidebar.radio("Menu", [
    "Dashboard",
    "Masuk",
    "Keluar",
    "Data Aktif",
    "Cari",
    "Sorting",
    "Grafik"
])

# =========================================================
# DASHBOARD
# =========================================================
if menu == "Dashboard":
    st.title("🏢 Smart Parking System")
    st.info("Linked List + Payment + PDF + Grafik TANPA matplotlib")

# =========================================================
# MASUK
# =========================================================
elif menu == "Masuk":
    st.title("🚗 Kendaraan Masuk")

    plat = st.text_input("Plat Nomor")
    jenis = st.selectbox("Jenis", ["Motor", "Mobil"])

    if st.button("Masuk"):
        ll.add(plat, jenis)
        tkt = ticket()

        st.success("Kendaraan masuk")
        st.code(f"""
TICKET : {tkt}
PLAT   : {plat}
JENIS  : {jenis}
WAKTU  : {datetime.now()}
""")

# =========================================================
# KELUAR
# =========================================================
elif menu == "Keluar":
    st.title("🚪 Kendaraan Keluar")

    plat = st.text_input("Plat keluar")

    if st.button("Proses"):
        data = ll.find(plat)

        if data:
            keluar = datetime.now()
            lama = max(1, int((keluar - data.masuk).seconds / 3600))
            total = tarif(data.jenis, lama)

            metode = st.selectbox("Metode Bayar", ["QRIS", "Cash", "Transfer Bank"])

            st.write(f"Total bayar: Rp {total}")

            if st.button("Bayar"):
                ll.delete(plat)

                st.session_state.riwayat.append(total)
                st.session_state.pendapatan.append(total)

                st.success("Pembayaran sukses")
                st.write("Metode:", metode)

        else:
            st.error("Data tidak ditemukan")

# =========================================================
# DATA AKTIF
# =========================================================
elif menu == "Data Aktif":
    st.title("📋 Kendaraan Aktif")

    df = pd.DataFrame(ll.all())
    st.dataframe(df)

# =========================================================
# CARI
# =========================================================
elif menu == "Cari":
    st.title("🔍 Searching")

    plat = st.text_input("Cari plat")

    if st.button("Search"):
        res = ll.find(plat)

        if res:
            st.success(f"Ditemukan: {res.plat} ({res.jenis})")
        else:
            st.error("Tidak ditemukan")

# =========================================================
# SORTING
# =========================================================
elif menu == "Sorting":
    st.title("🔤 Sorting A-Z")

    data = sorted(ll.all(), key=lambda x: x["Plat"])
    st.dataframe(data)

# =========================================================
# GRAFIK (STREAMLIT BUILT-IN)
# =========================================================
elif menu == "Grafik":
    st.title("📈 Pendapatan")

    if len(st.session_state.pendapatan) > 0:
        df = pd.DataFrame(st.session_state.pendapatan, columns=["Pendapatan"])
        st.line_chart(df)
        st.bar_chart(df)
    else:
        st.info("Belum ada transaksi")