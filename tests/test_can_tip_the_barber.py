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

# initialising WMATIC erc20 token
with open("./contract_data/erc20_abi.json") as file_c:
    erc20_abi = file_c.read()

wmatic_erc20_token = w3.eth.contract(
    address="0x9c3C9283D3e44854697Cd22D3Faa240Cfb032889", abi=erc20_abi
)


def test_can_tip_barber():
    # initialising the accounts
    barber = config["wallets"]["from_key"]["main"]
    barber_address = config["addresses"]["main_address"]

    customer_1 = config["wallets"]["from_key"]["dev_2"]
    customer_1_address = config["addresses"]["dev_2_address"]

    # check barber's balance
    initial_barber_wmatic_balance = wmatic_erc20_token.functions.balanceOf(
        barber_address
    ).call()

    # check customer balance
    initial_customer_wmatic_balance = wmatic_erc20_token.functions.balanceOf(
        customer_1_address
    ).call()

    # customer makes a tip
    tip_amount = 10

    # Approving the contract to spend the customer's WMATIC...
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
    # Signing the transaction...
    signed_tx = w3.eth.account.sign_transaction(tx, customer_1)
    # Sending the transaction...
    send_tx = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    # Waiting for the transaction receipt...
    tx_receipt = w3.eth.wait_for_transaction_receipt(send_tx)

    tx_receipt

    # sending the tip
    # Getting the nonce..
    nonce = w3.eth.get_transaction_count(customer_1_address)
    # Building the transaction...
    tx = contract_instance.functions.tip(tip_amount).buildTransaction(
        {
            "gasPrice": w3.eth.gas_price,
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

    # check the new balances and assertions
    # check barber's balance
    barber_wmatic_balance = wmatic_erc20_token.functions.balanceOf(
        barber_address
    ).call()

    assert barber_wmatic_balance > initial_barber_wmatic_balance

    # check customer balance
    customer_wmatic_balance = wmatic_erc20_token.functions.balanceOf(
        customer_1_address
    ).call()

    assert customer_wmatic_balance < initial_customer_wmatic_balance

    # end of test
