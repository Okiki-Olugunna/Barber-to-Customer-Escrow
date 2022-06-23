// SPDX-License-Identifier: MIT

pragma solidity 0.8.12;

import "../interfaces/IERC20.sol";
import "../interfaces/ILendingPool.sol";

contract HairBookingEscrow {
    // mainnet AAVE V2 lending pool
    ILendingPool public constant POOL =
        ILendingPool(0x7d2768dE32b0b80b7a3454c06BdAc94A69DDc7A9);
    // aave interest bearing aDAI
    IERC20 public constant aDai =
        IERC20(0x028171bCA77440897B824Ca71D1c56caC55b68A3);
    // DAI stablecoin
    IERC20 public constant DAI =
        IERC20(0x6B175474E89094C44Da98b954EedeAC495271d0F);

    address public barber;
    address public arbiter;

    uint256[] bookingID;
    address[] allPreviousCustomers;
    mapping(uint256 => bool) public bookingExists;
    mapping(uint256 => uint256) public bookingIDToAmount;
    mapping(uint256 => address) public bookingIDToCustomer;
    mapping(address => uint256) customerToNumberOfBookings; // can give a discount after X amount of bookings

    // mapping the customer's address to the bookingID to the appointment details
    mapping(address => mapping(uint256 => Appointment)) bookingDetails;

    struct Appointment {
        string name;
        address customerAddress;
        uint256 amountPaid;
        uint256 bookingID;
        uint256 startTime;
        uint256 endTime;
    }

    event bookingMade(
        uint256 bookingID,
        address indexed customer,
        uint256 bookingAmount,
        uint256 bookingNumber,
        uint256 timeOfAppointment,
        uint256 endOfAppointment
    );
    event bookingCancelled(address indexed canceller, uint256 bookingID);
    event paymentReceived(uint256);
    event paidInterestToCustomer(uint256);
    event Tip(uint256 amount, address indexed tipper);

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

        Appointment memory appointment;

        appointment.name = _name;
        appointment.amountPaid = _bookingAmount;
        appointment.customerAddress = msg.sender;
        appointment.bookingID = newBooking;
        appointment.startTime = _startTime;
        appointment.endTime = _endTime;

        bookingDetails[msg.sender][newBooking] = appointment;

        emit bookingMade(
            newBooking,
            msg.sender,
            _bookingAmount,
            customerToNumberOfBookings[msg.sender],
            _startTime,
            _endTime
        );

        return newBooking; // returns the bookingID
    }

    // view the details of your booking by passing in your booking ID
    function viewBookingDetails(uint256 _bookingID)
        external
        view
        returns (Appointment memory)
    {
        require(
            bookingIDToCustomer[_bookingID] == msg.sender ||
                msg.sender == barber,
            "You are not permitted to view the details of this booking."
        );

        return bookingDetails[msg.sender][_bookingID]; // returns the Appointment struct
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
        uint256 amountForBarber = totalBalance - bookingIDToAmount[_bookingID];
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

        emit bookingCancelled(msg.sender, _bookingID);
    }
}
