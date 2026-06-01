import streamlit as st
import pandas as pd

st.set_page_config(page_title="Tiket Konser", page_icon="🎫", layout="wide")

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

    def tambah_tiket(self, kode, nama, konser, seat, kategori, jumlah, total, pembayaran):
        node = TicketNode(kode, nama, konser, seat, kategori, jumlah, total, pembayaran)
        if not self.head:
            self.head = node
        else:
            cur = self.head
            while cur.next:
                cur = cur.next
            cur.next = node

    def tampilkan_data(self):
        data = []
        cur = self.head
        while cur:
            data.append({
                "Kode Tiket": cur.kode,
                "Nama": cur.nama,
                "Konser": cur.konser,
                "Seat": cur.seat,
                "Kategori": cur.kategori,
                "Jumlah Tiket": cur.jumlah,
                "Pembayaran": cur.pembayaran,
                "Total Bayar": f"Rp {cur.total:,}"
            })
            cur = cur.next
        return data

    def update_tiket(self, kode, nama, seat, kategori, jumlah, total, pembayaran):
        cur = self.head
        while cur:
            if cur.kode == kode:
                cur.nama = nama
                cur.seat = seat
                cur.kategori = kategori
                cur.jumlah = jumlah
                cur.total = total
                cur.pembayaran = pembayaran
                return True
            cur = cur.next
        return False

    def hapus_tiket(self, kode):
        if not self.head:
            return False

        if self.head.kode == kode:
            self.head = self.head.next
            return True

        prev = self.head
        cur = self.head.next

        while cur:
            if cur.kode == kode:
                prev.next = cur.next
                return True
            prev = cur
            cur = cur.next
        return False

if "tickets" not in st.session_state:
    st.session_state.tickets = TicketLinkedList()

if "seat_terpakai" not in st.session_state:
    st.session_state.seat_terpakai = {}

if "admin_login" not in st.session_state:
    st.session_state.admin_login = False

konser_data = {
    "Coldplay World Tour": {
        "lokasi": "Jakarta International Stadium",
        "tanggal": "12 Juni 2026",
        "vip": 2500000,
        "regular": 1200000
    },
    "NIKI Live Concert": {
        "lokasi": "ICE BSD",
        "tanggal": "20 Juli 2026",
        "vip": 1800000,
        "regular": 850000
    },
    "Taylor Swift Eras Tour": {
        "lokasi": "Gelora Bung Karno",
        "tanggal": "10 Agustus 2026",
        "vip": 3500000,
        "regular": 2000000
    }
}

st.title("🎫 Aplikasi Pemesanan Tiket Konser")
st.write("Project Struktur Data Menggunakan Linked List dan Streamlit")

st.sidebar.header("📝 Form Pemesanan")
st.sidebar.divider()

st.sidebar.subheader("🔑 Login Admin")

username = st.sidebar.text_input(
    "Username Admin"
)

password = st.sidebar.text_input(
    "Password Admin",
    type="password"
)

if st.sidebar.button("Login Admin"):

    if username == "admin" and password == "12345":

        st.session_state.admin_login = True

        st.sidebar.success(
            "Login Berhasil"
        )

    else:

        st.sidebar.error(
            "Username atau Password Salah"
        )

if st.session_state.admin_login:

    st.sidebar.success(
        "✅ Status : Admin Aktif"
    )

    if st.sidebar.button("🚪 Logout"):

        st.session_state.admin_login = False

        st.rerun()

nama = st.sidebar.text_input("👤 Nama Pembeli")
konser = st.sidebar.selectbox("🎵 Pilih Konser", list(konser_data.keys()))

semua_kursi = ["A1","A2","A3","A4","A5","B1","B2","B3","B4","B5","C1","C2","C3","C4","C5"]

if konser not in st.session_state.seat_terpakai:
    st.session_state.seat_terpakai[konser] = []

kursi_tersedia = [k for k in semua_kursi if k not in st.session_state.seat_terpakai[konser]]
seat = st.sidebar.selectbox("💺 Pilih Kursi", kursi_tersedia)

kategori = st.sidebar.radio("🎫 Kategori Tiket", ["VIP", "Regular"])
jumlah = st.sidebar.number_input("🔢 Jumlah Tiket", min_value=1, max_value=5, value=1)
metode_bayar = st.sidebar.selectbox("💳 Metode Pembayaran",["Cash", "QRIS", "Transfer Bank"])

if kategori == "VIP":
    harga_preview = konser_data[konser]["vip"]
else:
    harga_preview = konser_data[konser]["regular"]

st.sidebar.divider()
st.sidebar.subheader("🧾 Ringkasan Checkout")
st.sidebar.write(f"🎵 Konser : {konser}")
st.sidebar.write(f"💺 Kursi : {seat}")
st.sidebar.write(f"🎫 Kategori : {kategori}")
st.sidebar.write(f"🔢 Jumlah : {jumlah}")
st.sidebar.write(f"💳 Pembayaran : {metode_bayar}")
st.sidebar.write(f"💰 Total : Rp {harga_preview * jumlah:,}")
submit = st.sidebar.button("🛒 Checkout")

st.header("🎤 Daftar Konser")

konser_list = list(konser_data.items())
col1, col2, col3 = st.columns(3)

for col, item in zip([col1, col2, col3], konser_list):
    with col:
        nama_konser, detail = item
        st.subheader(nama_konser)
        st.write(f"📍 {detail['lokasi']}")
        st.write(f"📅 {detail['tanggal']}")
        st.write(f"💎 VIP : Rp {detail['vip']:,}")
        st.write(f"🎟️ Regular : Rp {detail['regular']:,}")
        st.success("Tiket Tersedia")

if submit and nama:
    harga = konser_data[konser]["vip"] if kategori == "VIP" else konser_data[konser]["regular"]
    total = harga * jumlah
    kode = f"TRX-{len(st.session_state.tickets.tampilkan_data())+1}"

    st.session_state.tickets.tambah_tiket(
        kode, nama, konser, seat, kategori, jumlah, total, metode_bayar
    )

    st.session_state.seat_terpakai[konser].append(seat)

    st.success("✅ Tiket berhasil dipesan!")
    st.subheader("🎫 E-Ticket")
    st.info(f"""Kode Tiket : {kode}

Nama : {nama}
Konser : {konser}
Seat : {seat}
Kategori : {kategori}
Jumlah : {jumlah}
Pembayaran : {metode_bayar}
Total Bayar : Rp {total:,}
Status : Berhasil""")

st.divider()

if st.session_state.admin_login:

    st.header("📊 Data Pemesanan Tiket")

    data = st.session_state.tickets.tampilkan_data()

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Total Transaksi",
            len(data)
        )

    with col2:
        total_pendapatan = 0

        cur = st.session_state.tickets.head

        while cur:
            total_pendapatan += cur.total
            cur = cur.next

        st.metric(
            "Total Pendapatan",
            f"Rp {total_pendapatan:,}"
        )

    if data:

        st.dataframe(
            pd.DataFrame(data),
            use_container_width=True
        )

        st.subheader("✏️ Update Pesanan")

        kode_update = st.selectbox(
            "Pilih Kode Tiket",
            [row["Kode Tiket"] for row in data]
        )

        nama_baru = st.text_input("Nama Baru")

        seat_baru = st.selectbox(
            "Seat Baru",
            semua_kursi,
            key="seat_update"
        )

        kategori_baru = st.radio(
            "Kategori Baru",
            ["VIP", "Regular"],
            key="kat_update"
        )

        pembayaran_baru = st.selectbox(
            "Metode Pembayaran Baru",
            ["Cash", "QRIS", "Transfer Bank"],
            key="bayar_update"
        )

        jumlah_baru = st.number_input(
            "Jumlah Baru",
            min_value=1,
            value=1
        )

        if st.button("Update Pesanan"):

            harga = (
                konser_data[konser]["vip"]
                if kategori_baru == "VIP"
                else konser_data[konser]["regular"]
            )

            total_baru = harga * jumlah_baru

            if st.session_state.tickets.update_tiket(
                kode_update,
                nama_baru,
                seat_baru,
                kategori_baru,
                jumlah_baru,
                total_baru,
                pembayaran_baru
            ):
                st.success("Pesanan berhasil diupdate")

        st.subheader("🗑️ Hapus Pesanan")

        kode_hapus = st.selectbox(
            "Pilih Kode Yang Akan Dihapus",
            [row["Kode Tiket"] for row in data],
            key="hapus"
        )

        if st.button("Hapus Pesanan"):

            if st.session_state.tickets.hapus_tiket(
                kode_hapus
            ):
                st.success(
                    "Pesanan berhasil dihapus"
                )
                st.rerun()

    else:

        st.warning(
            "Belum ada data pemesanan"
        )

else:

    st.info(
        "🔒 Data pemesanan hanya dapat dilihat Admin"
    )

st.caption("© 2026 | Project UAS Struktur Data - Tiket Konser")
