// SPDX-License-Identifier: MIT

pragma solidity 0.8.12;

import "../../interfaces/IERC20.sol";
import "../../interfaces/ILendingPool.sol";

contract HairBookingEscrow {
    // mumbai AAVE V2 lending pool
    ILendingPool public constant POOL =
        ILendingPool(0x9198F13B08E299d85E096929fA9781A1E3d5d827);
    // aave interest bearing aDAI on mumbai
    IERC20 public constant aDai =
        IERC20(0x639cB7b21ee2161DF9c882483C9D55c90c20Ca3e);
    // DAI stablecoin on mumbai
    IERC20 public constant DAI =
        IERC20(0x001B3B4d0F3714Ca98ba10F6042DaEbF0B1B7b6F);

    // address of the barber
    address public barber;
    // address of the arbiter
    address public arbiter;

    // price of a fade
    uint256 public Fade = 30 * (10**18);
    // price of a level cut
    uint256 public LevelCut = 20 * (10**18);

    // array of all booking IDs
    uint256[] bookingID;
    // array of the addresses of all previous customers
    address[] allPreviousCustomers;

    // mapping to store whether a booking still exists & has not been cancelled
    mapping(uint256 => bool) public bookingExists;
    // mapping to store how much was paid for a booking
    mapping(uint256 => uint256) public bookingIDToAmount;
    // mapping to store the wallet address of a booking ID
    mapping(uint256 => address) public bookingIDToCustomer;
    // mapping to store the number of bookings this customer/address has made
    mapping(address => uint256) public customerToNumberOfBookings; // can give a discount after X amount of bookings

    // mapping the customer's address to the bookingID to the appointment details
    mapping(address => mapping(uint256 => Appointment)) bookingDetails;

    // storing the appointment details
    struct Appointment {
        string name;
        address customerAddress;
        uint256 amountPaid;
        uint256 bookingID;
        uint256 startTime;
        uint256 endTime;
    }

    // event for when a booking is made
    event bookingMade(
        uint256 bookingID,
        address indexed customer,
        uint256 bookingAmount,
        uint256 bookingNumber,
        uint256 timeOfAppointment,
        uint256 endOfAppointment
    );
    // event for when a customer cancels a booking
    event bookingCancelled(address indexed canceller, uint256 bookingID);
    // event for when the barber gets paid the deposit + interest - emitted on completion of the haircut
    event paymentReceived(uint256);
    // event for when the customer gets paid their interest - emitted on completion of the haircut
    event paidInterestToCustomer(uint256);
    // event for when a customer tips the barber
    event Tip(uint256 amount, address indexed tipper);

    // initialising the barber and the arbiter
    constructor(address _barber, address _arbiter) {
        barber = _barber;
        arbiter = _arbiter;
    }

    // function to view the 2 haircut types available - fade & level cut
    function viewHairCutPrices(uint256 _hairCutType)
        public
        pure
        returns (string memory _price)
    {
        if (_hairCutType == 1) return "Fade: 30 DAI";
        if (_hairCutType == 2) return "Level Cut: 20 DAI";
    }

    // function to book the haircut
    function bookHairCut(
        string memory _name,
        uint256 _bookingAmount,
        uint256 _startTime,
        uint256 _endTime
    ) external returns (uint256 newBooking) {
        //transferring the booking amount of dai to this contract
        DAI.transferFrom(msg.sender, address(this), _bookingAmount);

        // depositing the dai into aave
        DAI.approve(address(POOL), _bookingAmount);
        POOL.deposit(address(DAI), _bookingAmount, address(this), 0);

        // adding 1 to the total number of bookings this customer has made
        customerToNumberOfBookings[msg.sender] += 1;

        // initialising the booking ID
        newBooking = bookingID.length;

        // adding the booking ID to the booking ID array
        bookingID.push(newBooking);
        // adding the booking to the mapping of bookings that exist
        bookingExists[newBooking] = true;
        // tying this bookingID to the amount
        bookingIDToAmount[newBooking] = _bookingAmount;
        // tying this bookingID to the customer
        bookingIDToCustomer[newBooking] = msg.sender;

        // initialising the appointment
        Appointment memory appointment;

        appointment.name = _name;
        appointment.amountPaid = _bookingAmount;
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

    // function to view the details of your booking by passing in your booking ID
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

    // once the haircut is complete, the arbiter will confirm it with this function
    function completed(uint256 _bookingID) external {
        // only the arbiter can mark the haircut as complete
        require(msg.sender == arbiter, "You are not the arbiter.");

        // initialising the customer's address so can pay them interest
        address customer = bookingIDToCustomer[_bookingID];

        // calculating the amount of interest earned on aave
        uint256 totalBalance = aDai.balanceOf(address(this));

        // calculation: giving the barber the intital deposit and 50% of the extra interest
        uint256 amountForBarber = bookingIDToAmount[_bookingID] + // initial deposit
            (totalBalance / 2); // 50% of interest earned

        // calculation: giving the customer the other 50% of the extra interest
        uint256 interestForCustomer = totalBalance / 2;

        // withdrawing the initial deposit + the interest from aave
        POOL.withdraw(address(DAI), type(uint256).max, address(this));

        // tranferring interest to the customer
        payable(customer).transfer(interestForCustomer);
        emit paidInterestToCustomer(interestForCustomer);

        // transferring the initial deposit + the remaining interest to the barber
        payable(barber).transfer(amountForBarber);
        emit paymentReceived(amountForBarber);
    }

    // tip function for customers to use after the haircut, or if just feeling generous
    function tip() external payable {
        // transferring the tip to the barber's wallet address
        payable(barber).transfer(msg.value);
        // emitting event that someone has tipped the barber
        emit Tip(msg.value, msg.sender);
    }

    // function to cancel the booking
    function cancelBooking(uint256 _bookingID) public {
        // only the customer who made the booking, or the barber, may cancel the booking
        require(
            bookingIDToCustomer[_bookingID] == msg.sender ||
                msg.sender == barber,
            "You are not permitted to cancel this booking."
        );
        require(bookingExists[_bookingID], "Booking does not exist");

        // marking the booking as no longer existing
        bookingExists[_bookingID] = false;

        // calculating the amount of interest earned on aave
        uint256 totalBalance = aDai.balanceOf(address(this));

        // calculating how much to send the barber (interest earned)
        uint256 amountForBarber = totalBalance;
        // calculating the amount to send to the customer (only their initial deposit)
        uint256 amountForCustomer = bookingIDToAmount[_bookingID];

        //withdrawing the customer's deposit from aave
        POOL.withdraw(address(DAI), type(uint256).max, address(this));

        // initialising the customer's address
        address customer = bookingIDToCustomer[_bookingID];
        // transferring the customer's initial deposit back to them
        payable(customer).transfer(amountForCustomer);

        // transferring the interest earned back to the barber
        payable(barber).transfer(amountForBarber);

        // emitting event that the booking has been cancelled
        emit bookingCancelled(msg.sender, _bookingID);
    }
}
