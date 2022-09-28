from brownie import accounts, config
from web3 import Web3
from decimal import Decimal

# web3 connection
w3 = Web3(Web3.WebsocketProvider(config["provider"]["websockets"]))

# initialising the contract instance
with open("./contract_data/address.txt") as file_a:
    contract_address = file_a.read()

with open("./contract_data/abi.json") as file_b:
    contract_abi = file_b.read()

contract_instance = w3.eth.contract(address=contract_address, abi=contract_abi)

# initialising WMATIC erc20 token
with open("./contract_data/erc20_abi.json") as file_c:
    erc20_abi = file_c.read()

wmatic_erc20_token = w3.eth.contract(
    address="0x9c3C9283D3e44854697Cd22D3Faa240Cfb032889", abi=erc20_abi
)


def main():
    print("\n------------------------------------------- \n")
    print("STARTING THE TIP_THE_BARBER.PY SCRIPT \n ")
    print("------------------------------------------- \n")

    # initialising the accounts
    print("Initialising the accoounts...\n")
    barber = config["wallets"]["from_key"]["main"]
    barber_address = config["addresses"]["main_address"]

    customer_1 = config["wallets"]["from_key"]["dev_2"]
    customer_1_address = config["addresses"]["dev_2_address"]
    print("Accounts initialised. \n")

    # check barber's balance
    initial_barber_wmatic_balance = wmatic_erc20_token.functions.balanceOf(
        barber_address
    ).call()
    converted_barber_balance = w3.fromWei(initial_barber_wmatic_balance, "ether")
    print(
        f"The barber's current WMATIC balance is: {converted_barber_balance} WMATIC \n"
    )

    # check customer balance
    initial_customer_wmatic_balance = wmatic_erc20_token.functions.balanceOf(
        customer_1_address
    ).call()
    converted_customer_balance = w3.fromWei(initial_customer_wmatic_balance, "ether")
    print(
        f"The customer's current WMATIC balance is: {converted_customer_balance} WMATIC \n"
    )

    # customer makes a tip
    print("The customer is going to give the barber a tip for his great service... \n")

    tip_amount = 10
    print(f"The tip amount will be {tip_amount} \n")

    print("Approving the contract to spend the customer's WMATIC...\n")
    nonce = w3.eth.get_transaction_count(customer_1_address)
    tx = wmatic_erc20_token.functions.approve(
        contract_address, tip_amount
    ).buildTransaction(
        {
            "gasPrice": w3.eth.gas_price,
            "chainId": 80001,
            "from": customer_1_address,
            "nonce": nonce,
        }
    )
    print("Signing the transaction...")
    signed_tx = w3.eth.account.sign_transaction(tx, customer_1)
    print("Sending the transaction...")
    send_tx = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    print("Waiting for the transaction receipt...")
    tx_receipt = w3.eth.wait_for_transaction_receipt(send_tx)
    print("\n--------------------------------------------")
    print(f"Transaction Receipt:\n{tx_receipt}")
    print("--------------------------------------------\n")
    print("The contract has been approved to spend the WMATIC tokens.\n")

    # sending the tip
    print("Now calling the function to send a tip...\n")
    print("Getting the nonce..")
    nonce = w3.eth.get_transaction_count(customer_1_address)
    print("Building the transaction...")
    tx = contract_instance.functions.tip(tip_amount).buildTransaction(
        {
            "gasPrice": w3.eth.gas_price,
            "chainId": 80001,
            "from": customer_1_address,
            "nonce": nonce,
        }
    )
    print("Signing the transaction...")
    signed_tx = w3.eth.account.sign_transaction(tx, customer_1)
    print("Sending the transaction...")
    send_tx = w3.eth.send_raw_transaction(signed_tx.rawTransaction)

    print("Waiting for the transaction receipt...\n")

    tx_receipt = w3.eth.wait_for_transaction_receipt(send_tx)
    print("--------------------------------------------")
    print(f"Transaction Receipt:\n{tx_receipt}")
    print("--------------------------------------------\n")

    print("The tip has been sent! \n")

    # check the new balances

    # check barber's balance
    barber_wmatic_balance = wmatic_erc20_token.functions.balanceOf(
        barber_address
    ).call()
    converted_barber_balance = w3.fromWei(barber_wmatic_balance, "ether")
    print(f"The barber's new WMATIC balance is: {converted_barber_balance} WMATIC ")
    if barber_wmatic_balance > initial_barber_wmatic_balance:
        print("This is greater than the initial amount as expected.\n")

    # check customer balance
    customer_wmatic_balance = wmatic_erc20_token.functions.balanceOf(
        customer_1_address
    ).call()
    converted_customer_balance = w3.fromWei(customer_wmatic_balance, "ether")
    print(f"The customer's new WMATIC balance is: {converted_customer_balance} WMATIC ")
    if customer_wmatic_balance < initial_customer_wmatic_balance:
        print("This is less than the initial amount as expected.\n")

    print("------------------------------------------- \n")
    print("END OF TIP_THE_BARBER.PY SCRIPT \n")
    print("------------------------------------------- \n")
