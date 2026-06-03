import streamlit as st
from datetime import datetime
import pandas as pd

# =====================================================
# CUSTOM CSS (TAMBAHKAN DI SINI)
# =====================================================
st.markdown("""
    <style>
    /* 1. Background Halaman Utama (Tema Unicorn Pastel) */
    .stApp {
        background: linear-gradient(135deg, #FFB7E8 0%, #B7E4FF 50%, #D4B7FF 100%);
        background-attachment: fixed;
    }

    /* 2. Styling Sidebar (Kotak Utama Sidebar) */
    [data-testid="stSidebar"] {
        background-color: rgba(255, 255, 255, 0.6);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 20px;
        margin: 10px;
    }

    /* 3. Membuat setiap pilihan menu memiliki kotak */
    [data-testid="stSidebar"] div[role="radiogroup"] > label {
        background-color: white;
        padding: 10px 15px;
        border-radius: 10px;
        border: 1px solid #ddd;
        margin-bottom: 5px;
        transition: all 0.3s ease;
    }

    /* Efek hover saat mouse di atas menu */
    [data-testid="stSidebar"] div[role="radiogroup"] > label:hover {
        background-color: #f0f7ff;
        border-color: #7d5fff;
    }
    
    /* Menghilangkan bullet point default bawaan streamlit jika perlu */
    [data-testid="stSidebar"] div[role="radiogroup"] {
        gap: 10px;
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
# DASHBOARD
# =====================================================

else:

    st.title("🏢 SISTEM PARKIR MALL")

    menu = st.sidebar.radio(
        "Menu",
        [
            "🏠 Dashboard",
            "🚗 Kendaraan Masuk",
            "🚘 Kendaraan Keluar",
            "📋 Daftar Parkir",
            "🔍 Cari Kendaraan",
            "🔤 Sorting Plat",
            "🧾 Riwayat Transaksi",
            "💰 Pendapatan"
        ]
        
    )
    
    st.sidebar.markdown("---")

    if st.sidebar.button("🚪 Logout"):
        st.session_state.login = False
        st.rerun()

    # =================================================
    # DASHBOARD
    # =================================================

    if menu == "🏠 Dashboard":
        total_parkir = len(st.session_state.parkir.tampilkan())

        total_transaksi = len(st.session_state.riwayat)

        st.subheader("📊 Dashboard")
        st.caption("Ringkasan data parkir saat ini")
        st.divider()
        
        col1, col2, col3 = st.columns(3)

        col1.metric("🚗 Kendaraan Parkir", total_parkir)
        col2.metric("🧾 Transaksi", total_transaksi)
        col3.metric(
            "💰 Pendapatan",
            f"Rp {st.session_state.pendapatan:,}"
        )
        
        st.info(
            f"""
            📌 Ringkasan Hari Ini
            🚗 Kendaraan aktif : {total_parkir}
            🧾 Total transaksi : {total_transaksi}
            💰 Total pendapatan : Rp {st.session_state.pendapatan:,}
            """
        )

        st.info("Selamat Datang di Dashboard Sistem Parkir Mall")
        
        data = st.session_state.parkir.tampilkan()

        motor = len([
            x for x in data
            if x["Jenis"] == "Motor"
        ])

        mobil = len([
            x for x in data
            if x["Jenis"] == "Mobil"
        ])

        st.markdown("### 📊 Statistik Kendaraan")

        col1, col2 = st.columns(2)

        col1.metric(
            "🏍️ Motor Parkir",
            motor
        )

        col2.metric(
            "🚗 Mobil Parkir",
            mobil
        )

        with st.expander("🧮 Simulasi Tarif Parkir"):

            jenis_simulasi = st.selectbox(
                "Jenis Kendaraan",
                ["Motor", "Mobil"]
            )

            jam_simulasi = st.number_input(
                "Lama Parkir (Jam)",
                min_value=1,
                value=1
            )

        if jenis_simulasi == "Motor":
            tarif_simulasi = 3000
        else:
            tarif_simulasi = 5000

        estimasi = jam_simulasi * tarif_simulasi

        st.success(
            f"Estimasi Biaya Parkir: Rp {estimasi:,}"
        )

        st.write("Rincian:")
        st.write(f"Jenis Kendaraan : {jenis_simulasi}")
        st.write(f"Lama Parkir : {jam_simulasi} Jam")
        st.write(f"Tarif per Jam : Rp {tarif_simulasi:,}")

    # =================================================
    # KENDARAAN MASUK
    # =================================================

    elif menu == "🚗 Kendaraan Masuk":

        st.subheader("🚗 Kendaraan Masuk")

        plat = st.text_input("Plat Nomor")

        jenis = st.selectbox(
            "Jenis Kendaraan",
            ["Motor", "Mobil"]
        )

        if st.button("Cetak Tiket"):

            tiket = f"TKT-{st.session_state.nomor_tiket}"

            st.session_state.nomor_tiket += 1

            waktu = datetime.now().strftime(
                "%d-%m-%Y %H:%M:%S"
            )

            node = KendaraanNode(
                tiket,
                plat,
                jenis,
                waktu
            )

            st.session_state.parkir.tambah(node)

            st.success("Kendaraan Berhasil Masuk")

            st.info(
                f"""
                🎫 Nomor Tiket : {tiket}
                🚗 Plat Nomor : {plat}
                🚘 Jenis Kendaraan : {jenis}
                🕒 Waktu Masuk : {waktu}
                """
            )

    # =================================================
    # KENDARAAN KELUAR
    # =================================================

    elif menu == "🚘 Kendaraan Keluar":

        st.subheader("🚘 Kendaraan Keluar")
        st.info("""
            📌 Tarif Parkir

            🏍️ Motor
            • 1 Jam = Rp 3.000
            • 6 Jam = Rp 18.000
            • 12 Jam = Rp 36.000

            🚗 Mobil
            • 1 Jam = Rp 5.000
            • 6 Jam = Rp 30.000
            • 12 Jam = Rp 60.000

            Biaya dihitung berdasarkan jumlah jam parkir.
        """)

        data_parkir = st.session_state.parkir.tampilkan()

        plat = None

        if len(data_parkir) > 0:

            daftar_plat = [
                item["Plat"]
                for item in data_parkir
            ]

            col1, col2 = st.columns(2)

            with col1:
                plat = st.selectbox(
                    "🚗 Pilih Plat Nomor",
                    daftar_plat
                )

            with col2:
                metode = st.selectbox(
                    "💳 Metode Pembayaran",
                [
                    "Cash",
                    "E-Wallet"
                ]
            )

        kendaraan = st.session_state.parkir.cari(plat)

        if kendaraan:

            with st.expander("🚗 Detail Kendaraan"):

                st.write("🎫 Tiket :", kendaraan.tiket)
                st.write("🚘 Jenis :", kendaraan.jenis)
                st.write("🕒 Waktu Masuk :", kendaraan.waktu_masuk)

        else:

            st.warning(
            "Tidak ada kendaraan yang sedang parkir"
        )
        if plat and st.button("Hitung Tagihan"):

            data = st.session_state.parkir.cari(plat)

            if data:

                masuk = datetime.strptime(
                    data.waktu_masuk,
                    "%d-%m-%Y %H:%M:%S"
                )

                keluar = datetime.now()

                durasi = (
                    keluar - masuk
                ).total_seconds() / 3600

                if data.jenis == "Motor":
                    tarif = 3000
                else:
                    tarif = 5000

                biaya = max(1, int(durasi)) * tarif

                st.session_state.data_keluar = {
                    "data": data,
                    "biaya": biaya,
                    "keluar": keluar.strftime("%d-%m-%Y %H:%M:%S"),
                    "metode": metode
                }

                st.success("Tagihan Berhasil Dihitung")

                st.subheader("💳 Detail Tagihan")

                col1, col2 = st.columns(2)

                with col1:
                    st.metric(
                        "⏱️ Durasi",
                        f"{durasi:.1f} Jam"
                    )

                with col2:
                    st.metric(
                        "💰 Total Bayar",
                        f"Rp {biaya:,}"
                    )

                st.write("🚗 Plat :", data.plat)
                st.write("🚘 Jenis :", data.jenis)
                st.write("💳 Metode :", metode)
                st.write("💵 Tarif per Jam :", f"Rp {tarif:,}")

            else:
                st.error("Kendaraan Tidak Ditemukan")

        if "data_keluar" in st.session_state:

            transaksi = st.session_state.data_keluar

            if transaksi["metode"] == "Cash":

                uang = st.number_input(
                    "Uang Diterima",
                    min_value=0,
                        step=1000
                )

                if st.button("Bayar Cash"):

                    if uang < transaksi["biaya"]:
                        st.error("Uang Tidak Mencukupi")

                    else:

                        kembalian = uang - transaksi["biaya"]

                        st.success("Pembayaran Berhasil")

                        st.write(
                        f"Kembalian : Rp {kembalian:,}"
                     )

                        data = transaksi["data"]

                        st.session_state.pendapatan += transaksi["biaya"]

                        st.session_state.riwayat.append({
                            "Plat": data.plat,
                            "Jenis": data.jenis,
                            "Masuk": data.waktu_masuk,
                            "Keluar": transaksi["keluar"],
                            "Metode": transaksi["metode"],
                            "Biaya": transaksi["biaya"]
                        })

                        st.session_state.parkir.hapus(
                            data.plat
                        )

                        del st.session_state.data_keluar

            else:

                if st.button("Konfirmasi Pembayaran"):

                    data = transaksi["data"]

                    st.session_state.pendapatan += transaksi["biaya"]

                    st.session_state.riwayat.append({
                        "Plat": data.plat,
                        "Jenis": data.jenis,
                        "Masuk": data.waktu_masuk,
                        "Keluar": transaksi["keluar"],
                        "Metode": transaksi["metode"],
                        "Biaya": transaksi["biaya"]
                    })

                    st.session_state.parkir.hapus(
                        data.plat
                    )

                    st.success(
                    "Pembayaran Berhasil"
                    )

                    del st.session_state.data_keluar

    # =================================================
    # DAFTAR PARKIR
    # =================================================

    elif menu == "📋 Daftar Parkir":

        st.subheader("📋 Daftar Kendaraan Parkir")

        data = st.session_state.parkir.tampilkan()

        if len(data) > 0:

            df = pd.DataFrame(data)

            st.dataframe(
                df,
                use_container_width=True
            )

            st.success(
                f"Total Kendaraan Parkir : {len(data)}"
            )

        else:
            st.warning(
                "Belum Ada Kendaraan Yang Parkir"
            )

    # =================================================
    # CARI KENDARAAN
    # =================================================

    elif menu == "🔍 Cari Kendaraan":

        st.subheader("🔍 Cari Kendaraan")

        data_parkir = st.session_state.parkir.tampilkan()

        if len(data_parkir) > 0:

            daftar_plat = [
                item["Plat"]
                for item in data_parkir
            ]

            plat_cari = st.selectbox(
                "Pilih Plat Nomor",
                daftar_plat
            )

            hasil = st.session_state.parkir.cari(
                plat_cari
            )

            if hasil:

                st.success("Kendaraan Ditemukan")

                st.info(
                    f"""
                    🎫 Tiket : {hasil.tiket}

                    🚗 Plat : {hasil.plat}

                    🚘 Jenis : {hasil.jenis}

                    🕒 Waktu Masuk : {hasil.waktu_masuk}
                    """
                )

        else:

            st.warning(
                "Belum Ada Kendaraan Yang Parkir"
            )


# =================================================
# SORTING PLAT
# =================================================

    elif menu == "🔤 Sorting Plat":

        st.subheader(
            "🔤 Sorting Plat Nomor (A-Z)"
        )

        data = st.session_state.parkir.tampilkan()

        if len(data) > 0:

            data_sort = sorted(
                data,
                key=lambda x: x["Plat"]
            )

            st.dataframe(
                pd.DataFrame(data_sort),
                use_container_width=True
            )

        else:

            st.warning(
                "Belum Ada Data Parkir"
            )

# =================================================
# RIWAYAT TRANSAKSI
# =================================================

    elif menu == "🧾 Riwayat Transaksi":

        st.subheader("🧾 Riwayat Transaksi")

        if len(st.session_state.riwayat) > 0:

            df = pd.DataFrame(
                st.session_state.riwayat
            )

            col1, col2 = st.columns(2)

            with col1:
                st.metric(
                    "🧾 Jumlah Transaksi",
                    len(df)
                )

            with col2:
                st.metric(
                    "💰 Total Pendapatan",
                    f"Rp {df['Biaya'].sum():,}"
                )

            st.dataframe(
                df,
                use_container_width=True
            )

        else:

            st.warning(
                "Belum Ada Riwayat Transaksi"
            )

# =================================================
# PENDAPATAN
# =================================================

    elif menu == "💰 Pendapatan":

        st.subheader("💰 Pendapatan Parkir")

        st.metric(
            "Total Pendapatan",
            f"Rp {st.session_state.pendapatan:,}"
        )

        if len(st.session_state.riwayat) > 0:

            df = pd.DataFrame(
                st.session_state.riwayat
            )

            st.dataframe(
                df[[
                    "Plat",
                    "Metode",
                    "Biaya"
                ]],
                use_container_width=True
            )