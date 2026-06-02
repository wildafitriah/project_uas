import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Smart Parking Pro", page_icon="🚗", layout="wide")

# =========================================================
# 🎨 UI MODERN (BACKGROUND + DASHBOARD STYLE)
# =========================================================
st.markdown("""
<style>

.stApp {
    background: linear-gradient(135deg, #f0f9ff, #fdf2f8, #ecfeff);
}

/* SIDEBAR */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #e0f2fe, #ffffff);
}

/* TITLE */
h1, h2, h3 {
    color: #1e3a8a;
    font-weight: 800;
}

/* CARD */
.card {
    background: white;
    padding: 18px;
    border-radius: 18px;
    border: 1px solid #e5e7eb;
    box-shadow: 0 10px 25px rgba(0,0,0,0.08);
    margin-bottom: 12px;
}

/* DASHBOARD BIG CARD */
.big-card {
    background: linear-gradient(135deg, #3b82f6, #6366f1);
    color: white;
    padding: 20px;
    border-radius: 18px;
    box-shadow: 0 10px 25px rgba(0,0,0,0.2);
}

/* BUTTON */
.stButton>button {
    width: 100%;
    border-radius: 12px;
    background: linear-gradient(90deg,#3b82f6,#6366f1);
    color: white;
    font-weight: bold;
    border: none;
}

.stButton>button:hover {
    transform: scale(1.02);
    transition: 0.2s;
}

/* SUCCESS */
.success-box {
    background: #22c55e;
    color: white;
    padding: 12px;
    border-radius: 10px;
    font-weight: bold;
    text-align: center;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# LINKED LIST STRUCTURE
# =========================================================
class Node:
    def __init__(self, plat, jenis, masuk, keluar, lama, total, metode):
        self.plat = plat
        self.jenis = jenis
        self.masuk = masuk
        self.keluar = keluar
        self.lama = lama
        self.total = total
        self.metode = metode
        self.next = None

class LinkedList:
    def __init__(self):
        self.head = None

    def tambah(self, node):
        if not self.head:
            self.head = node
        else:
            cur = self.head
            while cur.next:
                cur = cur.next
            cur.next = node

    def to_list(self):
        data = []
        cur = self.head
        while cur:
            data.append({
                "Plat": cur.plat,
                "Jenis": cur.jenis,
                "Masuk": cur.masuk,
                "Keluar": cur.keluar,
                "Lama (jam)": cur.lama,
                "Total": cur.total,
                "Metode": cur.metode
            })
            cur = cur.next
        return data

# =========================================================
# SESSION STATE
# =========================================================
if "db" not in st.session_state:
    st.session_state.db = LinkedList()

if "login" not in st.session_state:
    st.session_state.login = False

# =========================================================
# LOGIN
# =========================================================
st.sidebar.title("🚗 Smart Parking")

user = st.sidebar.text_input("Username")
pw = st.sidebar.text_input("Password", type="password")

if st.sidebar.button("Login"):
    if user == "admin" and pw == "123":
        st.session_state.login = True
        st.sidebar.success("Login berhasil")
    else:
        st.sidebar.error("Login gagal")

# =========================================================
# MENU
# =========================================================
menu = st.sidebar.radio("Menu", [
    "Dashboard",
    "Entry",
    "Exit",
    "Data Parkir"
])

# =========================================================
# DASHBOARD BESAR (BIAR GA POLOS)
# =========================================================
if menu == "Dashboard":
    st.title("🚗 Smart Parking System")

    data = st.session_state.db.to_list()

    aktif = sum(1 for d in data if d["Keluar"] is None)
    income = sum(d["Total"] for d in data if d["Total"])

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
        <div class="big-card">
        🚗 Kendaraan Aktif<br><h2>{aktif}</h2>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="big-card">
        💰 Total Pendapatan<br><h2>Rp {income:,}</h2>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="big-card">
        🟢 Status Sistem<br><h2>ONLINE</h2>
        </div>
        """, unsafe_allow_html=True)

# =========================================================
# ENTRY PARKIR
# =========================================================
elif menu == "Entry":
    st.title("🚗 Kendaraan Masuk")

    plat = st.text_input("Plat Nomor")
    jenis = st.selectbox("Jenis Kendaraan", ["Motor", "Mobil"])

    if st.button("Masuk Parkir"):
        node = Node(
            plat.upper(),
            jenis,
            datetime.now().strftime("%H:%M:%S"),
            None,
            None,
            None,
            None
        )

        st.session_state.db.tambah(node)
        st.success("Kendaraan masuk berhasil 🚗")

# =========================================================
# EXIT + BAYAR
# =========================================================
elif menu == "Exit":
    st.title("🚪 Kendaraan Keluar")

    plat = st.text_input("Plat Keluar")

    if st.button("Cek Kendaraan"):
        cur = st.session_state.db.head

        found = False

        while cur:
            if cur.plat == plat.upper() and cur.keluar is None:
                found = True

                cur.keluar = datetime.now().strftime("%H:%M:%S")

                cur.lama = 1
                cur.total = 5000 if cur.jenis == "Motor" else 10000

                cur.metode = st.selectbox("Metode Bayar", ["Cash", "QRIS", "Transfer"])

                if st.button("Bayar"):
                    st.markdown("""
                    <div class="success-box">
                    🎉 PEMBAYARAN BERHASIL
                    </div>
                    """, unsafe_allow_html=True)

                break
            cur = cur.next

        if not found:
            st.error("Kendaraan tidak ditemukan")

# =========================================================
# DATA PARKIR
# =========================================================
elif menu == "Data Parkir":
    st.title("📋 Data Parkir")

    data = st.session_state.db.to_list()

    if data:
        st.dataframe(pd.DataFrame(data), use_container_width=True)
    else:
        st.warning("Belum ada data")