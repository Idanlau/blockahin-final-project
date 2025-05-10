import json
import os
from web3 import Web3
from dotenv import load_dotenv

def update_env_var(var_name, value):
    dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
    if not os.path.exists(dotenv_path):
        with open(dotenv_path, "w") as f:
            pass

    with open(dotenv_path, "r") as f:
        lines = f.readlines()

    updated = False
    for i, line in enumerate(lines):
        if line.startswith(f"{var_name}="):
            lines[i] = f"{var_name}={value}\n"
            updated = True
            break

    if not updated:
        lines.append(f"{var_name}={value}\n")

    with open(dotenv_path, "w") as f:
        f.writelines(lines)


if __name__ == "__main__":
    load_dotenv()

    # Connect to local Ganache
    w3 = Web3(Web3.HTTPProvider(os.getenv("WEB3_PROVIDER_URL")))
    PRIVATE_KEY = os.getenv("PRIVATE_KEY")
    account = w3.eth.account.from_key(PRIVATE_KEY)

    nonce = w3.eth.get_transaction_count(account.address)

    ### STEP 1: Deploy the NFT contract
    with open("nft.sol.abi") as f:
        nft_abi = json.load(f)
    with open("nft.sol.bin") as f:
        nft_bytecode = f.read()

    nft_contract = w3.eth.contract(abi=nft_abi, bytecode=nft_bytecode)

    tx = nft_contract.constructor().build_transaction({
        'from': account.address,
        'nonce': nonce,
        'gas': 3000000,
        'gasPrice': w3.to_wei('1', 'gwei'),
    })
    signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    print("🚀 Deploying NFT contract...")
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    nft_address = tx_receipt.contractAddress
    print(f"✅ NFT deployed at: {nft_address}")
    update_env_var("NFT_CONTRACT_ADDRESS", nft_address)
    nonce += 1

    ### STEP 2: Deploy the Loan contract
    with open("CollateralizedLoan.sol.abi") as f:
        loan_abi = json.load(f)
    with open("CollateralizedLoan.sol.bin") as f:
        loan_bytecode = f.read()

    interest_rate = 500  # 5%
    due_date = int(w3.eth.get_block("latest")["timestamp"]) + 7 * 24 * 60 * 60

    loan_contract = w3.eth.contract(abi=loan_abi, bytecode=loan_bytecode)

    tx = loan_contract.constructor(interest_rate, due_date).build_transaction({
        'from': account.address,
        'nonce': nonce,
        'gas': 3000000,
        'gasPrice': w3.to_wei('1', 'gwei'),
    })
    signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    print("📦 Deploying Loan contract...")
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    loan_address = tx_receipt.contractAddress
    print(f"✅ Loan contract deployed at: {loan_address}")
    update_env_var("CONTRACT_ADDRESS", loan_address)
