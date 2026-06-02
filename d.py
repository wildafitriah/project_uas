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
    page_title="ParkFlow OS",
    page_icon="🚗",
    layout="wide"
)

# =========================================================
# FINAL BOSS UI STYLE (STARTUP SaaS)
# =========================================================
st.markdown("""
<style>

/* GLOBAL BACKGROUND */
body {
    background: #f4f7ff;
}

/* HEADER */
h1, h2, h3 {
    font-family: sans-serif;
    color: #1e3a8a;
    margin-bottom: 5px;
}

/* TOP DASH CARDS */
.big-card {
    background: white;
    border-radius: 18px;
    padding: 18px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.08);
    border: 1px solid #eef2ff;
}

/* METRIC CARD */
.metric {
    background: linear-gradient(135deg, #3b82f6, #6366f1);
    color: white;
    padding: 18px;
    border-radius: 16px;
    text-align: center;
    box-shadow: 0 10px 20px rgba(59,130,246,0.25);
}

/* SUCCESS ALERT */
.success {
    background: #22c55e;
    color: white;
    padding: 12px;
    border-radius: 10px;
    font-weight: bold;
    text-align: center;
}

/* BUTTON */
.stButton>button {
    width: 100%;
    border-radius: 12px;
    background: linear-gradient(90deg,#2563eb,#4f46e5);
    color: white;
    font-weight: bold;
    padding: 10px;
    border: none;
}

.stButton>button:hover {
    transform: scale(1.02);
    transition: 0.2s;
}

/* SIDEBAR */
section[data-testid="stSidebar"] {
    background: white;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# DATABASE
# =========================================================
conn = sqlite3.connect("parkflow_finalboss.db", check_same_thread=False)
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
# LOGIN (APP STYLE)
# =========================================================
def login():
    st.title("🚗 ParkFlow OS")
    st.caption("Smart Parking Management System")

    col1, col2 = st.columns(2)

    with col1:
        user = st.text_input("Username")

    with col2:
        pw = st.text_input("Password", type="password")

    if st.button("Login to Dashboard"):
        if user == "admin" and pw == "123":
            st.session_state.login = True
            st.success("Access Granted ✔ Welcome Admin")
        else:
            st.error("Invalid Login")

if not st.session_state.login:
    login()
    st.stop()

# =========================================================
# UTIL
# =========================================================
def ticket():
    return "PF-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=7))

def tarif(jenis, jam):
    return jam * (2000 if jenis == "Motor" else 5000)

# =========================================================
# SIDEBAR NAV
# =========================================================
st.sidebar.title("🚗 ParkFlow OS")
menu = st.sidebar.radio("Navigation", [
    "Dashboard",
    "Entry Vehicle",
    "Exit Vehicle",
    "Active Parking",
    "History",
    "Analytics"
])

# =========================================================
# DASHBOARD (FINAL BOSS STYLE)
# =========================================================
if menu == "Dashboard":
    st.title("📊 Control Dashboard")

    c.execute("SELECT COUNT(*) FROM parkir WHERE keluar IS NULL")
    active = c.fetchone()[0]

    c.execute("SELECT SUM(total) FROM parkir WHERE total IS NOT NULL")
    income = c.fetchone()[0] or 0

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
        <div class="metric">
            <h3>🚗 Active Cars</h3>
            <h2>{active}</h2>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric">
            <h3>💰 Revenue</h3>
            <h2>Rp {income}</h2>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="metric">
            <h3>🟢 Status</h3>
            <h2>ONLINE</h2>
        </div>
        """, unsafe_allow_html=True)

# =========================================================
# ENTRY VEHICLE
# =========================================================
elif menu == "Entry Vehicle":
    st.title("🚗 Vehicle Entry System")

    col1, col2 = st.columns(2)

    with col1:
        plat = st.text_input("Plate Number")

    with col2:
        jenis = st.selectbox("Vehicle Type", ["Motor", "Mobil"])

    if st.button("Generate Ticket & Entry"):
        tkt = ticket()
        now = datetime.now().isoformat()

        c.execute("""
        INSERT INTO parkir (plat, jenis, masuk, ticket)
        VALUES (?, ?, ?, ?)
        """, (plat.upper(), jenis, now, tkt))
        conn.commit()

        st.markdown(f"""
        <div class="big-card">
            <h3>🎫 ENTRY SUCCESS</h3>
            <p><b>Ticket:</b> {tkt}</p>
            <p><b>Plate:</b> {plat.upper()}</p>
            <p><b>Type:</b> {jenis}</p>
        </div>
        """, unsafe_allow_html=True)

# =========================================================
# EXIT VEHICLE
# =========================================================
elif menu == "Exit Vehicle":
    st.title("🚪 Exit System")

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

            metode = st.selectbox("Payment Method", ["QRIS", "Cash", "Transfer Bank"])

            st.markdown(f"""
            <div class="big-card">
                <h3>💰 Payment Summary</h3>
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

                st.markdown("""
                <div class="success">
                    🎉 PAYMENT SUCCESSFUL - VEHICLE EXITED
                </div>
                """, unsafe_allow_html=True)

        else:
            st.error("Vehicle not found")

# =========================================================
# ACTIVE PARKING
# =========================================================
elif menu == "Active Parking":
    st.title("🅿️ Active Parking List")

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
    st.title("📈 Business Analytics")

    df = pd.read_sql("SELECT total FROM parkir WHERE total IS NOT NULL", conn)

    if len(df) > 0:
        st.line_chart(df)
        st.bar_chart(df)
    else:
        st.info("No revenue data yet")