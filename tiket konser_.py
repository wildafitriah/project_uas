import streamlit as st
import pandas as pd

st.set_page_config(page_title="Tiket Konser Pro Max", page_icon="🎫", layout="wide")

# =========================================================
# 🎨 UI STYLE (PASTEL MODERN - NO DARK)
# =========================================================
st.markdown("""
<style>

.stApp {
    background: linear-gradient(135deg, #fdf2f8, #eff6ff, #ecfeff);
}

h1, h2, h3 {
    color: #4f46e5;
    font-weight: 800;
}

.concert-card {
    background: white;
    padding: 16px;
    border-radius: 18px;
    border: 1px solid #e5e7eb;
    box-shadow: 0 8px 25px rgba(0,0,0,0.08);
    margin-bottom: 10px;
}

.ticket {
    background: linear-gradient(135deg, #6366f1, #22c55e);
    color: white;
    padding: 18px;
    border-radius: 18px;
    font-weight: bold;
    box-shadow: 0 10px 25px rgba(0,0,0,0.2);
}

.stButton>button {
    width: 100%;
    border-radius: 12px;
    background: linear-gradient(90deg,#6366f1,#22c55e);
    color: white;
    font-weight: bold;
    padding: 10px;
    border: none;
}

.stButton>button:hover {
    transform: scale(1.03);
    transition: 0.2s;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# 🎫 LINKED LIST STRUCTURE
# =========================================================
class TicketNode:
    def __init__(self, kode, nama, konser, seat, kategori, jumlah, total, pembayaran):
        self.kode = kode
        self.nama = nama
        self.konser = konser
        self.seat = seat
        self.kategori = kategori
        self.jumlah = jumlah
        self.total = total
        self.pembayaran = pembayaran
        self.next = None


class TicketLinkedList:
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
                "Kode": cur.kode,
                "Nama": cur.nama,
                "Konser": cur.konser,
                "Seat": cur.seat,
                "Kategori": cur.kategori,
                "Jumlah": cur.jumlah,
                "Pembayaran": cur.pembayaran,
                "Total": cur.total
            })
            cur = cur.next
        return data


# =========================================================
# SESSION STATE
# =========================================================
if "db" not in st.session_state:
    st.session_state.db = TicketLinkedList()

if "seat_used" not in st.session_state:
    st.session_state.seat_used = {}

if "login" not in st.session_state:
    st.session_state.login = False


# =========================================================
# DATA KONSER
# =========================================================
konser_data = {
    "Coldplay": {"lokasi": "JIS Jakarta", "tanggal": "12 Juni 2026", "vip": 2500000, "regular": 1200000},
    "NIKI": {"lokasi": "ICE BSD", "tanggal": "20 Juli 2026", "vip": 1800000, "regular": 850000},
    "Taylor Swift": {"lokasi": "GBK", "tanggal": "10 Agustus 2026", "vip": 3500000, "regular": 2000000}
}

# =========================================================
# LOGIN ADMIN
# =========================================================
st.sidebar.title("🔐 Admin Panel")

user = st.sidebar.text_input("Username")
pw = st.sidebar.text_input("Password", type="password")

if st.sidebar.button("Login"):
    if user == "admin" and pw == "12345":
        st.session_state.login = True
        st.sidebar.success("Login sukses")
    else:
        st.sidebar.error("Salah login")

# =========================================================
# INPUT USER
# =========================================================
nama = st.sidebar.text_input("👤 Nama Pembeli")
konser = st.sidebar.selectbox("🎤 Konser", list(konser_data.keys()))

if konser not in st.session_state.seat_used:
    st.session_state.seat_used[konser] = []

semua_seat = ["A1","A2","A3","A4","A5","B1","B2","B3","B4","B5"]

seat_available = [s for s in semua_seat if s not in st.session_state.seat_used[konser]]
seat = st.sidebar.selectbox("💺 Seat", seat_available)

kategori = st.sidebar.radio("🎫 Kategori", ["VIP", "Regular"])
jumlah = st.sidebar.number_input("🔢 Jumlah", 1, 5, 1)
metode = st.sidebar.selectbox("💳 Pembayaran", ["Cash", "QRIS", "Transfer"])

harga = konser_data[konser]["vip"] if kategori == "VIP" else konser_data[konser]["regular"]
total = harga * jumlah

st.sidebar.markdown("### 🧾 Summary")
st.sidebar.write(f"Konser: {konser}")
st.sidebar.write(f"Seat: {seat}")
st.sidebar.write(f"Total: Rp {total:,}")

submit = st.sidebar.button("🛒 Checkout")


# =========================================================
# UI HEADER
# =========================================================
st.title("🎟️ Tiket Konser Pro Max")
st.caption("Sistem Pemesanan Tiket Modern dengan Linked List")

# =========================================================
# LIST KONSER
# =========================================================
st.subheader("🎤 Daftar Konser")

col1, col2, col3 = st.columns(3)

for col, (nama_konser, d) in zip([col1, col2, col3], konser_data.items()):
    with col:
        st.markdown(f"""
        <div class="concert-card">
            <h3>🎤 {nama_konser}</h3>
            <p>📍 {d['lokasi']}</p>
            <p>📅 {d['tanggal']}</p>
            <p>💎 VIP: Rp {d['vip']:,}</p>
            <p>🎟️ Regular: Rp {d['regular']:,}</p>
        </div>
        """, unsafe_allow_html=True)

# =========================================================
# CHECKOUT
# =========================================================
if submit and nama:
    kode = f"TIX-{len(st.session_state.db.to_list())+1}"

    node = TicketNode(
        kode, nama, konser, seat, kategori, jumlah, total, metode
    )

    st.session_state.db.tambah(node)
    st.session_state.seat_used[konser].append(seat)

    st.balloons()

    st.markdown(f"""
    <div class="ticket">
    🎫 TICKET SUCCESS

    Kode: {kode}
    Nama: {nama}
    Konser: {konser}
    Seat: {seat}
    Kategori: {kategori}
    Jumlah: {jumlah}
    Pembayaran: {metode}

    💰 TOTAL: Rp {total:,}

    STATUS: BERHASIL ✔
    </div>
    """, unsafe_allow_html=True)

# =========================================================
# ADMIN DASHBOARD
# =========================================================
st.divider()

if st.session_state.login:

    st.subheader("📊 Admin Dashboard")

    data = st.session_state.db.to_list()

    col1, col2 = st.columns(2)

    col1.metric("Total Tiket", len(data))

    total_income = sum([d["Total"] for d in data]) if data else 0
    col2.metric("Total Income", f"Rp {total_income:,}")

    if data:
        st.dataframe(pd.DataFrame(data), use_container_width=True)

    else:
        st.warning("Belum ada transaksi")

else:
    st.info("Login admin untuk melihat data transaksi")

# =========================================================
# FOOTER
# =========================================================
st.caption("© 2026 Tiket Konser Pro Max - Project UAS Struktur Data")