import json, os
from web3 import Web3
from dotenv import load_dotenv

def send(tx_dict, label):
    """Sign, send, and wait for a transaction to be mined."""
    signed = w3.eth.account.sign_transaction(tx_dict, PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    print(f"✅ {label} → {tx_hash.hex()}")
    return receipt

if __name__ == "__main__":
    load_dotenv()

    # Connect to Ganache
    w3 = Web3(Web3.HTTPProvider(os.getenv("WEB3_PROVIDER_URL")))
    PRIVATE_KEY = os.getenv("PRIVATE_KEY")
    account = w3.eth.account.from_key(PRIVATE_KEY)
    borrower_address = account.address

    # Load ABIs
    with open("CollateralizedLoan.sol.abi") as f:
        loan_abi = json.load(f)
    with open("nft.sol.abi") as f:
        nft_abi = json.load(f)

    # Load contracts
    loan_contract = w3.eth.contract(
        address=Web3.to_checksum_address(os.getenv("CONTRACT_ADDRESS")),
        abi=loan_abi
    )
    nft_contract = w3.eth.contract(
        address=Web3.to_checksum_address(os.getenv("NFT_CONTRACT_ADDRESS")),
        abi=nft_abi
    )

    token_id = 0
    loan_amount = w3.to_wei(1, 'ether')
    gas_price = w3.to_wei('1', 'gwei')
    nonce = w3.eth.get_transaction_count(account.address)

    # 1. Fund the loan
    print("📤 Funding loan...")
    tx = loan_contract.functions.fundLoan(borrower_address, loan_amount).build_transaction({
        'from': account.address,
        'value': loan_amount,
        'gas': 300_000,
        'gasPrice': gas_price,
        'nonce': nonce,
    })
    send(tx, "Loan funded")
    nonce += 1

    # 2. Mint NFT
    print("🪙 Minting NFT...")
    tx = nft_contract.functions.mint().build_transaction({
        'from': account.address,
        'gas': 200_000,
        'gasPrice': gas_price,
        'nonce': nonce,
    })
    send(tx, "NFT minted")
    nonce += 1

    # 3. Approve loan contract to transfer NFT
    print("🔏 Approving NFT for loan contract...")
    tx = nft_contract.functions.approve(loan_contract.address, token_id).build_transaction({
        'from': account.address,
        'gas': 100_000,
        'gasPrice': gas_price,
        'nonce': nonce,
    })
    send(tx, "NFT approved")
    nonce += 1

    # 4. Deposit NFT as collateral
    print("📤 Depositing NFT as collateral...")
    tx = loan_contract.functions.depositCollateral(nft_contract.address, token_id).build_transaction({
        'from': account.address,
        'gas': 300_000,
        'gasPrice': gas_price,
        'nonce': nonce,
    })
    send(tx, "Collateral deposited")

    # ✅ Final state check
    state = loan_contract.functions.state().call()
    print("🏁 Loan state:", state)  # should be 2 (Collateralized)
