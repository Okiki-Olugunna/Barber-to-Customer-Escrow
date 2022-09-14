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


# initialising erc20 token
with open("./contract_data/erc20_abi.json") as file_c:
    erc20_abi = file_c.read()

dai_erc20_token = w3.eth.contract(
    address="0x001B3B4d0F3714Ca98ba10F6042DaEbF0B1B7b6F", abi=erc20_abi
)


def test_can_tip_the_barber():
    # initialising the accounts
    barber = config["wallets"]["from_key"]["main"]
    barber_address = config["addresses"]["main_address"]

    customer_1 = config["wallets"]["from_key"]["dev_2"]
    customer_1_address = config["addresses"]["dev_2_address"]

    # check barber's balance
    barber_dai_balance = dai_erc20_token.functions.balanceOf(barber_address).call()
    initial_converted_barber_balance = w3.fromWei(barber_dai_balance, "ether")

    # check customer balance
    customer_dai_balance = dai_erc20_token.functions.balanceOf(
        customer_1_address
    ).call()
    initial_converted_customer_balance = w3.fromWei(customer_dai_balance, "ether")

    # customer makes a tip
    tip_amount = 10

    nonce = w3.eth.get_transaction_count(customer_1_address)
    tx = contract_instance.functions.tip(tip_amount).buildTransaction(
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

    # assertions
    # check the new balances
    # check barber's balance
    barber_dai_balance = dai_erc20_token.functions.balanceOf(barber_address).call()
    new_converted_barber_balance = w3.fromWei(barber_dai_balance, "ether")
    assert new_converted_barber_balance > initial_converted_barber_balance

    # check customer balance
    customer_dai_balance = dai_erc20_token.functions.balanceOf(
        customer_1_address
    ).call()
    new_converted_customer_balance = w3.fromWei(customer_dai_balance, "ether")
    assert new_converted_customer_balance < initial_converted_customer_balance

    # end of test
