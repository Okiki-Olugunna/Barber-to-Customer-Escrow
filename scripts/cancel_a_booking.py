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


# initialising the amWMATIC erc20 token
with open("./contract_data/erc20_abi.json") as file_c:
    a_dai_abi = file_c.read()

am_wmatic_token = w3.eth.contract(
    address="0xF45444171435d0aCB08a8af493837eF18e86EE27", abi=a_dai_abi
)

# initialising regular WMATIC erc20 token
with open("./contract_data/erc20_abi.json") as file_d:
    erc20_abi = file_d.read()

wmatic_erc20_token = w3.eth.contract(
    address="0x9c3C9283D3e44854697Cd22D3Faa240Cfb032889", abi=erc20_abi
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
    print("Getting the current booking state... \n")
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
    # haircut_price = contract_instance.functions.viewHairCutPrices(1).call()
    haircut_price = contract_instance.functions.FadePrice().call()
    converted_haircut_price = w3.fromWei(haircut_price, "ether")
    print(f"Haircut price of a fade is: {converted_haircut_price} WMATIC\n")

    print("Customer is fine with the price and is now proceeding to book...\n")

    # check customer balance before booking
    customer_wmatic_balance = wmatic_erc20_token.functions.balanceOf(
        customer_1_address
    ).call()
    converted_customer_balance = w3.fromWei(customer_wmatic_balance, "ether")
    print(
        f"The customer's current WMATIC balance is: {converted_customer_balance} WMATIC \n"
    )

    # check contract balance before booking
    contract_wmatic_balance = wmatic_erc20_token.functions.balanceOf(
        contract_address
    ).call()
    converted_contract_balance = w3.fromWei(contract_wmatic_balance, "ether")
    print(
        f"The contract's current WMATIC balance is: {converted_contract_balance} WMATIC \n"
    )

    # customer books a haircut
    print("Customer is booking a haircut...\n")

    # customer is approving the contract to spend the wmatic
    print("Customer is approving the booking contract to spend the WMATIC... \n ")
    print("Getting the nonce...")
    nonce = w3.eth.get_transaction_count(customer_1_address)
    print("Building the transaction...")
    tx = wmatic_erc20_token.functions.approve(
        contract_address, haircut_price
    ).buildTransaction(
        {
            "gasPrice": w3.eth.gas_price,
            "gas": 10_000_000,
            "chainId": 80001,
            "from": customer_1_address,
            "nonce": nonce,
        }
    )
    print("Signing the transaction...")
    signed_tx = w3.eth.account.sign_transaction(tx, customer_1)
    print("Sending the transaction...")
    send_tx = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    print("Waiting for the transaction receipt of the approval...")
    tx_receipt = w3.eth.wait_for_transaction_receipt(send_tx)
    print("--------------------------------------------")
    print(f"Transaction Receipt of approval: \n{tx_receipt}")
    print("--------------------------------------------\n")

    # HAIRCUT BOOKING
    print("Now calling the booking function for the haircut..\n")
    print("Getting the nonce...\n")
    nonce = w3.eth.get_transaction_count(customer_1_address)
    print("Got the nonce.\n")

    print("Building the transaction...\n")

    name = "Jeff"
    start_time = 1400
    end_time = 1500

    tx = contract_instance.functions.bookAFade(
        name,
        start_time,
        end_time,
    ).buildTransaction(
        {
            "gasPrice": w3.eth.gas_price,
            "gas": 10_000_000,
            "chainId": 80001,
            "from": customer_1_address,
            "nonce": nonce,
        }
    )
    print("Transaction built.\n")

    print("Signing the transaction...\n")
    signed_tx = w3.eth.account.sign_transaction(tx, customer_1)
    print("Sending the transaction...\n")
    send_tx = w3.eth.send_raw_transaction(signed_tx.rawTransaction)

    print("Waiting for the transaction receipt...\n")

    tx_receipt = w3.eth.wait_for_transaction_receipt(send_tx)
    print("--------------------------------------------")
    print(f"Transaction Receipt:\n{tx_receipt}")
    print("--------------------------------------------\n")

    print(f"Customer 1 ({customer_1_address}) has now made a booking!\n")

    # checking the booking ID
    current_booking_id = contract_instance.functions.currentBookingID().call()
    print(f"The booking ID for customer 1 is: {current_booking_id} \n")

    # check contract balance after booking
    contract_wmatic_balance = wmatic_erc20_token.functions.balanceOf(
        contract_address
    ).call()
    converted_contract_balance = w3.fromWei(contract_wmatic_balance, "ether")
    print(
        f"The contract's current WMATIC balance is: {converted_contract_balance} WMATIC \n"
    )

    # check new contract balance in Aave
    contract_am_wmatic_token_balance = am_wmatic_token.functions.balanceOf(
        contract_address
    ).call()
    converted_balance = w3.fromWei(contract_am_wmatic_token_balance, "ether")
    print(
        f"The contract's current amWMATIC balance is: {converted_balance} amWMATIC \n"
    )

    # check barber balance before completion of haircut
    barber_wmatic_balance = wmatic_erc20_token.functions.balanceOf(
        barber_address
    ).call()
    converted_barber_balance = w3.fromWei(barber_wmatic_balance, "ether")
    print(
        f"The barber's current WMATIC balance is: {converted_barber_balance} WMATIC \n"
    )

    # check customer balance before completion of haircut
    customer_wmatic_balance = wmatic_erc20_token.functions.balanceOf(
        customer_1_address
    ).call()
    converted_customer_balance = w3.fromWei(customer_wmatic_balance, "ether")
    print(f"The customer's WMATIC balance is: {converted_customer_balance} WMATIC \n")

    ###############################################################################################
    ###############################################################################################
    ###############################################################################################

    # customer has realised they are in fact bald-headed, so no longer requires a haircut
    print(
        "\n---------------------------------------------------------------------------------"
    )
    print(
        "Customer has realised he is bald-headed, so is proceeding to cancel the haircut... \n"
    )
    print(
        "\n---------------------------------------------------------------------------------"
    )

    # customer is cancelling a haircut
    print("Customer is now cancelling the haircut... \n")

    nonce = w3.eth.get_transaction_count(customer_1_address)

    tx = contract_instance.functions.cancelBooking(current_booking_id).buildTransaction(
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

    ###############################################################################################
    ###############################################################################################
    ###############################################################################################

    # checking whether the booking still exists
    booking_exists = contract_instance.functions.bookingExists(1).call()
    print(f"Does this booking still exist?: {booking_exists} ")
    if booking_exists == False:
        print("This booking no longer exists.\n")
    else:
        print("Something went wrong. Please try again.\n")

    # check barber's new balance - barber's balance should go up since they're getting some interest
    barber_new_wmatic_balance = wmatic_erc20_token.functions.balanceOf(
        barber_address
    ).call()
    converted_barber_balance = w3.fromWei(barber_new_wmatic_balance, "ether")
    print(f"The barber's new WMATIC balance is: {converted_barber_balance} WMATIC ")
    # sanity check
    if barber_new_wmatic_balance > barber_wmatic_balance:
        print("This is higher than before the booked haircut, as expected.\n")

    # check customer's new balance - balance should go up - since they're getting refunded
    customer_new_wmatic_balance = wmatic_erc20_token.functions.balanceOf(
        customer_1_address
    ).call()
    converted_customer_balance = w3.fromWei(customer_new_wmatic_balance, "ether")
    print(f"The customer's new WMATIC is: {converted_customer_balance} WMATIC ")
    # sanity check
    if customer_new_wmatic_balance > customer_wmatic_balance:
        print("This is higher than after initially booking the haircut, as expected.\n")

    # check the contract's new balance on Aave - should have gone down
    new_contract_am_wmatic_token_balance = am_wmatic_token.functions.balanceOf(
        contract_address
    ).call()
    converted_balance = w3.fromWei(new_contract_am_wmatic_token_balance, "ether")
    print(f"The contract's new amWMATIC balance is: {converted_balance} amWMATIC ")
    # sanity check
    if new_contract_am_wmatic_token_balance < contract_am_wmatic_token_balance:
        print("This is lower than when the haircut was booked, as expected.\n")

    print("\n--------------------------------------------- \n")
    print("CANCEL_A_BOOKING.PY SCRIPT IS NOW COMPLETE \n")
    print("---------------------------------------------\n")
