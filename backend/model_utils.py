import json
from web3 import Web3

GANACHE_URL = 'http://127.0.0.1:7545'
CONTRACT_JSON = '../build/contracts/Predictions.json'

def load_contract(web3, contract_json_path=CONTRACT_JSON):
    with open(contract_json_path) as f:
        info = json.load(f)
    abi = info['abi']
    deployed_address = list(info['networks'].values())[0]['address']
    return web3.eth.contract(address=deployed_address, abi=abi)

def store_on_chain(symbol, price):
    w3 = Web3(Web3.HTTPProvider(GANACHE_URL))
    contract = load_contract(w3)
    acct = w3.eth.accounts[0]
    tx = contract.functions.storePrediction(symbol, int(price*100)).transact({'from': acct})
    receipt = w3.eth.wait_for_transaction_receipt(tx)
    return receipt
