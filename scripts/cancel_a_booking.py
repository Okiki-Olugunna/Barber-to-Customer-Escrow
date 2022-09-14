from brownie import config
from web3 import Web3

# web3 connection
w3 = Web3(Web3.WebsocketProvider(config["provider"]["websockets"]))

# initialising the contract instance
with open("./contract_data/address.txt") as file_a:
    contract_address = file_a.read()

with open("./contract_data/abi.json") as file_b:
    contract_abi = file_b.read()

contract_instance = w3.eth.contract(address=contract_address, abi=contract_abi)


# initialising the aDai erc20 token
with open("./contract_data/erc20_abi.json") as file_c:
    a_dai_abi = file_c.read()

a_dai_token = w3.eth.contract(
    address="0x639cB7b21ee2161DF9c882483C9D55c90c20Ca3e", abi=a_dai_abi
)

# initialising regular DAI erc20 token
with open("./contract_data/erc20_abi.json") as file_d:
    erc20_abi = file_d.read()

dai_erc20_token = w3.eth.contract(  # aDai
    address="0x001B3B4d0F3714Ca98ba10F6042DaEbF0B1B7b6F", abi=erc20_abi
)


def main():
    print("\n--------------------------------------------- \n")
    print("STARTING THE CANCEL_A_BOOKING.PY SCRIPT\n")
    print("---------------------------------------------\n")

    # initialising the accounts
    print("Initialising the accoounts...\n")
    barber = config["wallets"]["from_key"]["main"]
    barber_address = config["addresses"]["main_address"]

    customer_1 = config["wallets"]["from_key"]["dev_2"]
    customer_1_address = config["addresses"]["dev_2_address"]

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

    # customer checks the haircut price of a fade
    print("Customer is checking the price of a fade...\n")
    haircut_price = contract_instance.functions.viewHairCutPrices(1).call()
    print(f"Haircut price of a fade is: {haircut_price}\n")

    print("Customer is fine with the price and is now proceeding to book...\n")

    # check customer balance before booking
    customer_dai_balance = dai_erc20_token.functions.balanceOf(
        customer_1_address
    ).call()
    converted_customer_balance = w3.fromWei(customer_dai_balance, "ether")
    print(f"The customer's current DAI balance is: {converted_customer_balance} DAI \n")

    # customer books a haircut
    print("Customer is booking a haircut...\n")
    nonce = w3.eth.get_transaction_count(customer_1_address)
    tx = contract_instance.functions.bookHairCut(
        "Jeff", 1, 1400, 1500  # name  # haircut type  # start time  # end time
    ).buildTransaction(
        {
            "gasPrice": w3.eth.gas_price,
            "chainId": 80001,
            "from": customer_1_address,
            "nonce": nonce,
        }
    )
    signed_tx = w3.eth.account.sign_transaction(tx, customer_1)
    send_tx = w3.eth.send_raw_transaction(signed_tx.rawTransaction)

    print("Waiting for the transaction receipt...\n")

    tx_receipt = w3.eth.wait_for_transaction_receipt(send_tx)
    print("--------------------------------------------")
    print(f"Transaction Receipt:\n{tx_receipt}")
    print("--------------------------------------------\n")

    print(f"Customer 1 ({customer_1_address}) has now made a booking!\n")

    # checking the booking ID
    print(f"The booking ID for customer 1 is: {tx} \n")  # the return value from the tx

    # check new contract balance in Aave
    a_dai_token_balance = a_dai_token.functions.balanceOf(contract_address).call()
    converted_balance = w3.fromWei(a_dai_token_balance, "ether")
    print(f"The contract's current aDai balance is: {converted_balance} aDAI \n")

    # check barber balance before haircut
    barber_dai_balance = dai_erc20_token.functions.balanceOf(barber_address).call()
    converted_barber_balance = w3.fromWei(barber_dai_balance, "ether")
    print(f"The barber's current DAI balance is: {converted_barber_balance} DAI \n")

    # check customer balance before haircut
    customer_dai_balance = dai_erc20_token.functions.balanceOf(
        customer_1_address
    ).call()
    converted_customer_balance = w3.fromWei(customer_dai_balance, "ether")
    print(f"The customer's new DAI balance is: {converted_customer_balance} DAI \n")

    # customer has realised they are in fact bald-headed, so no longer requires a haircut
    print(
        "Customer has realised he is bald-headed, so is proceeding to cancel the haircut... \n"
    )

    # customer is cancelling a haircut
    print("Customer is now cancelling the haircut... \n")

    nonce = w3.eth.get_transaction_count(customer_1_address)
    # booking ID = 1
    tx = contract_instance.functions.cancelBooking(1).buildTransaction(
        {
            "gasPrice": w3.eth.gas_price,
            "chainId": 80001,
            "from": customer_1_address,
            "nonce": nonce,
        }
    )
    signed_tx = w3.eth.account.sign_transaction(tx, customer_1)
    send_tx = w3.eth.send_raw_transaction(signed_tx.rawTransaction)

    print("Waiting for the transaction receipt...\n")

    tx_receipt = w3.eth.wait_for_transaction_receipt(send_tx)
    print("--------------------------------------------")
    print(f"Transaction Receipt:\n{tx_receipt}")
    print("--------------------------------------------\n")

    print(f"Customer 1 ({customer_1_address}) has now cancelled the booking! \n")

    # checking whether the booking still exists
    booking_exists = contract_instance.functions.bookingExists(1).call()
    print(f"Booking Exists? : {booking_exists}")

    # check barber's new balance - barber's balance should go up since they're getting some interest
    barber_new_dai_balance = dai_erc20_token.functions.balanceOf(barber_address).call()
    converted_barber_balance = w3.fromWei(barber_new_dai_balance, "ether")
    print(f"The barber's new DAI balance is: {converted_barber_balance} DAI ")
    # sanity check
    if barber_new_dai_balance > barber_dai_balance:
        print("This is higher than before the booked haircut, as expected.\n")

    # check customer's new balance - balance should go up - since they're getting refunded
    customer_new_dai_balance = dai_erc20_token.functions.balanceOf(
        customer_1_address
    ).call()
    converted_customer_balance = w3.fromWei(customer_new_dai_balance, "ether")
    print(f"The customer's new DAI is: {converted_customer_balance} DAI ")
    # sanity check
    if customer_new_dai_balance > customer_dai_balance:
        print("This is higher than after initially booking the haircut, as expected.\n")

    # check the contract's new balance on Aave - should have gone down
    new_a_dai_token_balance = a_dai_token.functions.balanceOf(contract_address).call()
    converted_balance = w3.fromWei(new_a_dai_token_balance, "ether")
    print(f"The contract's new aDai balance is: {converted_balance} aDAI \n")
    # sanity check
    if new_a_dai_token_balance < a_dai_token_balance:
        print("This is lower than when the haircut was booked, as expected.\n")

    print("\n--------------------------------------------- \n")
    print("CANCEL_A_BOOKING.PY SCRIPT IS NOW COMPLETE \n")
    print("---------------------------------------------\n")
