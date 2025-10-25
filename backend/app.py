import streamlit as st
import numpy as np
import joblib
from tensorflow.keras.models import load_model
import matplotlib.pyplot as plt
import yfinance as yf
from web3 import Web3
from model_utils import store_on_chain, load_contract
import os
from datetime import timedelta

# ================= Constants =================
SCALER = 'scaler.pkl'
GAN_MODEL = 'generator.h5'
SEQ_LEN = 20
FUTURE_DAYS = 30
NOISE_DIM = 10
GANACHE_URL = 'http://127.0.0.1:7545'
CONTRACT_JSON = '../build/contracts/Predictions.json'

# ================= Load models =================
@st.cache(allow_output_mutation=True)
def load_models():
    scaler = joblib.load(SCALER)
    gen = load_model(GAN_MODEL, compile=False)
    return gen, scaler

gen, scaler = load_models()

# ================= Prediction =================
def predict_future_prices(symbol):
    df = yf.download(symbol, period=f'{SEQ_LEN+1}d', interval='1h')  # hourly data
    if df.empty or len(df) < SEQ_LEN:
        st.error(f"Not enough data for {symbol}.")
        return None, None, None, None

    last_prices = df['Close'].values[-SEQ_LEN:].reshape(-1,1)
    scaled_context = scaler.transform(last_prices).flatten()
    context = scaled_context.copy()
    future_scaled = []

    # Get last timestamp from historical data
    last_timestamp = df.index[-1]

    future_dates = [last_timestamp + timedelta(hours=i*24) for i in range(1, FUTURE_DAYS+1)]

    for _ in range(FUTURE_DAYS):
        preds = []
        for _ in range(5):
            noise = np.random.normal(0,1,(1, NOISE_DIM))
            inp = np.concatenate([noise, context.reshape(1,-1)], axis=1)
            preds.append(gen.predict(inp, verbose=0)[0,0])
        next_day = np.mean(preds)
        future_scaled.append(next_day)
        context = np.roll(context, -1)
        context[-1] = next_day

    future_prices = scaler.inverse_transform(np.array(future_scaled).reshape(-1,1)).flatten()

    # Best buy/sell
    buy_idx = np.argmin(future_prices)
    sell_idx = np.argmax(future_prices)
    best_buy = (future_dates[buy_idx], future_prices[buy_idx])
    best_sell = (future_dates[sell_idx], future_prices[sell_idx])

    return future_dates, future_prices, best_buy, best_sell

# ================= Streamlit UI =================
st.title("💹 AI Stock Predictor - Best Buy/Sell Timestamp")
symbol = st.text_input("Enter stock symbol (e.g. AAPL, TSLA, NIFTY):")

if st.button("Predict & Recommend") and symbol:
    st.info(f"🔮 Predicting {symbol.upper()} prices for next {FUTURE_DAYS} days (timestamps included)...")
    dates, prices, best_buy, best_sell = predict_future_prices(symbol.upper())

    if dates is not None:
        # Plot trend
        fig, ax = plt.subplots(figsize=(12,6))
        ax.plot(dates, prices, label='Predicted Prices', color='blue')
        ax.scatter(best_buy[0], best_buy[1], color='green', s=100, label='Best BUY')
        ax.scatter(best_sell[0], best_sell[1], color='red', s=100, label='Best SELL')
        ax.set_title(f"{symbol.upper()} Price Prediction & Best Buy/Sell")
        ax.set_xlabel("Timestamp")
        ax.set_ylabel("Price")
        ax.legend()
        plt.xticks(rotation=45)
        st.pyplot(fig)

        # Show best buy/sell with full timestamp
        st.subheader("📊 Best Recommendation")
        st.write(f"✅ Best **BUY**: {best_buy[0].strftime('%Y-%m-%d %H:%M:%S')} at price ${best_buy[1]:.2f}")
        st.write(f"🔴 Best **SELL**: {best_sell[0].strftime('%Y-%m-%d %H:%M:%S')} at price ${best_sell[1]:.2f}")

        # Store on blockchain with transaction details
        if os.path.exists(CONTRACT_JSON):
            st.info("⛓️ Storing best buy/sell points on blockchain...")
            try:
                w3 = Web3(Web3.HTTPProvider(GANACHE_URL))
                contract = load_contract(w3, CONTRACT_JSON)

                tx_receipts = []
                tx_receipts.append(store_on_chain(symbol.upper(), float(best_buy[1])))
                tx_receipts.append(store_on_chain(symbol.upper(), float(best_sell[1])))

                st.success("✅ Stored successfully on blockchain!")
                st.subheader("📄 Transaction Details")

                for i, tx in enumerate(tx_receipts):
                    st.write(f"Transaction {i+1}:")
                    st.write(f"- Transaction Hash: {tx.transactionHash.hex()}")
                    st.write(f"- Block Hash: {tx.blockHash.hex()}")
                    st.write(f"- Gas Used: {tx.gasUsed}")
                    st.write(f"- Gas Price: {tx.effectiveGasPrice}")
                    st.write(f"- Cumulative Gas Used: {tx.cumulativeGasUsed}")
                    st.write(f"- Status: {'Success' if tx.status==1 else 'Failed'}")
                    st.write("---")

            except Exception as e:
                st.error(f"⚠️ Blockchain storage failed: {e}")
        else:
            st.warning("⚠️ Contract JSON not found. Skipping blockchain storage.")
