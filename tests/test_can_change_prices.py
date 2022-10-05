from brownie import config
from web3 import Web3
from decimal import Decimal

# web3 connection
# w3 = Web3(Web3.WebsocketProvider(config["provider"]["websockets"]))
w3 = Web3(Web3.HTTPProvider(config["provider"]["http"]))

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


# main script
def test_can_Change_prices():

    # initialising the account
    barber = config["wallets"]["from_key"]["main"]
    barber_address = config["addresses"]["main_address"]

    # getting the initial prices
    old_fade_price_in_wei = contract_instance.functions.FadePrice().call()
    old_fade_price = w3.fromWei(old_fade_price_in_wei, "ether")

    old_level_cut_price_in_wei = contract_instance.functions.LevelCutPrice().call()
    old_level_cut_price = w3.fromWei(old_level_cut_price_in_wei, "ether")

    # change the fade price
    new_fade_price = old_fade_price_in_wei + 250

    converted_fade_price = w3.toWei(Decimal(new_fade_price), "ether")
    # initiating transaction
    nonce = w3.eth.get_transaction_count(barber_address)
    # Building the transaction..
    tx = contract_instance.functions.changeFadePrice(
        converted_fade_price
    ).buildTransaction(
        {
            "gasPrice": w3.eth.gas_price,
            "gas": 10_000_000,
            "chainId": 80001,
            "from": barber_address,
            "nonce": nonce,
        }
    )
    # Signing the transaction...
    signed_tx = w3.eth.account.sign_transaction(tx, barber)
    # Sending the transaction...
    send_tx = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    # Waiting for the transaction receipt...
    tx_receipt = w3.eth.wait_for_transaction_receipt(send_tx)

    tx_receipt

    updated_fade_price = contract_instance.functions.FadePrice().call()
    converted_updated_fade_price = w3.fromWei(updated_fade_price, "ether")

    # assertion
    assert converted_updated_fade_price != old_fade_price

    # change the level cut price
    new_level_cut_price = old_level_cut_price_in_wei + 500

    converted_level_cut_price = w3.toWei(Decimal(new_level_cut_price), "ether")
    # initiating transaction
    # Getting the nonce...
    nonce = w3.eth.get_transaction_count(barber_address)
    # Building the transaction...
    tx = contract_instance.functions.changeLevelCutPrice(
        converted_level_cut_price
    ).buildTransaction(
        {
            "gasPrice": w3.eth.gas_price,
            "gas": 10_000_000,
            "chainId": 80001,
            "from": barber_address,
            "nonce": nonce,
        }
    )
    # Signing the transaction...
    signed_tx = w3.eth.account.sign_transaction(tx, barber)
    # Sending the transaction...
    send_tx = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    # Waiting for the transaction receipt...
    tx_receipt = w3.eth.wait_for_transaction_receipt(send_tx)

    tx_receipt

    updated_level_cut_price = contract_instance.functions.LevelCutPrice().call()
    converted_updated_level_cut_price = w3.fromWei(updated_level_cut_price, "ether")

    # assertion
    assert converted_updated_level_cut_price != old_level_cut_price

    # end of test 
