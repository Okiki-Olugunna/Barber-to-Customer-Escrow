// SPDX-License-Identifier: MIT

pragma solidity 0.8.12;

import "../interfaces/IERC20.sol";
import "../interfaces/ILendingPool.sol";

/**
 * @title Barber-to-Customer Escrow
 * @author Okiki Olugunna
 * @notice This contract facilitates the booking process for a
 * haircut between a customer and a barber, while making sure that
 * the barber executed the haircut to a good standard.
 * @dev This contract is intended for the polygon mumbai testnet.
 */
contract HairBookingEscrow {
    /**
     * @notice This is the contract address of the AAVE V2 lending pool on mumbai
     */
    ILendingPool public constant POOL =
        ILendingPool(0x9198F13B08E299d85E096929fA9781A1E3d5d827);

    /**
     * @notice This is the contract address of the Aave interest bearing aDAI token on mumbai
     * @dev This is where the extra interest to give the customer and barber comes from
     */
    //
    IERC20 public constant aDai =
        IERC20(0x639cB7b21ee2161DF9c882483C9D55c90c20Ca3e);

    /**
     * @notice This is the regular DAI stablecoin token on mumbai
     */
    IERC20 public constant DAI =
        IERC20(0x001B3B4d0F3714Ca98ba10F6042DaEbF0B1B7b6F);
        
    /**
     * @notice This is the MATIC token contract address on mumbai
     */
    IERC20 public constant MATIC =
        IERC20(0x0000000000000000000000000000000000001010);

    /// @notice This is the address of the barber
    address public barber;

    /// @notice This is the address of the arbiter
    address public arbiter;

    /**
     * @notice This is a price of a Fade in DAI.
     * Keeping it cheap for testnet purposes.
     * Would be 30 * (10**18) on mainnet
     */
    uint256 public FadePrice = 3;

    /**
     * @notice This is the price of a Level Cut in DAI.
     * Keeping it cheap for testnet purposes.
     * Would be 20 * (10**18) on mainnet
     */

    uint256 public LevelCutPrice = 2;

    /// @notice This is an array to store all of the booking IDs
    uint256[] bookingID;

    /// @notice This is an array to store the addresses of all previous customers
    address[] allPreviousCustomers;

    /// @notice This mapping stores whether a booking still exists & has not been cancelled
    mapping(uint256 => bool) public bookingExists;

    /// @notice This mapping stores how much was paid for a booking
    mapping(uint256 => uint256) public bookingIDToAmount;

    /// @notice This mapping stores the wallet address of a booking ID
    mapping(uint256 => address) public bookingIDToCustomer;

    /**
     * @notice This mapping stores the number of bookings a customer's address has made.
     * This is to be able to give a discount to certain customers after X amount of bookings
     */
    mapping(address => uint256) public customerToNumberOfBookings;

    /**
     * @notice This mapping store the customer's address and links it to the bookingID
     * and the appointment details of that booking ID
     */
    mapping(address => mapping(uint256 => Appointment)) public bookingDetails;

    /// @notice This struct stores the appointment details
    struct Appointment {
        string name;
        address customerAddress;
        uint256 hairCutType;
        uint256 amountPaid;
        uint256 bookingID;
        uint256 startTime;
        uint256 endTime;
    }

    /// @notice This enum holds the 2 different booking states
    enum BOOKING_STATE {
        CLOSED,
        OPEN
    }

    /// @notice This variable holds the current booking state
    BOOKING_STATE public bookingState;

    /**
     * @notice This event is triggered when bookings are opened
     * @param _timestamp The time that the bookings were opened
     */
    event bookingsOpened(uint256 _timestamp);

    /**
     * @notice This event gets triggered when bookings are closed
     * @param _timestamp The time that the bookings were closed
     */
    event bookingsClosed(uint256 _timestamp);

    /**
     * @notice This event gets triggered when a booking is made
     * @param bookingID The booking ID of the booking that was made
     * @param customer The address of the customer that made a booking
     * @param bookingAmount The amount of DAI that the customer paid
     * @param bookingNumber The number of bookings that this customer has made
     * @param timeOfAppointment The starting time of the scheduled appointment
     * @param endOfAppointment The ending time of the scheduled appointment
     */
    event bookingMade(
        uint256 bookingID,
        address indexed customer,
        uint256 bookingAmount,
        uint256 bookingNumber,
        uint256 timeOfAppointment,
        uint256 endOfAppointment
    );

    /**
     * @notice This event gets triggered when a customer cancels a booking
     * @param canceller The address that cancelled the booking
     * @param bookingID The booking ID that was cancelled
     */
    event bookingCancelled(address indexed canceller, uint256 bookingID);

    /**
     * @notice This event gets triggered when the barber gets paid the
     * deposit +  the interest, on completion of the haircut
     * @param _amount The amount paid to the barber
     */
    event paymentReceived(uint256 _amount);

    /**
     * @notice This event gets triggered when the customer gets paid their
     * interest, on completion of the haircut
     * @param _amount The amount paid to the customer
     */
    event paidInterestToCustomer(uint256 _amount);

    /**
     * @notice This event gets triggered when a customer tips the barber
     * @param amount The amount given in the tip
     * @param tipper The address of the tipper
     */
    event Tip(uint256 amount, address indexed tipper);

    /// @dev Only the barber can call functions marked by this modifier
    modifier onlyBarber() {
        require(msg.sender == barber, "You are not the barber.");
        _;
    }

    /**
     * @dev Functions marked by this modifier can only be called if
     * that booking ID exists
     */
    modifier thisBookingExists(uint256 _bookingID) {
        require(bookingExists[_bookingID], "This booking does not exist.");
        _;
    }

    /**
     * @dev constructor
     * @param _barber The address of the barber
     * @param _arbiter The address of the arbiter
     */
    constructor(address _barber, address _arbiter) {
        // initialising the barber and the arbiter
        barber = _barber;
        arbiter = _arbiter;

        // setting the booking state to be initially closed
        bookingState = BOOKING_STATE.CLOSED;
    }

    /**
     * @notice This function allows the barber to open up the bookings
     */
    function openUpBookings() external onlyBarber {
        // the booking state must first be closed
        require(bookingState == BOOKING_STATE.CLOSED, "Bookings already open.");

        // changing the booking state
        bookingState = BOOKING_STATE.OPEN;

        // emitting event that bookings are now open
        emit bookingsOpened(block.timestamp);
    }

    /**
     * @notice This function allows the barber to close booking availablity
     */
    function closeBookings() external onlyBarber {
        // the booking state must first be open
        require(bookingState == BOOKING_STATE.OPEN, "Bookings already closed.");

        // changing the booking state
        bookingState = BOOKING_STATE.CLOSED;

        // emitting event that bookings are now closed
        emit bookingsClosed(block.timestamp);
    }

    /**
     * @notice This function allows anyone to view the 2 haircut types available
     * @param _hairCutType The haircut type to view the price of
     */
    function viewHairCutPrices(uint256 _hairCutType)
        external
        pure
        returns (string memory _price)
    {
        if (_hairCutType == 1) return "Fade: 30 DAI"; // mainnet price
        if (_hairCutType == 2) return "Level Cut: 20 DAI"; // mainnet price
    }

    /**
     * @notice This function executes the booking of a haircut
     * @param _name The name of the person making the booking
     * @param _hairCutType The type of haircut the individual wants
     * @param _startTime The requested start time of the haircut
     * @param _endTime The requested end time of the haircut
     */
    function bookHairCut(
        string memory _name,
        uint256 _hairCutType,
        uint256 _startTime,
        uint256 _endTime
    ) external returns (uint256 newBooking) {
        // booking state must be open first
        require(
            bookingState == BOOKING_STATE.OPEN,
            "Bookings are currently closed."
        );

        // haircut type must be of type 1 or 2
        require(
            _hairCutType == 1 || _hairCutType == 2,
            "Invalid haircut type."
        );

        // initialising the new booking ID - this will be returned at the end of the function
        newBooking = bookingID.length + 1;

        // initialising the appointment
        Appointment memory appointment;

        // initialising the boking amount
        uint256 _bookingAmount;

        // initialising the customer's DAI balance
        uint256 customerDAIBalance = IERC20(DAI).balanceOf(msg.sender);

        // if haircut type = 1, then its a fade, transfer X amount of DAI
        if (_hairCutType == 1) {
            _bookingAmount = FadePrice;

            // the balance of the customer must be greater than or equal to the price of the haircut
            // putting this in place as "buy now, pay later" is starting to come into the scene in defi
            // do not people going into debt for a haircut
            require(
                customerDAIBalance >= _bookingAmount,
                "Your DAI balance is too low to pay for the haircut."
            );

            // transferring the haircut price amount of dai to this contract
            DAI.transferFrom(msg.sender, address(this), FadePrice);

            // depositing the dai into aave
            DAI.approve(address(POOL), FadePrice);
            POOL.deposit(address(DAI), FadePrice, address(this), 0);

            // tying this bookingID to the amount
            bookingIDToAmount[newBooking] = FadePrice;

            // adding initial appointment info
            appointment.amountPaid = FadePrice;
            appointment.hairCutType = 1;
        } else {
            // if haircut type = 2, then its a level cut, transfer X amount of DAI
            _bookingAmount = LevelCutPrice;

            // the balance of the customer must be greater than or equal to the price of the haircut
            // putting this in place as "buy now, pay later" is starting to come into the scene in defi
            // do not people going into debt for a haircut
            require(
                customerDAIBalance >= _bookingAmount,
                "Your DAI balance is too low to pay for the haircut."
            );

            // transferring the haircut price amount of dai to this contract
            DAI.transferFrom(msg.sender, address(this), LevelCutPrice);

            // depositing the dai into aave
            DAI.approve(address(POOL), LevelCutPrice);
            POOL.deposit(address(DAI), LevelCutPrice, address(this), 0);

            // tying this bookingID to the amount
            bookingIDToAmount[newBooking] = FadePrice;

            // adding initial appointment info
            appointment.amountPaid = LevelCutPrice;
            appointment.hairCutType = 2;
        }

        // adding 1 to the total number of bookings this customer has made
        customerToNumberOfBookings[msg.sender] += 1;

        // adding the booking ID to the booking ID array
        bookingID.push(newBooking);

        // adding the booking to the mapping of bookings that exist
        bookingExists[newBooking] = true;

        // tying this bookingID to the customer
        bookingIDToCustomer[newBooking] = msg.sender;

        // adding the extra appointment information
        appointment.name = _name;
        appointment.customerAddress = msg.sender;
        appointment.bookingID = newBooking;
        appointment.startTime = _startTime;
        appointment.endTime = _endTime;

        // tying the appintment details to the bookingID and address of customer
        bookingDetails[msg.sender][newBooking] = appointment;

        // emitting event that a booking has been made
        emit bookingMade(
            newBooking,
            msg.sender,
            _bookingAmount,
            customerToNumberOfBookings[msg.sender],
            _startTime,
            _endTime
        );

        // returns the bookingID back to the customer
        return newBooking;
    }

    /**
     * @notice This function allow the customer or barber to view the details of a specific booking
     *  by passing in the booking ID
     * @param _bookingID The booking ID to view the details of
     */
    function viewBookingDetails(uint256 _bookingID)
        external
        view
        returns (Appointment memory)
    {
        // only the customer who booked, or the barber, may call this function
        require(
            bookingIDToCustomer[_bookingID] == msg.sender ||
                msg.sender == barber,
            "You are not permitted to view the details of this booking."
        );

        // returns the Appointment struct
        return bookingDetails[msg.sender][_bookingID];
    }

    /**
     * @notice This function allows the arbiter to confirm that the haircut was
     * done to a good standard
     * @param _bookingID The booking ID of the appointment that has been completed
     */
    function completed(uint256 _bookingID)
        external
        thisBookingExists(_bookingID)
    {
        // only the arbiter can mark the haircut as complete
        require(msg.sender == arbiter, "You are not the arbiter.");

        // updating the booking ID as no longer existing
        bookingExists[_bookingID] = false;

        // initialising the customer's address so can pay them the interest
        address customer = bookingIDToCustomer[_bookingID];

        // calculating the amount of interest earned on aave
        uint256 totalBalance = aDai.balanceOf(address(this));

        // calculation: giving the barber the intital deposit and 50% of the extra interest
        uint256 amountForBarber = bookingIDToAmount[_bookingID] + // this line is the initial deposit
            (totalBalance / 2); // this line is 50% of the interest earned

        // calculation: giving the customer the other 50% of the extra interest
        uint256 interestForCustomer = totalBalance / 2;

        // withdrawing the initial deposit + the interest from aave
        POOL.withdraw(address(DAI), type(uint256).max, address(this));

        // tranferring interest to the customer
        DAI.transfer(customer, interestForCustomer);
        // emitting event that the interest has been paid to customer
        emit paidInterestToCustomer(interestForCustomer);

        // transferring the initial deposit + the remaining interest to the barber
        DAI.transfer(barber, amountForBarber);
        // emitting event that the payment + interest has been sent to the barber
        emit paymentReceived(amountForBarber);
    }

    /**
     * @notice This function allows the arbiter to confirm that the haircut was
     * done to a bad standard
     * @param _bookingID The booking ID of the appointment
     */
    function notUpToStandard(uint256 _bookingID)
        external
        thisBookingExists(_bookingID)
    {
        require(
            msg.sender == arbiter,
            "You are not permitted to call this function."
        );

        // updating the booking ID as no longer existing
        bookingExists[_bookingID] = false;

        // initialising the customer's address so can pay them
        address customer = bookingIDToCustomer[_bookingID];

        // calculating the amount of interest earned on aave
        uint256 totalBalance = aDai.balanceOf(address(this));

        // calculation to give the customer their money back + interest
        uint256 interestForCustomer = totalBalance;

        // withdrawing the initial deposit + the interest from aave
        POOL.withdraw(address(DAI), type(uint256).max, address(this));

        // tranferring interest to the customer
        DAI.transfer(customer, interestForCustomer);

        // emitting event that the interest has been paid to customer
        emit paidInterestToCustomer(interestForCustomer);
    }

    /**
     * @notice This function allows anyone to tip the barber with DAI at any time
     * @param _amount The amount to send as a tip
     */
    function tip(uint256 _amount) external {
        // transferring the tip to the barber's wallet address
        DAI.transfer(barber, _amount);

        // emitting event that someone has tipped the barber
        emit Tip(_amount, msg.sender);
    }

    /**
     * @notice This function executes the cancellation of a booking
     * @param _bookingID The booking ID to cancel
     */
    function cancelBooking(uint256 _bookingID)
        external
        thisBookingExists(_bookingID)
    {
        // only the customer who made the booking, or the barber, may cancel the booking
        require(
            bookingIDToCustomer[_bookingID] == msg.sender ||
                msg.sender == barber,
            "You are not permitted to cancel this booking."
        );

        // marking the booking as no longer existing
        bookingExists[_bookingID] = false;

        // calculating the amount of interest earned on aave
        uint256 totalBalance = aDai.balanceOf(address(this));

        // calculating how much to send the barber (interest earned)
        uint256 amountForBarber = totalBalance;

        // calculating the amount to send to the customer (only their initial deposit)
        uint256 amountForCustomer = bookingIDToAmount[_bookingID];

        // withdrawing the customer's deposit from aave
        POOL.withdraw(address(DAI), totalBalance, address(this));

        // initialising the customer's address
        address customer = bookingIDToCustomer[_bookingID];

        // transferring the customer's initial deposit back to them
        DAI.transfer(customer, amountForCustomer);

        // transferring the interest earned back to the barber
        DAI.transfer(barber, amountForBarber);

        // emitting event that the booking has been cancelled
        emit bookingCancelled(msg.sender, _bookingID);
    }

    /**
     * @notice This function allows the barber to change the price of a fade
     * @param _newPrice The new price of a Fade
     */
    function changeFadePrice(uint256 _newPrice) external onlyBarber {
        FadePrice = _newPrice;
    }

    /**
     * @notice This function allows the barber to change the price of a Level Cut
     * @param _newPrice The new price of a Level Cut
     */
    function changeLevelCutPrice(uint256 _newPrice) external onlyBarber {
        LevelCutPrice = _newPrice;
    }

    /**
     * @notice This function allows the barber to change the address they receive payments to
     * @param _newAddress The new wallet address of the barber's payments
     */
    function changeBarberAddress(address _newAddress) external onlyBarber {
        barber = _newAddress;
    }

    /**
     * @notice This function allows the barber or arbiter to change the address of the arbiter
     * @param _newAddress The new address of the arbiter
     */
    function changeArbiterAddress(address _newAddress) external {
        require(
            msg.sender == barber || arbiter == msg.sender,
            "You are not permitted to call this."
        );
        arbiter = _newAddress;
    }
}
