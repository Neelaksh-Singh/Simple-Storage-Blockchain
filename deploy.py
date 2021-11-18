from solcx import compile_standard, install_solc
from web3 import Web3
import json, os
from dotenv import load_dotenv

load_dotenv()

with open("./SimpleStorage.sol", "r") as file:
    simple_storage_file = file.read()
    

install_solc("0.6.0")
compiled_sol = compile_standard({
    "language": "Solidity",
    "sources" : {"SimpleStorage.sol": {"content": simple_storage_file}},
    "settings":{
        "outputSelection": {
            "*":{
                "*": ["abi", "metadata","evm.bytecode","evm.sourceMap"]
            }

        }
    }
}, solc_version="0.6.0")

# print(compiled_sol)

with open("compiled_code.json","w") as file:
    json.dump(compiled_sol,file)



# get Bytecode, ABI

bytecode = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"]["bytecode"]["object"]
abi = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["abi"]

#for connecting ganache

w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
chain_id = 1337
my_address = "your_address"
pv_key = os.getenv("PRIVATE_KEY")


#Createing contract in python

SimpleStorage = w3.eth.contract(abi=abi, bytecode=bytecode)
# print(SimpleStorage)
#Getting our latest transaction
nonce = w3.eth.get_transaction_count(my_address)
# print(nonce)

# 1. Build a transaction
#2. Sign a Transaction
# 3. Send a Transaction

transaction = SimpleStorage.constructor().buildTransaction({"chainId": chain_id, "from": my_address, "nonce": nonce})
# print(transaction)

signed_txn = w3.eth.account.sign_transaction(transaction,private_key=pv_key)

# Send this transaction
print("Being Deployed...")
tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
tx_reciept = w3.eth.wait_for_transaction_receipt(tx_hash)
print("Deployed!!")
#Working with contract we need ->
# 1. Contract Address and 2. Contract ABI

simple_storage = w3.eth.contract(address=tx_reciept.contractAddress, abi=abi)
# Call -> Simulate making call and getting values(like blue-button in remix)
# Transact -> Actually make state change(build and send transaction)

# initial value of favourite no
print(simple_storage.functions.retrieve().call())
print("Updating Contract.....")
# print(simple_storage.functions.store(15).call())

store_transaction = simple_storage.functions.store(15).buildTransaction(
    {"chainId": chain_id, "from": my_address, "nonce": nonce+1}
)

signed_store_txn = w3.eth.account.sign_transaction(store_transaction,private_key=pv_key)
send_store_txn = w3.eth.send_raw_transaction(signed_store_txn.rawTransaction)
transaction_reciept = w3.eth.wait_for_transaction_receipt(send_store_txn)
print("Updated!!")
print(simple_storage.functions.retrieve().call())