AI Stock Price Prediction with GAN & Blockchain
📌 Overview

This project predicts future stock prices using a Generative Adversarial Network (GAN) and provides the best day to buy and sell a stock. All recommendations are optionally stored on a blockchain (Ganache) for immutability and security.

⚡ Features

Predicts stock prices for the next 30 days using historical data.

Identifies the optimal buy and sell day.

Visualizes price trends and recommendations with charts.

Stores buy/sell points on Ethereum blockchain for safety.

Fetches live stock data directly via Yahoo Finance.

🛠 Tech Stack

Frontend: Streamlit

Backend/ML: Python, TensorFlow/Keras, GAN, NumPy, Pandas

Blockchain: Ethereum (Ganache), Web3.py

Data Source: Yahoo Finance

📂 Files

backend/train_gan.py – GAN model training

backend/generator.h5 – Pretrained generator model

backend/scaler.pkl – Pretrained data scaler

backend/app.py – Streamlit UI and prediction logic

build/contracts/Predictions.json – Compiled blockchain contract

contracts/Predictions.sol – Solidity smart contract

🚀 How to Run

Clone the repo:

git clone https://github.com/catherine621/stockprice-prediction-using-ai-and-blockchain.git


Install dependencies:

pip install -r backend/requirements.txt


Run the Streamlit app:

streamlit run backend/app.py


Enter a stock symbol (e.g., AAPL, TSLA, NIFTY) and get predictions.
