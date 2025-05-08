import json
import os
from django.http import JsonResponse
from web3 import Web3
from dotenv import load_dotenv
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render  # Add this import



@csrf_exempt
def repay_loan(request):


    load_dotenv()  # Optional: load ENV vars from .env

    # Connect to Ethereum
    w3 = Web3(Web3.HTTPProvider(os.getenv("WEB3_PROVIDER_URL")))  # e.g. Infura/Alchemy

    # Load Contract ABI and Address
    with open("/Users/idanlau/Desktop/blockchain-final/myproject/myapp/CollateralizedLoanABI.json") as f:
        abi = json.load(f)

    contract = w3.eth.contract(
        address=Web3.to_checksum_address(os.getenv("CONTRACT_ADDRESS")),
        abi=abi
    )

    PRIVATE_KEY = os.getenv("PRIVATE_KEY")  # Keep this secret and secure!
    
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    try:
        account = w3.eth.account.from_key(PRIVATE_KEY)
        nonce = w3.eth.get_transaction_count(account.address)

        # Call contract to get repayment amount
        repayment = contract.functions.getRepaymentAmount().call()

        tx = contract.functions.repay().build_transaction({
            'from': account.address,
            'value': repayment,
            'gas': 300000,
            'gasPrice': w3.to_wei('30', 'gwei'),
            'nonce': nonce,
        })

        signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)

        return JsonResponse({
            "message": "Transaction sent",
            "tx_hash": tx_hash.hex(),
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# Add the new view function here
def loan_repayment_page(request):
    return render(request, 'myapp/loan_repayment.html')