import streamlit as st
from datetime import datetime
import pandas as pd

st.set_page_config(page_title="Ultra Parking Mall", page_icon="🏢", layout="wide")

# =====================================================
# 🎨 UI ENTERPRISE STYLE
# =====================================================
st.markdown("""
<style>

.stApp {
    background: linear-gradient(120deg, #eef2ff, #ecfeff, #fff7ed);
}

/* SIDEBAR */
section[data-testid="stSidebar"] {
    background: #ffffff;
    border-right: 1px solid #e5e7eb;
}

/* TEXT */
h1, h2, h3 {
    color: #0f172a;
    font-weight: 800;
}

/* KPI CARD */
.kpi {
    background: white;
    padding: 18px;
    border-radius: 16px;
    box-shadow: 0 10px 25px rgba(0,0,0,0.08);
    border: 1px solid #eef2f7;
    text-align: center;
}

/* CARD */
.card {
    background: white;
    padding: 16px;
    border-radius: 14px;
    border: 1px solid #eef2f7;
    box-shadow: 0 6px 18px rgba(0,0,0,0.06);
    margin-bottom: 10px;
}

/* BUTTON */
.stButton>button {
    width: 100%;
    border-radius: 10px;
    background: linear-gradient(90deg,#2563eb,#06b6d4);
    color: white;
    font-weight: 600;
    border: none;
}

.stButton>button:hover {
    transform: scale(1.02);
    transition: 0.2s;
}

/* BADGE */
.badge {
    padding: 4px 10px;
    border-radius: 999px;
    background: #dcfce7;
    color: #166534;
    font-size: 12px;
    font-weight: bold;
    display: inline-block;
}

</style>
""", unsafe_allow_html=True)

# =====================================================
# LINKED LIST
# =====================================================
class Node:
    def __init__(self, plat, jenis, masuk):
        self.plat = plat
        self.jenis = jenis
        self.masuk = masuk
        self.keluar = None
        self.total = 0
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
                "Total": cur.total
            })
            cur = cur.next
        return data

# =====================================================
# SESSION STATE
# =====================================================
if "db" not in st.session_state:
    st.session_state.db = LinkedList()

# =====================================================
# HEADER HERO
# =====================================================
st.markdown("""
<div style="
    padding:22px;
    border-radius:18px;
    background: linear-gradient(90deg,#2563eb,#06b6d4,#22c55e);
    color:white;
    font-size:18px;
    font-weight:700;
    box-shadow:0px 10px 25px rgba(0,0,0,0.15);
">
🏢 ULTRA ENTERPRISE PARKING MALL SYSTEM<br>
🚗 Smart Parking • Real-time Tracking • Linked List Engine
</div>
""", unsafe_allow_html=True)

# =====================================================
# MENU
# =====================================================
menu = st.sidebar.radio("MENU", [
    "Dashboard",
    "Masuk Parkir",
    "Keluar Parkir",
    "Data Parkir"
])

# =====================================================
# DASHBOARD
# =====================================================
if menu == "Dashboard":

    data = st.session_state.db.to_list()

    aktif = sum(1 for d in data if d["Keluar"] is None)
    total = len(data)
    income = sum(d["Total"] for d in data if d["Total"])

    st.markdown("## 📊 Enterprise Dashboard")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
        <div class="kpi">
        🚗 Active Vehicles<br>
        <h2>{aktif}</h2>
        <span class="badge">LIVE</span>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="kpi">
        📦 Total Records<br>
        <h2>{total}</h2>
        <span class="badge">TRACKED</span>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="kpi">
        💰 Revenue<br>
        <h2>Rp {income:,}</h2>
        <span class="badge">EARNED</span>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    st.markdown("## 🚗 Activity Feed")

    if data:
        for d in reversed(data[-5:]):

            status = "🟢 ACTIVE" if d["Keluar"] is None else "🔴 EXITED"

            st.markdown(f"""
            <div class="card">
            🚗 <b>{d['Plat']}</b> ({d['Jenis']})<br>
            📍 Status: {status}<br>
            💰 Total: Rp {d['Total']}
            </div>
            """, unsafe_allow_html=True)

    else:
        st.info("Belum ada data parkir")

# =====================================================
# MASUK PARKIR
# =====================================================
elif menu == "Masuk Parkir":

    st.subheader("🚗 Kendaraan Masuk")

    plat = st.text_input("Plat Nomor")
    jenis = st.selectbox("Jenis Kendaraan", ["Motor", "Mobil"])

    if st.button("Masuk"):

        node = Node(
            plat.upper(),
            jenis,
            datetime.now().strftime("%H:%M:%S")
        )

        st.session_state.db.tambah(node)

        st.success("Kendaraan masuk berhasil 🚗")

# =====================================================
# KELUAR PARKIR
# =====================================================
elif menu == "Keluar Parkir":

    st.subheader("🚪 Kendaraan Keluar")

    plat = st.text_input("Plat Nomor")

    if st.button("Hitung Biaya"):

        cur = st.session_state.db.head

        while cur:
            if cur.plat == plat.upper() and cur.keluar is None:

                keluar = datetime.now()
                masuk = datetime.strptime(cur.masuk, "%H:%M:%S")

                durasi = (keluar - masuk).seconds / 3600

                jam = max(1, int(durasi) if durasi.is_integer() else int(durasi) + 1)

                tarif = 3000 if cur.jenis == "Motor" else 5000

                total = jam * tarif

                cur.keluar = keluar.strftime("%H:%M:%S")
                cur.total = total

                st.markdown(f"""
                <div class="card">
                ⏱️ Durasi: {durasi:.2f} jam<br>
                📌 Dibulatkan: {jam} jam<br>
                💰 Total Bayar: Rp {total:,}
                </div>
                """, unsafe_allow_html=True)

                st.success("Pembayaran berhasil ✔")

                break

            cur = cur.next

# =====================================================
# DATA PARKIR
# =====================================================
elif menu == "Data Parkir":

    data = st.session_state.db.to_list()

    if data:
        st.dataframe(pd.DataFrame(data), use_container_width=True)
    else:
        st.warning("Belum ada data parkir")