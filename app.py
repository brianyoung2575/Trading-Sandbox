import streamlit as st
import matplotlib.pyplot as plt
import time
import uuid
from pricegenerator import step_price
from engine import create_position, update_position

st.session_state.price = getattr(st.session_state, "price", 100.0)
st.session_state.history = getattr(st.session_state, "history", [100.0])
st.session_state.positions = getattr(st.session_state, "positions", [])
st.session_state.balance = getattr(st.session_state, "balance", 10000.0)
st.session_state.last_update = getattr(st.session_state, "last_update", time.time())
st.session_state.close_id = getattr(st.session_state, "close_id", None)

if st.session_state.close_id is not None:
    close_id = st.session_state.close_id

    new_positions = []
    for pos in st.session_state.positions:
        if pos["id"] == close_id:
            st.session_state.balance += pos["pnl"]
        else:
            new_positions.append(pos)

    st.session_state.positions = new_positions
    st.session_state.close_id = None

now = time.time()
if now - st.session_state.last_update >= 3:
    st.session_state.price = step_price(st.session_state.price)
    st.session_state.history.append(st.session_state.price)
    st.session_state.last_update = now

total_pnl = 0
market_value = 0

for pos in st.session_state.positions:
    update_position(pos, st.session_state.price)
    total_pnl += pos["pnl"]

    if pos["direction"] == "long":
        market_value += pos["size"] * st.session_state.price
    else:
        market_value -= pos["size"] * st.session_state.price

equity = st.session_state.balance + total_pnl
lot_size = st.sidebar.number_input("Lot Size", min_value=1, value=10)
order_cost = st.session_state.price * lot_size
st.sidebar.metric("Order Cost", f"${order_cost:.2f}")
col1, col2 = st.sidebar.columns(2)

def open_position(direction):
    notional = lot_size * st.session_state.price
    current_exposure = sum(p["size"] * st.session_state.price for p in st.session_state.positions)

    if current_exposure + notional > st.session_state.balance:
        st.sidebar.warning("Not enough money")
        return

    pos = create_position(direction, st.session_state.price, lot_size)
    pos["id"] = str(uuid.uuid4())
    pos["cost"] = st.session_state.price * lot_size
    st.session_state.positions.append(pos)

with col1:
    if st.button("Long"):
        open_position("long")

with col2:
    if st.button("Short"):
        open_position("short")

st.sidebar.metric("Equity", f"${equity:.2f}")
st.sidebar.metric("PnL", f"${total_pnl:.2f}")
st.sidebar.metric("Market Value", f"${market_value:.2f}")

st.title("Trading Sandbox")
fig, ax = plt.subplots(figsize=(6, 2.5))
ax.plot(st.session_state.history)
ax.set_title(f"Price: {st.session_state.price:.2f}")
st.pyplot(fig)

st.subheader("Open Positions")

if not st.session_state.positions:
    st.write("No positions open")
else:
    for pos in st.session_state.positions:
        col1, col2 = st.columns([4, 1])

        with col1:
            st.write(
                f"{pos['direction'].upper()} | "
                f"Entry: {pos['entry_price']:.2f} | "
                f"Size: {pos['size']} | "
                f"PnL: {pos['pnl']:.2f}")

        with col2:
            if st.button("Close", key=pos["id"]):
                st.session_state.close_id = pos["id"]
                st.rerun()

time.sleep(3)
st.rerun()