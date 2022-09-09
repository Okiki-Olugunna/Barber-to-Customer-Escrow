## Barber-to-Customer Escrow
A smart contract based booking platform for hairdressers & barbers

#### How It Works:
- the customer makes a booking in advance 
- the payment is held in an escrow contract, e.g. 50 DAI, until the time of the haircut 
- during this time, the customer's funds are placed in Aave V2 to earn interest 

#### When the haircut is done:
- an arbiter approves that the haircut is complete to a good standard 
- the initially deposited funds are withdrawn from Aave 
- the customer gets some of the accrued interest 
- the barber gets their payment & some of the accrued interest as well (as an incentive to use this dapp) 


##### The earlier the customer makes the booking, the more interest they can get


#### If a customer cancels the booking: 
- the barber gets the interest earned (another incentive to use this dapp) 
- the customer only gets back their deposit 
