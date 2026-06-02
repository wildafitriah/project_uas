import streamlit as st
from datetime import datetime
import pandas as pd

# =====================================================
# CONFIG
# =====================================================
st.set_page_config(page_title="Parkir Mall Pro", page_icon="🏢", layout="wide")

# =====================================================
# 🎨 UI UPGRADE (MEWAH + CERAH)
# =====================================================
st.markdown("""
<style>

/* BACKGROUND CERAH */
.stApp {
    background: linear-gradient(135deg, #e0f2fe, #fef9c3, #fce7f3);
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

/* KPI DASHBOARD */
.kpi {
    background: linear-gradient(135deg,#60a5fa,#a78bfa);
    color: white;
    padding: 18px;
    border-radius: 16px;
    text-align: center;
    box-shadow: 0 10px 25px rgba(0,0,0,0.15);
}

/* CARD */
.card {
    background: white;
    padding: 15px;
    border-radius: 16px;
    border: 1px solid #e5e7eb;
    box-shadow: 0 8px 20px rgba(0,0,0,0.08);
    margin-bottom: 10px;
}

/* BUTTON */
.stButton>button {
    width: 100%;
    border-radius: 12px;
    background: linear-gradient(90deg,#2563eb,#06b6d4);
    color: white;
    font-weight: bold;
    border: none;
}

.stButton>button:hover {
    transform: scale(1.02);
    transition: 0.2s;
}

/* SUCCESS BOX */
.success-box {
    background: #dcfce7;
    border: 1px solid #86efac;
    padding: 12px;
    border-radius: 12px;
    font-weight: bold;
    color: #166534;
}

/* TITLE BANNER */
.banner {
    padding:20px;
    border-radius:18px;
    background: linear-gradient(90deg,#2563eb,#06b6d4,#22c55e);
    color:white;
    font-size:18px;
    font-weight:700;
    box-shadow:0px 10px 25px rgba(0,0,0,0.15);
}

</style>
""", unsafe_allow_html=True)

# =====================================================
# LOGIN ADMIN
# =====================================================
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "123"

# =====================================================
# LINKED LIST NODE
# =====================================================
class KendaraanNode:
    def __init__(self, tiket, plat, jenis, waktu_masuk):
        self.tiket = tiket
        self.plat = plat
        self.jenis = jenis
        self.waktu_masuk = waktu_masuk
        self.next = None

# =====================================================
# LINKED LIST PARKIR
# =====================================================
class LinkedListParkir:
    def __init__(self):
        self.head = None

    def tambah(self, node):
        if self.head is None:
            self.head = node
            return

        current = self.head
        while current.next:
            current = current.next
        current.next = node

    def tampilkan(self):
        data = []
        current = self.head

        while current:
            data.append({
                "Tiket": current.tiket,
                "Plat": current.plat,
                "Jenis": current.jenis,
                "Waktu Masuk": current.waktu_masuk
            })
            current = current.next

        return data

    def cari(self, plat):
        current = self.head
        while current:
            if current.plat.lower() == plat.lower():
                return current
            current = current.next
        return None

    def hapus(self, plat):
        current = self.head
        prev = None

        while current:
            if current.plat.lower() == plat.lower():
                if prev:
                    prev.next = current.next
                else:
                    self.head = current.next
                return current
            prev = current
            current = current.next

        return None

# =====================================================
# SESSION STATE
# =====================================================
if "login" not in st.session_state:
    st.session_state.login = False

if "parkir" not in st.session_state:
    st.session_state.parkir = LinkedListParkir()

if "riwayat" not in st.session_state:
    st.session_state.riwayat = []

if "pendapatan" not in st.session_state:
    st.session_state.pendapatan = 0

if "nomor_tiket" not in st.session_state:
    st.session_state.nomor_tiket = 1000

# =====================================================
# LOGIN PAGE
# =====================================================
if not st.session_state.login:

    st.title("🅿️ SISTEM PARKIR MALL")
    st.subheader("Login Admin")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            st.session_state.login = True
            st.success("Login Berhasil")
            st.rerun()
        else:
            st.error("Username atau Password Salah")

# =====================================================
# DASHBOARD SYSTEM
# =====================================================
else:

    st.markdown("""
    <div class="banner">
    🏢 ULTRA PARKING MALL SYSTEM<br>
    🚗 Smart Parking • Linked List • Enterprise UI
    </div>
    """, unsafe_allow_html=True)

    menu = st.sidebar.radio(
        "MENU",
        ["Dashboard", "Kendaraan Masuk", "Kendaraan Keluar", "Daftar Parkir", "Cari Kendaraan", "Sorting Plat", "Riwayat Transaksi", "Pendapatan"]
    )

    # =================================================
    # DASHBOARD
    # =================================================
    if menu == "Dashboard":

        total_parkir = len(st.session_state.parkir.tampilkan())
        total_transaksi = len(st.session_state.riwayat)

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(f"""
            <div class="kpi">
            🚗<br><h2>{total_parkir}</h2>
            Kendaraan Parkir
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class="kpi">
            💳<br><h2>{total_transaksi}</h2>
            Transaksi
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
            <div class="kpi">
            💰<br><h2>Rp {st.session_state.pendapatan:,}</h2>
            Pendapatan
            </div>
            """, unsafe_allow_html=True)

        st.markdown("## 📊 Status Sistem")
        st.success("🟢 Sistem Parkir Aktif & Berjalan Normal")

    # =================================================
    # MASUK
    # =================================================
    elif menu == "Kendaraan Masuk":

        st.subheader("🚗 Kendaraan Masuk")

        plat = st.text_input("Plat Nomor")
        jenis = st.selectbox("Jenis Kendaraan", ["Motor", "Mobil"])

        if st.button("Cetak Tiket"):

            tiket = f"TKT-{st.session_state.nomor_tiket}"
            st.session_state.nomor_tiket += 1

            waktu = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

            node = KendaraanNode(tiket, plat, jenis, waktu)
            st.session_state.parkir.tambah(node)

            st.markdown("""
            <div class="success-box">
            ✅ Kendaraan berhasil masuk!
            </div>
            """, unsafe_allow_html=True)

            st.markdown("### 🎫 TIKET PARKIR")
            st.write(f"Nomor Tiket : {tiket}")
            st.write(f"Plat : {plat}")
            st.write(f"Jenis : {jenis}")
            st.write(f"Waktu : {waktu}")

    # =================================================
    # KELUAR
    # =================================================
    elif menu == "Kendaraan Keluar":

        st.subheader("🚘 Kendaraan Keluar")

        plat = st.text_input("Masukkan Plat")

        metode = st.selectbox("Metode Pembayaran", ["Cash", "QRIS", "Debit", "E-Wallet"])

        if st.button("Hitung Tagihan"):

            data = st.session_state.parkir.cari(plat)

            if data:

                masuk = datetime.strptime(data.waktu_masuk, "%d-%m-%Y %H:%M:%S")
                keluar = datetime.now()

                durasi = (keluar - masuk).total_seconds() / 3600
                jam = max(1, int(durasi))

                tarif = 3000 if data.jenis == "Motor" else 5000
                biaya = jam * tarif

                st.session_state.data_keluar = {
                    "data": data,
                    "biaya": biaya,
                    "keluar": keluar.strftime("%d-%m-%Y %H:%M:%S"),
                    "metode": metode
                }

                st.success("Tagihan dihitung ✔")

                st.write(f"Total: Rp {biaya:,}")

            else:
                st.error("Kendaraan tidak ditemukan")

        if "data_keluar" in st.session_state:

            trx = st.session_state.data_keluar

            if trx["metode"] == "Cash":

                uang = st.number_input("Uang", min_value=0, step=1000)

                if st.button("Bayar Cash"):

                    if uang < trx["biaya"]:
                        st.error("Uang kurang")
                    else:

                        st.markdown("""
                        <div class="success-box">
                        ✅ Pembayaran Berhasil ✔
                        </div>
                        """, unsafe_allow_html=True)

                        st.session_state.pendapatan += trx["biaya"]

                        st.session_state.riwayat.append({
                            "Plat": trx["data"].plat,
                            "Jenis": trx["data"].jenis,
                            "Biaya": trx["biaya"]
                        })

                        st.session_state.parkir.hapus(trx["data"].plat)
                        del st.session_state.data_keluar

            else:

                if st.button("Bayar"):

                    st.markdown("""
                    <div class="success-box">
                    ✅ Pembayaran Berhasil ✔
                    </div>
                    """, unsafe_allow_html=True)

                    st.session_state.pendapatan += trx["biaya"]

                    st.session_state.riwayat.append({
                        "Plat": trx["data"].plat,
                        "Jenis": trx["data"].jenis,
                        "Biaya": trx["biaya"]
                    })

                    st.session_state.parkir.hapus(trx["data"].plat)
                    del st.session_state.data_keluar

    # =================================================
    # DATA
    # =================================================
    elif menu == "Daftar Parkir":

        st.dataframe(pd.DataFrame(st.session_state.parkir.tampilkan()), use_container_width=True)

    elif menu == "Riwayat Transaksi":

        st.dataframe(pd.DataFrame(st.session_state.riwayat), use_container_width=True)

    elif menu == "Pendapatan":

        st.metric("Total Pendapatan", f"Rp {st.session_state.pendapatan:,}")