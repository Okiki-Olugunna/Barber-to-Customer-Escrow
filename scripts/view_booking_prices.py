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


def main():
    # customer checks the haircut price of a fade
    print("Customer is checking the price of a fade...\n")
    haircut_price = contract_instance.functions.viewHairCutPrices(1).call()
    print(f"Haircut price of a fade is: {haircut_price}\n")

    # customer checks the haircut price of a level cut
    print("Customer is checking the price of a level cut...\n")
    haircut_price = contract_instance.functions.viewHairCutPrices(2).call()
    print(f"Haircut price of a level is: {haircut_price}\n")
