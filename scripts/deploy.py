from brownie import HairBookingEscrow, config, accounts
import json


def main():
    barber = accounts.add(config["wallets"]["from_key"]["main"])
    barber_address = config["addresses"]["main_address"]

    arbiter = accounts.add(config["wallets"]["from_key"]["dev_2"])
    arbiter_address = config["addresses"]["dev_2_address"]

    print("\nDeploying the contract...\n")

    contract = HairBookingEscrow.deploy(
        barber_address, arbiter_address, {"from": barber}
    )

    print("Contract has been successfully deployed.\n")
    print(f"The contract address is {contract.address}\n")

    print("Updating the abi file in the frontend...")
    abi = contract.abi
    json_object = json.dumps(abi)

    with open("./contract_data/abi.json", "w") as file:
        file.write(json_object)
    with open("./frontend/utils/abi.json", "w") as file:
        file.write(json_object)

    print("Successfully updated the ABI.\n")

    print("Updating the contract address file in the frontend...")
    address = contract.address

    with open("./contract_data/address.txt", "w") as file:
        file.write(address)
    with open("./frontend/utils/address.txt", "w") as file:
        file.write(address)

    print("Successfully updated the contract address.\n")

    print("The deployed contract is ready to be interacted with. :) \n")
