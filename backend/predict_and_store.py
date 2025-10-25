import sys
import pandas as pd
import joblib
from web3 import Web3
from model_utils import make_prediction, load_contract  # You should define these in a separate file or same folder

SCALER = 'scaler.pkl'
CONTRACT_JSON = 'contract.json'


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage: python predict_and_store.py path/to/stock.csv SYMBOL')
        sys.exit(1)

    csv_path = sys.argv[1]
    symbol = sys.argv[2]

    # Prepare context window (last seq_len values)
    seq_len = 20
    df = pd.read_csv(csv_path)
    prices = df['Close'].values.reshape(-1, 1)

    scaler = joblib.load(SCALER)
    p_scaled = scaler.transform(prices)
    context = p_scaled[-seq_len:].flatten()

    # Predict next price using trained GAN generator
    price = make_prediction(context)
    print('Predicted price:', price)

    # Connect to Ganache
    w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:7545'))
    assert w3.isConnected(), 'Not connected to Ganache'

    # Load smart contract
    contract = load_contract(w3, CONTRACT_JSON)
    acct = w3.eth.accounts[0]

    # Convert price to integer (multiplied by 100 for precision)
    price_int = int(round(price * 100))

    # Build transaction to store prediction
    tx = contract.functions.storePrediction(symbol, price_int).buildTransaction({
        'from': acct,
        'nonce': w3.eth.get_transaction_count(acct),
        'gas': 2000000,
        'gasPrice': w3.toWei('20', 'gwei')
    })

    # Try sending directly (for unlocked Ganache accounts)
    try:
        tx_hash = w3.eth.send_transaction({
            'from': acct,
            'to': contract.address,
            'data': contract.encodeABI(fn_name='storePrediction', args=[symbol, price_int])
        })
        print('Transaction sent successfully:', tx_hash.hex())

    except Exception as e:
        print('Unlocked account failed, fallback to signing manually:', e)

        # Example of manual signing (if Ganache account locked)
        # ⚠️ Replace with actual private key from Ganache
        PRIVATE_KEY = ''
        if PRIVATE_KEY:
            signed = w3.eth.account.sign_transaction(tx, private_key=PRIVATE_KEY)
            tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
            print('Signed transaction sent:', tx_hash.hex())
        else:
            print('No private key provided. Please unlock account or set PRIVATE_KEY.')
