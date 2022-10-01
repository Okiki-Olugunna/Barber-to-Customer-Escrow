## Barber-to-Customer Escrow
A smart contract based booking platform for barbers

<b>*Website:*</b> https://barber-to-customer-escrow.okikicodes.repl.co/ 

#### How It Works:
- the customer makes a booking in advance 
- the payment is held in an escrow contract, e.g. 50 DAI, until the time of the haircut 
- during this time, the customer's funds are placed in Aave V2 to earn interest 

#### When the haircut is done:
- an arbiter approves that the haircut is complete to a good standard 
- the initially deposited funds are withdrawn from Aave 
- the customer gets some of the accrued interest 
- the barber gets their payment & some of the accrued interest as well (as an incentive to use this dapp) 

To see a simulation of this, view [this script](https://github.com/Okiki-Olugunna/Barber-to-Customer-Escrow/blob/main/scripts/03_booking_and_completion_simulation.py) 


##### The earlier the customer makes the booking, the more interest they can get


#### If a customer cancels the booking: 
- the barber gets the interest earned (another incentive to use this dapp) 
- the customer only gets back their deposit 

#### If a customer does not show up to a booking:
- the barber gets both the deposit for the haircut, plus the interest earned

#### Extra info:
- When a booking is made, an SMS message is sent to the barber using a combination of Twilio's SMS API and Alchemy Notify, which listens to on-chain activity at the booking platform's contract address
