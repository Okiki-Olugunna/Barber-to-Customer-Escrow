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


def main():
    print("\n--------------------------------------------- \n")
    print("STARTING THE OPEN_THE_BOOKINGS.PY SCRIPT\n")
    print("---------------------------------------------\n")

    # initialising the accounts
    print("Initialising the barber's account...\n")
    barber = config["wallets"]["from_key"]["main"]
    barber_address = config["addresses"]["main_address"]

    print("Accounts initialised.\n")

    # barber needs to open up bookings
    current_booking_state = contract_instance.functions.bookingState().call()
    print(f"The current booking state: {current_booking_state}\n")

    if current_booking_state != 1:
        print("Barber is opening up the bookings...\n")

        nonce = w3.eth.get_transaction_count(barber_address)
        tx = contract_instance.functions.openUpBookings().buildTransaction(
            {
                "gasPrice": w3.eth.gas_price,
                "chainId": 80001,
                "from": barber_address,
                "nonce": nonce,
            }
        )
        signed_tx = w3.eth.account.sign_transaction(tx, barber)
        send_tx = w3.eth.send_raw_transaction(signed_tx.rawTransaction)

        print("Waiting for the transaction receipt...\n")

        tx_receipt = w3.eth.wait_for_transaction_receipt(send_tx)
        print("--------------------------------------------")
        print(f"Transaction Receipt:\n{tx_receipt}")
        print("--------------------------------------------\n")

        current_booking_state = contract_instance.functions.bookingState().call()
        print(f"The current booking state: {current_booking_state}\n")

    print("Bookings are now open.\n")
