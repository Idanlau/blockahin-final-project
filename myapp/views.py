import json
import os
from django.http import JsonResponse
from web3 import Web3
from dotenv import load_dotenv
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render

@csrf_exempt
def repay_loan(request):
    load_dotenv()

    w3 = Web3(Web3.HTTPProvider(os.getenv("WEB3_PROVIDER_URL")))
    PRIVATE_KEY = os.getenv("PRIVATE_KEY")
    account = w3.eth.account.from_key(PRIVATE_KEY)

    with open("/Users/idanlau/Desktop/blockchain-final/myproject/myapp/CollateralizedLoan.sol.abi") as f:
        abi = json.load(f)

    contract = w3.eth.contract(
        address=Web3.to_checksum_address(os.getenv("CONTRACT_ADDRESS")),
        abi=abi
    )

    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    # try:
    nonce = w3.eth.get_transaction_count(account.address)

    # Get loanAmount and interestRate from contract
    loan_amount = contract.functions.loanAmount().call()
    interest_rate = contract.functions.interestRate().call()

    # Calculate repayment
    repayment = loan_amount + ((loan_amount * interest_rate) // 10000)

    tx = contract.functions.repay().build_transaction({
        'from': account.address,
        'value': repayment,
        'gas': 300000,
        'gasPrice': w3.to_wei('30', 'gwei'),
        'nonce': nonce,
    })

    signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)


    return JsonResponse({
        "message": "Repayment transaction sent",
        "tx_hash": tx_hash.hex(),
    })

    # except Exception as e:
    #     return JsonResponse({"error": str(e)}, status=500)

def loan_repayment_page(request):
    return render(request, 'myapp/loan_repayment.html')
