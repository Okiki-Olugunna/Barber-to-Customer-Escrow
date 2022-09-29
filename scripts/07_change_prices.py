from brownie import accounts, config
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
def main():
    am_i_connected = w3.isConnected()
    print(f"Web3 connection is connected: {am_i_connected} \n")

    print("\n--------------------------------------------- \n")
    print("STARTING THE CHANGE_PRICES.PY SCRIPT\n")
    print("---------------------------------------------\n")

    # initialising the accounts
    print("Initialising the accoounts...\n")
    barber = config["wallets"]["from_key"]["main"]
    barber_address = config["addresses"]["main_address"]

    print("Accounts initialised.\n")

    # getting the initial prices
    old_fade_price_in_wei = contract_instance.functions.FadePrice().call()
    old_fade_price = w3.fromWei(old_fade_price_in_wei, "ether")

    old_level_cut_price_in_wei = contract_instance.functions.LevelCutPrice().call()
    old_level_cut_price = w3.fromWei(old_level_cut_price_in_wei, "ether")

    # change the fade price
    change_fade_price = input("Would you like to change the price of a Fade? (Y/N) ")
    if change_fade_price == "Y" or change_fade_price == "y":
        new_fade_price = input(
            "What would you like the new price of a Fade to be in WMATIC? "
        )

        print(
            f"Changing the Fade price from {old_fade_price} WMATIC to {new_fade_price} WMATIC \n"
        )

        converted_fade_price = w3.toWei(Decimal(new_fade_price), "ether")
        # initiating transaction
        print("Getting the nonce...")
        nonce = w3.eth.get_transaction_count(barber_address)
        print("Building the transaction...")
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
        print("Signing the transaction...")
        signed_tx = w3.eth.account.sign_transaction(tx, barber)
        print("Sending the transaction...")
        send_tx = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        print("Waiting for the transaction receipt...")
        tx_receipt = w3.eth.wait_for_transaction_receipt(send_tx)
        print("\n--------------------------------------------")
        print(f"Transaction Receipt: \n{tx_receipt}")
        print("--------------------------------------------\n")

        updated_fade_price = contract_instance.functions.FadePrice().call()
        converted_updated_fade_price = w3.fromWei(updated_fade_price, "ether")

        print(
            f"\nThe price of a Fade has been successfully changed to {converted_updated_fade_price} WMATIC \n \n"
        )
        print("--------------------------------------------\n")

    # change the level cut price
    change_level_cut_price = input(
        "Would you like to change the price of a Level Cut? (Y/N) "
    )
    if change_level_cut_price == "Y" or change_level_cut_price == "y":
        new_level_cut_price = input(
            "What would you like the new price of a Level Cut to be in WMATIC? "
        )

        print(
            f"Changing the level cut price from {old_level_cut_price} WMATIC to {new_level_cut_price} WMATIC \n"
        )

        converted_level_cut_price = w3.toWei(Decimal(new_level_cut_price), "ether")
        # initiating transaction
        print("Getting the nonce...")
        nonce = w3.eth.get_transaction_count(barber_address)
        print("Building the transaction...")
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
        print("Signing the transaction...")
        signed_tx = w3.eth.account.sign_transaction(tx, barber)
        print("Sending the transaction...")
        send_tx = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        print("Waiting for the transaction receipt...")
        tx_receipt = w3.eth.wait_for_transaction_receipt(send_tx)
        print("\n--------------------------------------------")
        print(f"Transaction Receipt: \n{tx_receipt}")
        print("--------------------------------------------\n")

        updated_level_cut_price = contract_instance.functions.LevelCutPrice().call()
        converted_updated_level_cut_price = w3.fromWei(updated_level_cut_price, "ether")

        print(
            f"\nThe price of a Level Cut has been successfully changed to {converted_updated_level_cut_price} WMATIC \n \n"
        )
        print("--------------------------------------------\n")

    #
    print("\n---------------------------------------------\n")
    print("END OF SCRIPT\n")
    print("---------------------------------------------\n")
