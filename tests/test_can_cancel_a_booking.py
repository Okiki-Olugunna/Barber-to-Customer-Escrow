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


def test_can_cancel_booking():
    # initialising the accounts
    barber = config["wallets"]["from_key"]["main"]
    barber_address = config["addresses"]["main_address"]

    customer_1 = config["wallets"]["from_key"]["dev_2"]
    customer_1_address = config["addresses"]["dev_2_address"]

    # opening up bookings
    current_booking_state = contract_instance.functions.bookingState().call()
    if current_booking_state != 1:
        # Barber is opening up the bookings...
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

        # Waiting for the transaction receipt...

        tx_receipt = w3.eth.wait_for_transaction_receipt(send_tx)
        tx_receipt

        current_booking_state = contract_instance.functions.bookingState().call()

    # customer checks the haircut price of a fade
    haircut_price = contract_instance.functions.FadePrice().call()

    # Customer is fine with the price and is now proceeding to book...

    # check customer balance before booking
    customer_wmatic_balance = wmatic_erc20_token.functions.balanceOf(
        customer_1_address
    ).call()

    # check contract balance before booking
    contract_wmatic_balance = wmatic_erc20_token.functions.balanceOf(
        contract_address
    ).call()

    # customer books a haircut
    # customer is approving the contract to spend the wmatic
    # Getting the nonce...
    nonce = w3.eth.get_transaction_count(customer_1_address)
    # Building the transaction...
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
    # Signing the transaction...
    signed_tx = w3.eth.account.sign_transaction(tx, customer_1)
    # Sending the transaction...
    send_tx = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    # Waiting for the transaction receipt of the approval...
    tx_receipt = w3.eth.wait_for_transaction_receipt(send_tx)
    tx_receipt

    # HAIRCUT BOOKING
    # Getting the nonce...
    nonce = w3.eth.get_transaction_count(customer_1_address)

    # Building the transaction...
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

    # Signing the transaction...
    signed_tx = w3.eth.account.sign_transaction(tx, customer_1)
    # Sending the transaction...
    send_tx = w3.eth.send_raw_transaction(signed_tx.rawTransaction)

    # Waiting for the transaction receipt...
    tx_receipt = w3.eth.wait_for_transaction_receipt(send_tx)
    tx_receipt

    # checking the booking ID
    current_booking_id = contract_instance.functions.currentBookingID().call()

    # check new contract balance in Aave after booking
    contract_am_wmatic_token_balance = am_wmatic_token.functions.balanceOf(
        contract_address
    ).call()

    # check barber balance before completion of haircut
    barber_wmatic_balance = wmatic_erc20_token.functions.balanceOf(
        barber_address
    ).call()

    # check customer balance before completion of haircut
    customer_wmatic_balance = wmatic_erc20_token.functions.balanceOf(
        customer_1_address
    ).call()

    ###############################################################################################
    ###############################################################################################
    ###############################################################################################

    # customer has realised they are in fact bald-headed, so no longer requires a haircut
    # customer is proceeding to cancel the haircut...

    # customer is now cancelling the haircut

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

    # Waiting for the transaction receipt...

    tx_receipt = w3.eth.wait_for_transaction_receipt(send_tx)
    tx_receipt

    # Customer 1 has now cancelled the booking

    ###############################################################################################
    ###############################################################################################
    ###############################################################################################

    # checking whether the booking still exists
    booking_exists = contract_instance.functions.bookingExists(1).call()
    assert booking_exists == False

    # check barber's new balance - barber's balance should go up since they're getting some interest
    barber_new_wmatic_balance = wmatic_erc20_token.functions.balanceOf(
        barber_address
    ).call()

    # sanity check
    assert barber_new_wmatic_balance > barber_wmatic_balance

    # check customer's new balance - balance should go up - since they're getting refunded
    customer_new_wmatic_balance = wmatic_erc20_token.functions.balanceOf(
        customer_1_address
    ).call()

    # sanity check
    assert customer_new_wmatic_balance > customer_wmatic_balance

    # check the contract's new balance on Aave - should have gone down
    new_contract_am_wmatic_token_balance = am_wmatic_token.functions.balanceOf(
        contract_address
    ).call()

    # sanity check
    assert new_contract_am_wmatic_token_balance < contract_am_wmatic_token_balance

    # end of test
