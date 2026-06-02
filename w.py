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
    page_title="ParkFlow - Smart Parking",
    page_icon="🚗",
    layout="wide"
)

# =========================================================
# STARTUP STYLE UI
# =========================================================
st.markdown("""
<style>

/* BACKGROUND STARTUP DARK */
.main {
    background-color: #0a0f1c;
    color: white;
}

/* SIDEBAR */
section[data-testid="stSidebar"] {
    background-color: #0f172a;
}

/* TITLE */
h1, h2, h3 {
    color: #60a5fa;
    font-weight: 700;
    margin-bottom: 5px;
}

/* CARD STYLE */
.card {
    background: linear-gradient(135deg, #111827, #0b1220);
    border: 1px solid #1f2937;
    padding: 18px;
    border-radius: 16px;
    box-shadow: 0 0 15px rgba(59,130,246,0.15);
    margin-bottom: 10px;
}

/* METRICS */
.metric {
    background-color: #111827;
    padding: 15px;
    border-radius: 12px;
    border: 1px solid #1f2937;
    text-align: center;
}

/* BUTTON */
.stButton>button {
    width: 100%;
    background: linear-gradient(90deg, #3b82f6, #06b6d4);
    color: white;
    border-radius: 12px;
    padding: 10px;
    font-weight: bold;
    border: none;
}

.stButton>button:hover {
    transform: scale(1.02);
    transition: 0.2s;
}

/* INPUT */
input {
    background-color: #0f172a !important;
    color: white !important;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# DATABASE
# =========================================================
conn = sqlite3.connect("parkflow.db", check_same_thread=False)
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
    metode TEXT,
    ticket TEXT
)
""")
conn.commit()

# =========================================================
# SESSION
# =========================================================
if "login" not in st.session_state:
    st.session_state.login = False

# =========================================================
# LOGIN PAGE (STARTUP STYLE)
# =========================================================
def login():
    st.markdown("## 🚗 ParkFlow Control Panel")
    st.markdown("### Login Admin")

    col1, col2 = st.columns(2)

    with col1:
        user = st.text_input("Username")

    with col2:
        pw = st.text_input("Password", type="password")

    if st.button("LOGIN"):
        if user == "admin" and pw == "123":
            st.session_state.login = True
            st.success("Access Granted ✔")
        else:
            st.error("Invalid Credentials")

if not st.session_state.login:
    login()
    st.stop()

# =========================================================
# UTILS
# =========================================================
def ticket():
    return "PF-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=7))

def tarif(jenis, jam):
    return jam * (2000 if jenis == "Motor" else 5000)

# =========================================================
# SIDEBAR (STARTUP NAV)
# =========================================================
st.sidebar.title("🚗 ParkFlow")
menu = st.sidebar.radio("Navigation", [
    "Dashboard",
    "Entry Vehicle",
    "Exit Vehicle",
    "Active Parking",
    "History",
    "Analytics"
])

# =========================================================
# DASHBOARD
# =========================================================
if menu == "Dashboard":
    st.title("📊 Overview Dashboard")

    c.execute("SELECT COUNT(*) FROM parkir WHERE keluar IS NULL")
    active = c.fetchone()[0]

    c.execute("SELECT SUM(total) FROM parkir WHERE total IS NOT NULL")
    income = c.fetchone()[0] or 0

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
        <div class="card">
            <h3>🚗 Active</h3>
            <h2>{active}</h2>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="card">
            <h3>💰 Revenue</h3>
            <h2>Rp {income}</h2>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="card">
            <h3>🟢 System</h3>
            <h2>ONLINE</h2>
        </div>
        """, unsafe_allow_html=True)

# =========================================================
# ENTRY
# =========================================================
elif menu == "Entry Vehicle":
    st.title("🚗 Vehicle Entry")

    col1, col2 = st.columns(2)

    with col1:
        plat = st.text_input("Plate Number")

    with col2:
        jenis = st.selectbox("Vehicle Type", ["Motor", "Mobil"])

    if st.button("Generate Ticket"):
        tkt = ticket()
        now = datetime.now().isoformat()

        c.execute("""
        INSERT INTO parkir (plat, jenis, masuk, ticket)
        VALUES (?, ?, ?, ?)
        """, (plat.upper(), jenis, now, tkt))
        conn.commit()

        st.markdown(f"""
        <div class="card">
            <h3>🎫 Ticket Issued</h3>
            <p><b>{tkt}</b></p>
            <p>{plat.upper()} - {jenis}</p>
        </div>
        """, unsafe_allow_html=True)

# =========================================================
# EXIT
# =========================================================
elif menu == "Exit Vehicle":
    st.title("🚪 Vehicle Exit")

    plat = st.text_input("Plate Number")

    if st.button("Check Vehicle"):
        c.execute("SELECT * FROM parkir WHERE plat=? AND keluar IS NULL", (plat.upper(),))
        data = c.fetchone()

        if data:
            id, plat, jenis, masuk, keluar, lama, total, metode, ticket_code = data

            masuk_dt = datetime.fromisoformat(masuk)
            now = datetime.now()

            jam = max(1, int((now - masuk_dt).seconds / 3600))
            total_bayar = tarif(jenis, jam)

            metode = st.selectbox("Payment Method", ["QRIS", "Cash", "Transfer"])

            st.markdown(f"""
            <div class="card">
                <h3>Total Payment</h3>
                <h2>Rp {total_bayar}</h2>
            </div>
            """, unsafe_allow_html=True)

            if st.button("PAY & EXIT"):
                c.execute("""
                UPDATE parkir
                SET keluar=?, lama=?, total=?, metode=?
                WHERE id=?
                """, (now.isoformat(), jam, total_bayar, metode, id))
                conn.commit()

                st.success("PAYMENT SUCCESSFUL ✔ Vehicle Exit Complete")

        else:
            st.error("Vehicle Not Found")

# =========================================================
# ACTIVE
# =========================================================
elif menu == "Active Parking":
    st.title("🅿️ Active Parking")

    df = pd.read_sql("SELECT * FROM parkir WHERE keluar IS NULL", conn)
    st.dataframe(df, use_container_width=True)

# =========================================================
# HISTORY
# =========================================================
elif menu == "History":
    st.title("📜 Transaction History")

    df = pd.read_sql("SELECT * FROM parkir WHERE keluar IS NOT NULL", conn)
    st.dataframe(df, use_container_width=True)

# =========================================================
# ANALYTICS
# =========================================================
elif menu == "Analytics":
    st.title("📈 Revenue Analytics")

    df = pd.read_sql("SELECT total FROM parkir WHERE total IS NOT NULL", conn)

    if len(df) > 0:
        st.line_chart(df)
        st.bar_chart(df)
    else:
        st.info("No transactions yet")