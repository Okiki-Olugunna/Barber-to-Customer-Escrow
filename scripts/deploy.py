from brownie import accounts, HairBookingEscrow


def deploy():
    account = accounts[0]
    barber = accounts[1]
    arbiter = accounts[2]
    HairBookingEscrow.deploy(barber, arbiter, {"from": account})
    print("Contract was successfully deployed.")


def main():
    deploy()
