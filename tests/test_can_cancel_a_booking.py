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


def test_can_cancel_a_booking():
    # initialising the accounts
    barber = config["wallets"]["from_key"]["main"]
    barber_address = config["addresses"]["main_address"]

    customer_1 = config["wallets"]["from_key"]["dev_2"]
    customer_1_address = config["addresses"]["dev_2_address"]

    # barber needs to open up bookings
    current_booking_state = contract_instance.functions.bookingState().call()

    if current_booking_state != 1:
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

        current_booking_state = contract_instance.functions.bookingState().call()

    # Bookings are now open

    # customer checks the haircut price of a fade
    haircut_price = contract_instance.functions.viewHairCutPrices(1).call()

    # Customer is fine with the price and is now proceeding to book...

    # checking customer balance before booking
    customer_dai_balance = dai_erc20_token.functions.balanceOf(
        customer_1_address
    ).call()
    converted_customer_balance = w3.fromWei(customer_dai_balance, "ether")

    # customer books a haircut
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

    # Waiting for the transaction receipt...

    tx_receipt = w3.eth.wait_for_transaction_receipt(send_tx)

    # Customer 1 has now made a booking

    # check new contract balance in Aave
    a_dai_token_balance = a_dai_token.functions.balanceOf(contract_address).call()
    converted_balance = w3.fromWei(a_dai_token_balance, "ether")

    # check barber balance before haircut
    barber_dai_balance = dai_erc20_token.functions.balanceOf(barber_address).call()
    converted_barber_balance = w3.fromWei(barber_dai_balance, "ether")

    # check customer balance before haircut
    customer_dai_balance = dai_erc20_token.functions.balanceOf(
        customer_1_address
    ).call()
    converted_customer_balance = w3.fromWei(customer_dai_balance, "ether")

    # customer has realised they are in fact bald-headed, so no longer requires a haircut

    # customer is cancelling a haircut

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

    # Waiting for the transaction receipt...

    tx_receipt = w3.eth.wait_for_transaction_receipt(send_tx)

    # Customer 1 has now cancelled the booking

    # assertions
    # checking whether the booking still exists
    booking_exists = contract_instance.functions.bookingExists(1).call()
    assert booking_exists == False

    # check barber's new balance - barber's balance should go up since they're getting some interest
    barber_new_dai_balance = dai_erc20_token.functions.balanceOf(barber_address).call()
    converted_barber_balance = w3.fromWei(barber_new_dai_balance, "ether")
    # sanity check
    assert barber_new_dai_balance > barber_dai_balance

    # check customer's new balance - balance should go up - since they're getting refunded
    customer_new_dai_balance = dai_erc20_token.functions.balanceOf(
        customer_1_address
    ).call()
    converted_customer_balance = w3.fromWei(customer_new_dai_balance, "ether")
    # sanity check
    assert customer_new_dai_balance > customer_dai_balance

    # check the contract's new balance on Aave - should have gone down
    new_a_dai_token_balance = a_dai_token.functions.balanceOf(contract_address).call()
    converted_balance = w3.fromWei(new_a_dai_token_balance, "ether")
    # sanity check
    assert new_a_dai_token_balance < a_dai_token_balance

    # end of test
