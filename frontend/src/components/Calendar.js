// Scheduling Component
import { useState, useEffect } from "react";
import { BigNumber, ethers } from "ethers";
import abi from "../utils/abi.json";
import erc20abi from "../utils/erc20_abi.json";
import Paper from "@mui/material/Paper";
import { Box, Button, Radio, Slider } from "@material-ui/core";
import SettingsSuggestIcon from "@mui/icons-material/SettingsSuggest";
import Dialog from "@mui/material/Dialog";
import CircularProgress from "@mui/material/CircularProgress";
import {
  ViewState,
  EditingState,
  IntegratedEditing,
} from "@devexpress/dx-react-scheduler";
import {
  Scheduler,
  WeekView,
  Appointments,
  AppointmentForm,
  Toolbar,
  DateNavigator,
  TodayButton,
} from "@devexpress/dx-react-scheduler-material-ui";

// dummy data
const schedulerData = [
  {
    startDate: "2022-10-01T09:45",
    endDate: "2022-10-01T11:00",
    title: "DeFi Integration",
  },
  {
    startDate: "2022-10-02T12:00",
    endDate: "2022-10-02T13:30",
    title: "Podcast appearance",
  },
  {
    startDate: "2022-10-03T09:45",
    endDate: "2022-10-03T11:00",
    title: "Meeting",
  },
  {
    startDate: "2022-10-04T12:00",
    endDate: "2022-10-04T13:30",
    title: "Go to the gym",
  },
];

// WMATIC ERC20 Token info
const wmaticContractAddress = "0x9c3C9283D3e44854697Cd22D3Faa240Cfb032889";
const wmaticABI = erc20abi.erc20abi;
const wmaticProvider = new ethers.providers.Web3Provider(window.ethereum);
const wmaticInstance = new ethers.Contract(
  wmaticContractAddress,
  wmaticABI,
  wmaticProvider.getSigner()
);

// hair booking smart contract info
const contractAddress = "0x5f93c7f83530F2ff9F6b99056B90Ea38ca258B45";
const contractABI = abi.abi;
const provider = new ethers.providers.Web3Provider(window.ethereum);

// contract instance
const contractInstance = new ethers.Contract(
  contractAddress,
  contractABI,
  provider.getSigner()
);

console.log("Hair Booking Contract Instance:", contractInstance);

const Calendar = (props) => {
  // state variables
  const [isBarber, setIsBarber] = useState(false);
  const [isArbiter, setIsArbiter] = useState(false);

  const [fadePrice, setFadePrice] = useState(0);
  const [levelCutPrice, setLevelCutPrice] = useState(0);

  const [selectedHaircutType, setSelectedHaircutType] = useState("");
  const [selectedFadeHaircut, setSelectedFadeHaircut] = useState(1);
  const [selectedLevelCut, setSelectedLevelCut] = useState(0);

  const [currentBookingState, setCurrentBookingState] = useState(false);
  const [appointments, setAppointments] = useState([]);
  const [tipAmount, setTipAmount] = useState("");

  const [currentBookingID, setCurrentBookingID] = useState("");
  const [cancelBookingID, setCancelBookingID] = useState("");
  const [goodHairCutID, setGoodHairCutID] = useState(0);
  const [badHairCutID, setBadHairCutID] = useState(0);
  const [noShowID, setNoShowID] = useState(0);

  // dialogs and progress indicators
  const [bookingHaircutShowDialog, setBookingHaircutShowDialog] =
    useState(false);
  const [cancelBookingShowDialog, setCancelBookingShowDialog] = useState(false);
  const [tipTheBarberShowDialog, setTipTheBarberShowDialog] = useState(false);
  const [openBookingsShowDialog, setOpenBookingsShowDialog] = useState(false);
  const [closeBookingsShowDialog, setCloseBookingsShowDialog] = useState(false);
  const [changeHaircutPriceShowDialog, setChangeHaircutPriceShowDialog] =
    useState(false);

  // making an apppointment
  const [showSign, setShowSign] = useState(false);
  const [mined, setMined] = useState(false);
  const [transactionHash, setTransactionHash] = useState("");

  // cancelling a booking
  const [showCancelBookingsSign, setShowCancelBookingsSign] = useState(false);
  const [cancelBookingsMined, setCancelBookingsMined] = useState(false);
  const [cancelBookingsTransactionHash, setCancelBookingsTransactionHash] =
    useState("");

  // tipping the barber
  const [showTipTheBarberSign, setShowTipTheBarberSign] = useState(false);
  const [tipTheBarberMined, setTipTheBarberMined] = useState(false);
  const [tipTheBarberTransactionHash, setTipTheBarberTransactionHash] =
    useState("");

  // opening the bookings
  const [showOpenBookingsSign, setShowOpenBookingsSign] = useState(false);
  const [openBookingsMined, setOpenBookingsMined] = useState(false);
  const [openBookingsTransactionHash, setOpenBookingsTransactionHash] =
    useState("");

  // closing the bookings
  const [showCloseBookingsSign, setShowCloseBookingsSign] = useState(false);
  const [closeBookingsMined, setCloseBookingsMined] = useState(false);
  const [closeBookingsTransactionHash, setCloseBookingsTransactionHash] =
    useState("");

  // changing the haircut price
  const [showChangeHaircutPriceSign, setShowChangeHaircutPriceSign] =
    useState(false);
  const [changeHaircutPriceMined, setChangeHaircutPriceMined] = useState(false);
  const [
    changeHaircutPriceTransactionHash,
    setChangeHaircutPriceTransactionHash,
  ] = useState("");

  // good haircut
  const [goodHairCutShowDialoag, setGoodHairCutShowDialog] = useState(false);
  const [showGoodHairCutSign, setShowGoodHairCutSign] = useState(false);
  const [goodHairCutMined, setGoodHairCutMined] = useState(false);
  const [goodHairCutTransactionHash, setGoodHairCutTransactionHash] =
    useState("");

  // bad haircut
  const [badHairCutShowDialog, setBadHairCutShowDialog] = useState(false);
  const [showBadHairCutSign, setShowBadHairCutSign] = useState(false);
  const [badHairCutMined, setBadHairCutMined] = useState(false);
  const [badHairCutTransactionHash, setBadHairCutTransactionHash] =
    useState("");

  // customer did not show up
  const [noShowShowDialog, setNoShowShowDialog] = useState(false);
  const [showNoShowShowSign, setNoShowShowSign] = useState(false);
  const [noShowMined, setNoShowMined] = useState(false);
  const [noShowTransactionHash, setNoShowTransactionHash] = useState("");

  // event handlers
  // when selecting a haircut type
  const onChangeHaircutFade = (event) => {
    console.log("\nRadio button changed to:", event.target.value);
    console.log("Changing the state to fade...");

    setSelectedFadeHaircut(1);
    setSelectedLevelCut(0);

    console.log(`Selected fade type: ${selectedFadeHaircut}`);
    console.log(`Selected level cut? : ${selectedLevelCut}`);
  };

  const onChangeHaircutLevelCut = (event2) => {
    console.log("\nRadio button changed to:", event2.target.value);
    console.log("Changing the state to level cut...");

    setSelectedLevelCut(1);
    setSelectedFadeHaircut(0);

    console.log(`Selected level cut type: ${selectedLevelCut}`);
    console.log(`Selected fade? : ${selectedFadeHaircut}`);
  };

  // for when slider of fade price is changed
  const handleFadeSliderChange = (event, newValue) => {
    setFadePrice(newValue);
    console.log("Fade slider changed to", newValue);
  };
  // for when slider of level cut price is changed
  const handleLevelCutSliderChange = (event, newValue) => {
    setLevelCutPrice(newValue);
    console.log("Level cut slider changed to", newValue);
  };
  // handling the input box for cancelling a booking
  const onCancelBookingIDChange = (event, value) => {
    setCancelBookingID(event.target.value);
  };
  // handling the input for the tips
  const onTipAmountChange = (event, value) => {
    setTipAmount(event.target.value);
  };
  // handling the input box for a good haircut
  const onGoodHairCutIDChange = (event, value) => {
    setGoodHairCutID(event.target.value);
  };
  // handling the input box for a bad haircut
  const onBadHairCutIDChange = (event, value) => {
    setBadHairCutID(event.target.value);
  };
  // handling the input box for a no show
  const onNoShowIDChange = (event, value) => {
    setNoShowID(event.target.value);
  };

  // load this data on page refresh
  const getData = async () => {
    // getting the barber's address from the contract
    const barber = await contractInstance.barber();
    console.log("Barber address: ", barber);
    console.log("Current account connected: ", props.account);

    // if the barber is connected
    setIsBarber(barber.toUpperCase() === props.account.toUpperCase());
    console.log(
      "Is the barber connected: ",
      barber.toUpperCase() === props.account.toUpperCase()
    );

    // getting the arbiter's address
    const arbiter = await contractInstance.arbiter();
    console.log("Arbiter address: ", barber);
    // if the arbiter is connected
    setIsArbiter(arbiter.toUpperCase() === props.account.toUpperCase());
    console.log(
      "Is the arbiter connected: ",
      arbiter.toUpperCase() === props.account.toUpperCase()
    );

    // the current booking state
    const bookingState = await contractInstance.bookingState();
    console.log("The current booking state: ", bookingState);
    if (bookingState == 1) {
      setCurrentBookingState(true);
    } else {
      setCurrentBookingState(false);
    }
    console.log("The current booking state: ", currentBookingState);

    // fade price
    const fade = await contractInstance.FadePrice();
    const fadeConverted = ethers.utils.formatEther(fade);
    console.log(`Fede Price: ${fadeConverted} WMATIC`);
    // level cut price
    const levelCut = await contractInstance.LevelCutPrice();
    const levelCutConverted = ethers.utils.formatEther(levelCut);
    console.log(`Level Cut Price: ${levelCutConverted} WMATIC`);

    // setting the sliders for the barber tools
    setFadePrice(ethers.utils.formatEther(fade.toString()));
    setLevelCutPrice(ethers.utils.formatEther(levelCut.toString()));

    // console.log("Current selected appointment type:", selectedHaircutType);

    // the array of appointments in the contract to display on screen
    const appointmentData = await contractInstance.getAppointments();
    console.log("Appointment Data:", appointmentData);

    transformAppointmentData(appointmentData);
  };

  // the appointments to display on the calendar on screen
  const transformAppointmentData = (appointmentData) => {
    let data = [];
    appointmentData.forEach((appointment) => {
      data.push({
        title: appointment.title,
        startDate: new Date(appointment.startTime * 1000), // unix time in milliseconds
        endDate: new Date(appointment.endTime * 1000), // unix time in milliseconds
      });
    });

    setAppointments(data);
  };

  // calling the getdata function on page load
  useEffect(() => {
    getData();
  }, []);

  // this function is called by the calendar
  const sendAppointment = (data) => {
    console.log("\nSending the appointment info...");
    if (selectedFadeHaircut == 1) {
      console.log("Passing the info to the fade function...");
      saveFadeAppointment(data);
    } else {
      console.log("Passing the info to the level cut function...");
      saveLevelCutAppointment(data);
    }
  };

  // function to save and book a fade appointment
  const saveFadeAppointment = async (data) => {
    console.log("\nThis is the fade function...\n");
    console.log("Caching appointment data...");
    console.log("Appointment data: ", data);

    const appointment = data.added;
    const title = appointment.title;
    const startTime = appointment.startDate.getTime() / 1000; // converted to unix milliseconds
    const endTime = appointment.endDate.getTime() / 1000; // converted to unix

    setShowSign(true);
    setBookingHaircutShowDialog(true);
    setMined(false);

    try {
      // customer must first approve the contract to spend the amount
      console.log("Approving the contract to spend the customer's funds...");
      const fade = await contractInstance.FadePrice();
      const approveTx = await wmaticInstance.approve(contractAddress, fade);
      console.log("Waiting for the transaction to go through...");
      await approveTx.wait();
      console.log("Transaction mined.");

      // making the booking
      console.log("Booking the haircut (fade)...");
      const tx = await contractInstance.bookAFade(
        title, // name of customer
        startTime, // start time of haircut
        endTime, // end time of haircut
        { gasLimit: 10000000 }
      );

      setShowSign(false);
      console.log("Waiting for the transaction to go through...");

      await tx.wait();
      setMined(true);
      console.log("Transaction mined.");

      // transaction hash
      setTransactionHash(tx.hash);

      // get the booking ID
      console.log("Getting the booking ID...\n");
      const bookingidTX = await contractInstance.currentBookingID();
      // await bookingidTX.wait();
      console.log(`Booking ID is: ${bookingidTX}`);
      const convertedBookingID = bookingidTX.toString();
      setCurrentBookingID(convertedBookingID);

      //
    } catch (error) {
      console.log(error);
      setBookingHaircutShowDialog(false);
    }
  };

  // function to save and book a level cut appointment
  const saveLevelCutAppointment = async (data) => {
    console.log("This is the level cut function...\n");
    console.log("Caching appointment data...");
    console.log("Appointment data: ", data);

    const appointment = data.added;
    const title = appointment.title;
    const startTime = appointment.startDate.getTime() / 1000; // converted to unix milliseconds
    const endTime = appointment.endDate.getTime() / 1000; // converted to unix

    setShowSign(true);
    setBookingHaircutShowDialog(true);
    setMined(false);

    try {
      // customer must first approve the contract to spend the amount
      console.log("Approving the contract to spend the customer's funds...");
      const levelCut = await contractInstance.LevelCutPrice();
      const approveTx = await wmaticInstance.approve(contractAddress, levelCut);
      console.log("Waiting for the transaction to go through...");
      await approveTx.wait();
      console.log("Transaction mined.");

      // making the booking
      console.log("Booking the haircut (level cut)...");
      const tx = await contractInstance.bookALevelCut(
        title, // name of customer
        startTime, // start time of haircut
        endTime, // end time of haircut
        { gasLimit: 10000000 }
      );

      setShowSign(false);
      console.log("Waiting for the transaction to go through...");

      await tx.wait();
      setMined(true);
      console.log("Transaction mined.");

      // transaction hash
      setTransactionHash(tx.hash);

      // get the booking ID
      const bookingidTX = await contractInstance.currentBookingID();
      console.log(`Booking ID is: ${bookingidTX.toString()}`);
      const convertedBookingID = bookingidTX.toString();
      setCurrentBookingID(convertedBookingID);

      //
    } catch (error) {
      console.log(error);
      setBookingHaircutShowDialog(false);
    }
  };

  // function to cancel a booking
  const cancelBooking = async () => {
    // getting the booking ID from the input
    console.log("Caching the booking ID...");
    const bookingID = cancelBookingID;

    setShowCancelBookingsSign(true);
    setCancelBookingShowDialog(true);
    setCancelBookingsMined(false);

    console.log(`Cancelling the booking with the ID of ${bookingID}...`);
    const cancelTx = await contractInstance.cancelBooking(bookingID);

    setShowCancelBookingsSign(false);
    console.log("Waiting for the transaction to go through...");

    await cancelTx.wait();
    console.log("Transaction mined.");

    setCancelBookingsMined(true);
    setCancelBookingsTransactionHash(cancelTx.hash);

    console.log("The booking has been successfully cancelled.");
  };

  // function to tip the barber
  const tipTheBarber = async () => {
    // getting the tip amount
    const amount = tipAmount;
    // converting the tip amount
    const convertedAmount = ethers.utils.parseUnits(amount, "ether");
    console.log(`You are tipping the barber ${amount} WMATIC`);
    console.log(
      `Caching the tip amount of ${convertedAmount} WMATIC in wei units`
    );

    setShowTipTheBarberSign(true);
    setTipTheBarberShowDialog(true);
    setTipTheBarberMined(false);

    console.log("Approving the contract to spend your WMATIC...");
    const approveTx = await wmaticInstance.approve(
      contractAddress,
      convertedAmount
    );

    console.log("Waiting for the transaction to go through...");
    await approveTx.wait();
    console.log("The contract has been approved to spend the WMATIC.\n");

    console.log("Calling the contract to send the tip...");
    const tipTx = await contractInstance.tip(convertedAmount);

    setShowTipTheBarberSign(false);
    console.log("Waiting for the transaction to go through...");
    await tipTx.wait();

    console.log("Transaction mined.");
    setTipTheBarberMined(true);
    setTipTheBarberTransactionHash(tipTx.hash);

    console.log("The tip has been sent to the barber. Thank you :)");

    // clear form field
    setTipAmount("");
  };

  // function to join the referral program
  //
  //

  // BARBER TOOLS
  // function to open the bookings
  const openTheBookings = async () => {
    console.log("Opening the bookings...");

    setShowOpenBookingsSign(true);
    setOpenBookingsShowDialog(true);
    setOpenBookingsMined(false);

    const tx = await contractInstance.openUpBookings();

    setShowOpenBookingsSign(false);
    console.log("Waiting for the transaction to go through...");

    await tx.wait();
    console.log("Bookings have been opened successfully.");

    const bookingStateTx = await contractInstance.bookingState();
    // await bookingStateTx.wait();
    console.log(
      `The current booking state of the contract is: ${bookingStateTx}`
    );
    setCurrentBookingState(true);

    setOpenBookingsMined(true);
    setOpenBookingsTransactionHash(tx.hash);
  };

  // function to close the bookings
  const closeTheBookings = async () => {
    console.log("Closing the bookings...");

    setShowCloseBookingsSign(true);
    setCloseBookingsShowDialog(true);
    setCloseBookingsMined(false);

    const tx = await contractInstance.closeBookings();
    setShowCloseBookingsSign(false);
    console.log("Waiting for the transaction to go through...");

    await tx.wait();
    console.log("Bookings have been closed successfully.");

    const bookingStateTx = await contractInstance.bookingState();
    // await bookingStateTx.wait();
    console.log(
      `The current booking state of the contract is: ${bookingStateTx}`
    );
    setCurrentBookingState(false);

    setCloseBookingsMined(true);
    setCloseBookingsTransactionHash(tx.hash);
  };

  // function to save and change the price of a Fade
  const saveFadePrice = async () => {
    const newPrice = ethers.utils.parseEther(fadePrice.toString());

    setShowChangeHaircutPriceSign(true);
    setChangeHaircutPriceShowDialog(true);
    setChangeHaircutPriceMined(false);

    // converting the hexnumber into a readable number
    const convertedFromHex = BigNumber.from(newPrice);
    const convertedFromWei = ethers.utils.formatEther(convertedFromHex);

    console.log("Saving new fade price of", convertedFromWei, "WMATIC...");

    const tx = await contractInstance.changeFadePrice(newPrice);
    setShowChangeHaircutPriceSign(false);

    console.log("Waiting for the transaction to go through...");

    await tx.wait();
    console.log("Transaction mined. \nFade Price successfully changed.");

    // get the new fade price
    const fade = await contractInstance.FadePrice();
    const fadeFromWei = ethers.utils.formatEther(fade);
    console.log(`New fade price is: ${fadeFromWei} WMATIC`);

    setChangeHaircutPriceMined(true);
    setChangeHaircutPriceTransactionHash(tx.hash);
  };

  // function to save and change the new price of a level cut
  const saveLevelCutPrice = async () => {
    const newPrice = ethers.utils.parseEther(levelCutPrice.toString());

    setShowChangeHaircutPriceSign(true);
    setChangeHaircutPriceShowDialog(true);
    setChangeHaircutPriceMined(false);

    // converting the hexnumber into a readable number
    const convertedFromHex = BigNumber.from(newPrice);
    const convertedFromWei = ethers.utils.formatEther(convertedFromHex);

    console.log("Saving new level cut price of", convertedFromWei, "WMATIC...");

    const tx = await contractInstance.changeLevelCutPrice(newPrice);
    setShowChangeHaircutPriceSign(false);

    console.log("Waiting for the transaction to go through...");

    await tx.wait();
    console.log("Transaction mined. Level Price successfully changed.");

    // get the new level cut price
    const levelCut = await contractInstance.LevelCutPrice();
    const levelCutFromWei = ethers.utils.formatEther(levelCut);
    console.log(`New level cut price is: ${levelCutFromWei} WMATIC`);

    setChangeHaircutPriceMined(true);
    setChangeHaircutPriceTransactionHash(tx.hash);
  };

  // marks for the slider
  const marks = [
    { value: 0.0, label: "0" },
    { value: 0.2, label: "Cheap" },
    { value: 0.4, label: "Standard Range" },
    { value: 0.6, label: "Standard Range" },
    { value: 0.8, label: "Premium" },
    { value: 1, label: "1" },
  ];

  // Barber tools
  const Barber = () => {
    return (
      <div id="barber">
        {/* <h3>Barber Tools</h3> */}

        <Box id="open-the-bookings" onClick={openTheBookings}>
          <h3>Open the Bookings</h3>
        </Box>

        <Box id="close-the-bookings" onClick={closeTheBookings}>
          <h3>Close the Bookings</h3>
        </Box>

        <Box id="fade-price">
          <h3> Set Fade Price </h3>
          <Slider
            defaultValue={parseFloat(fadePrice)}
            step={0.1}
            marks={marks}
            min={0}
            max={1}
            valueLabelDisplay="auto"
            onChangeCommitted={handleFadeSliderChange}
          ></Slider>
          <Button
            id="settings-button"
            onClick={saveFadePrice}
            variant="contained"
          >
            <SettingsSuggestIcon></SettingsSuggestIcon>
            Save Changes
          </Button>
        </Box>

        <Box id="level-cut-price">
          <h3> Set Level Cut Price </h3>
          <Slider
            defaultValue={parseFloat(levelCutPrice)}
            step={0.1}
            marks={marks}
            min={0}
            max={1}
            valueLabelDisplay="auto"
            onChangeCommitted={handleLevelCutSliderChange}
          ></Slider>
          <Button
            id="settings-button"
            onClick={saveLevelCutPrice}
            variant="contained"
          >
            <SettingsSuggestIcon></SettingsSuggestIcon>
            Save Changes
          </Button>
        </Box>
      </div>
    );
  };

  // arbiter tools
  const goodHairCut = async () => {
    // getting the booking ID
    const bookingID = goodHairCutID;
    console.log(
      `The haircut of ID: ${bookingID} was done to a good standard. \nCalling the complete function...`
    );

    setShowGoodHairCutSign(true);
    setGoodHairCutShowDialog(true);
    setGoodHairCutMined(false);

    try {
      // calling the contract
      const tx = await contractInstance.completed(bookingID);
      setShowGoodHairCutSign(false);

      console.log("Waiting for the transaction to go through...");

      await tx.wait();
      console.log("Transaction mined.");

      setGoodHairCutMined(true);
      setGoodHairCutTransactionHash(tx.hash);

      console.log(
        "Haircut is complete. Barber has received his payment, and the customer has received their interest."
      );
    } catch (error) {
      console.log("This booking does not exist.");
    }

    // clear the form fields
    setGoodHairCutID("");
  };

  const badHairCut = async () => {
    // getting the booking ID
    const bookingID = badHairCutID;
    console.log(
      `The haircut of ID : ${bookingID} was done to a bad standard. \nCalling the notUpToStandard function...`
    );

    setShowBadHairCutSign(true);
    setBadHairCutShowDialog(true);
    setBadHairCutMined(false);

    try {
      // calling the contract
      const tx = await contractInstance.notUpToStandard(bookingID);
      setShowBadHairCutSign(false);

      console.log("Waiting for the transaction to go through...");

      await tx.wait();
      console.log("Transaction mined.");

      setBadHairCutMined(true);
      setBadHairCutTransactionHash(tx.hash);

      console.log("\nCustomer has been refunded with interest.");
    } catch (error) {
      console.log("This booking does not exist.");
    }

    // clear the form fields
    setBadHairCutID("");
  };

  const noShow = async () => {
    // getting the booking ID
    const bookingID = noShowID;
    console.log(
      `The customer with the booking ID of : ${bookingID} did not turn up. \nCalling the noShow() function...`
    );

    setNoShowShowSign(true);
    setNoShowShowDialog(true);
    setNoShowMined(false);

    try {
      // calling the contract
      const tx = await contractInstance.noShow(bookingID);
      setNoShowShowSign(true);

      console.log("Waiting for the transaction to go through...");

      await tx.wait();
      console.log("Transaction mined.");

      setNoShowMined(false);
      setNoShowTransactionHash(tx.hash);

      console.log(
        "\nThe barber has been refunded for having their time wasted."
      );
    } catch (error) {
      console.log("This booking does not exist.");
    }

    // clear the form fields
    setBadHairCutID("");
  };

  // loading popup when booking a haircut
  const BookHaircutConfirmDialog = () => {
    return (
      <Dialog id="confirm-dialog" open={true}>
        <div style={{ textAlign: "right", padding: "0px 0px 0px 0px" }}>
          {mined && (
            <Button
              onClick={() => {
                setBookingHaircutShowDialog(false);
                getData();
              }}
            >
              CLOSE
            </Button>
          )}
        </div>

        <h3 id="confirm-dialog-header">
          {mined && "Appointment Confirmed!"}
          {!mined && !showSign && "Conforming Your Appointment"}
          {!mined && showSign && "Please Sign to Confirm"}
        </h3>

        <div style={{ textAlign: "left", padding: "0px 20px 20px 20px" }}>
          {!mined && !showSign && (
            <div>
              <p>Please wait while your appointment is being confirmed...</p>
            </div>
          )}
          {!mined && showSign && (
            <div>
              <p>
                Please sign the following 2 transactions from your wallet to
                confirm the appointment...
              </p>
            </div>
          )}

          {mined && (
            <div>
              Your appointment has been confirmed and your booking ID is:{" "}
              {currentBookingID}.<br></br>
              <p>
                Please make a note of this, as we will request this ID when you
                arrive.
              </p>
              <p>
                <a
                  target="_blank"
                  href={`https://mumbai.polygonscan.com/tx/${transactionHash}`}
                >
                  View transaction on Mumbai Polygonscan
                </a>
              </p>
            </div>
          )}
        </div>

        <div style={{ textAlign: "center", paddingBottom: "30px" }}>
          {!mined && <CircularProgress />}
        </div>
      </Dialog>
    );
  };

  // popup for when changing the haircut price
  const ChangeHaircutPriceDialog = () => {
    return (
      <Dialog id="confirm-dialog" open={true}>
        <div style={{ textAlign: "right", padding: "0px 0px 0px 0px" }}>
          {changeHaircutPriceMined && (
            <Button
              onClick={() => {
                setChangeHaircutPriceShowDialog(false);
                getData();
              }}
            >
              CLOSE
            </Button>
          )}
        </div>

        <h3 id="confirm-dialog-header">
          {changeHaircutPriceMined && "Price Changed!"}
          {!changeHaircutPriceMined &&
            !showChangeHaircutPriceSign &&
            "Conforming The Change Of Price"}
          {!changeHaircutPriceMined &&
            showChangeHaircutPriceSign &&
            "Please Sign to Confirm"}
        </h3>

        <div style={{ textAlign: "left", padding: "0px 20px 20px 20px" }}>
          {!changeHaircutPriceMined && !showChangeHaircutPriceSign && (
            <div>
              <p>Please wait while we are changing your prices...</p>
            </div>
          )}
          {!changeHaircutPriceMined && showChangeHaircutPriceSign && (
            <div>
              <p>
                Please sign the transaction from your wallet to confirm the
                change in price...
              </p>
            </div>
          )}

          {changeHaircutPriceMined && (
            <div>
              Your change in price has been confirmed!<br></br>
              <p>
                <a
                  target="_blank"
                  href={`https://mumbai.polygonscan.com/tx/${changeHaircutPriceTransactionHash}`}
                >
                  View transaction on Mumbai Polygonscan
                </a>
              </p>
            </div>
          )}
        </div>

        <div style={{ textAlign: "center", paddingBottom: "30px" }}>
          {!changeHaircutPriceMined && <CircularProgress />}
        </div>
      </Dialog>
    );
  };

  // popup for when someone cancels a booking
  const CancelBookingDialog = () => {
    return (
      <Dialog id="confirm-dialog" open={true}>
        <div style={{ textAlign: "right", padding: "0px 0px 0px 0px" }}>
          {cancelBookingsMined && (
            <Button
              onClick={() => {
                setCancelBookingShowDialog(false);
                getData();
              }}
            >
              CLOSE
            </Button>
          )}
        </div>

        <h3 id="confirm-dialog-header">
          {cancelBookingsMined && "Appointment Cancelled!"}
          {!cancelBookingsMined &&
            !showCancelBookingsSign &&
            "Conforming Your Cancellation"}
          {!cancelBookingsMined &&
            showCancelBookingsSign &&
            "Please Sign to Confirm"}
        </h3>

        <div style={{ textAlign: "left", padding: "0px 20px 20px 20px" }}>
          {!cancelBookingsMined && !showCancelBookingsSign && (
            <div>
              <p>Please wait while your appointment is being cancelled...</p>
            </div>
          )}
          {!cancelBookingsMined && showCancelBookingsSign && (
            <div>
              <p>
                Please sign the transaction from your wallet to confirm the
                cancellation...
              </p>
            </div>
          )}

          {cancelBookingsMined && (
            <div>
              Your appointment has been successfully cancelled.<br></br>
              <p>
                <a
                  target="_blank"
                  href={`https://mumbai.polygonscan.com/tx/${cancelBookingsTransactionHash}`}
                >
                  View transaction on Mumbai Polygonscan
                </a>
              </p>
            </div>
          )}
        </div>

        <div style={{ textAlign: "center", paddingBottom: "30px" }}>
          {!cancelBookingsMined && <CircularProgress />}
        </div>
      </Dialog>
    );
  };

  // popup for when someone tips the barber
  const TipTheBarberDialog = () => {
    return (
      <Dialog id="confirm-dialog" open={true}>
        <div style={{ textAlign: "right", padding: "0px 0px 0px 0px" }}>
          {tipTheBarberMined && (
            <Button
              onClick={() => {
                setTipTheBarberShowDialog(false);
                getData();
              }}
            >
              CLOSE
            </Button>
          )}
        </div>

        <h3 id="confirm-dialog-header">
          {tipTheBarberMined && "Tip Sent!"}
          {!tipTheBarberMined && !showTipTheBarberSign && "Sending Your Tip"}
          {!tipTheBarberMined &&
            showTipTheBarberSign &&
            "Please Sign to Confirm"}
        </h3>

        <div style={{ textAlign: "left", padding: "0px 20px 20px 20px" }}>
          {!tipTheBarberMined && !showTipTheBarberSign && (
            <div>
              <p>Please wait while your tip is being sent...</p>
            </div>
          )}
          {!tipTheBarberMined && showTipTheBarberSign && (
            <div>
              <p>
                Please sign the transaction from your wallet to confirm your
                tip...
              </p>
            </div>
          )}

          {tipTheBarberMined && (
            <div>
              Your tip has been sent!<br></br>
              Thank you! {" :) "}
              <p>
                <a
                  target="_blank"
                  href={`https://mumbai.polygonscan.com/tx/${tipTheBarberTransactionHash}`}
                >
                  View transaction on Mumbai Polygonscan
                </a>
              </p>
            </div>
          )}
        </div>

        <div style={{ textAlign: "center", paddingBottom: "30px" }}>
          {!tipTheBarberMined && <CircularProgress />}
        </div>
      </Dialog>
    );
  };

  // popup for when the barber is opening the bookings
  const OpenTheBookingsDialog = () => {
    return (
      <Dialog id="confirm-dialog" open={true}>
        <div style={{ textAlign: "right", padding: "0px 0px 0px 0px" }}>
          {openBookingsMined && (
            <Button
              onClick={() => {
                setOpenBookingsShowDialog(false);
                getData();
              }}
            >
              CLOSE
            </Button>
          )}
        </div>

        <h3 id="confirm-dialog-header">
          {openBookingsMined && "Bookings Opened!"}
          {!openBookingsMined &&
            !showOpenBookingsSign &&
            "Opening The Bookings"}
          {!openBookingsMined &&
            showOpenBookingsSign &&
            "Please Sign To Confirm"}
        </h3>

        <div style={{ textAlign: "left", padding: "0px 20px 20px 20px" }}>
          {!openBookingsMined && !showOpenBookingsSign && (
            <div>
              <p>Please wait while we are opening the bookings...</p>
            </div>
          )}
          {!openBookingsMined && showOpenBookingsSign && (
            <div>
              <p>
                Please sign the transaction from your wallet to confirm that you
                want to open the bookings...
              </p>
            </div>
          )}

          {openBookingsMined && (
            <div>
              Bookings have now been opened!<br></br>
              <p>Your clients and customers can now make a booking with you.</p>
              <p>
                <a
                  target="_blank"
                  href={`https://mumbai.polygonscan.com/tx/${openBookingsTransactionHash}`}
                >
                  View transaction on Mumbai Polygonscan
                </a>
              </p>
            </div>
          )}
        </div>

        <div style={{ textAlign: "center", paddingBottom: "30px" }}>
          {!openBookingsMined && <CircularProgress />}
        </div>
      </Dialog>
    );
  };

  // popup for when the barber is closing the bookings
  const CloseTheBookingsDialog = () => {
    return (
      <Dialog id="confirm-dialog" open={true}>
        <div style={{ textAlign: "right", padding: "0px 0px 0px 0px" }}>
          {closeBookingsMined && (
            <Button
              onClick={() => {
                setCloseBookingsShowDialog(false);
                getData();
              }}
            >
              CLOSE
            </Button>
          )}
        </div>

        <h3 id="confirm-dialog-header">
          {closeBookingsMined && "Bookings Closed!"}
          {!closeBookingsMined &&
            !showCloseBookingsSign &&
            "Closing The Bookings"}
          {!closeBookingsMined &&
            showCloseBookingsSign &&
            "Please Sign to Confirm"}
        </h3>

        <div style={{ textAlign: "left", padding: "0px 20px 20px 20px" }}>
          {!closeBookingsMined && !showCloseBookingsSign && (
            <div>
              <p>Please wait while bookings are being closed...</p>
            </div>
          )}
          {!closeBookingsMined && showCloseBookingsSign && (
            <div>
              <p>
                Please sign the transaction from your wallet to confirm that you
                would like to close the bookings...
              </p>
            </div>
          )}

          {closeBookingsMined && (
            <div>
              Bookings have successfully been closed.<br></br>
              <p>
                <a
                  target="_blank"
                  href={`https://mumbai.polygonscan.com/tx/${closeBookingsTransactionHash}`}
                >
                  View transaction on Mumbai Polygonscan
                </a>
              </p>
            </div>
          )}
        </div>

        <div style={{ textAlign: "center", paddingBottom: "30px" }}>
          {!closeBookingsMined && <CircularProgress />}
        </div>
      </Dialog>
    );
  };

  // popup for when the arbiter is marking a haircut as good standard
  const GoodHairCutDialog = () => {
    return (
      <Dialog id="confirm-dialog" open={true}>
        <div style={{ textAlign: "right", padding: "0px 0px 0px 0px" }}>
          {goodHairCutMined && (
            <Button
              onClick={() => {
                setGoodHairCutShowDialog(false);
                getData();
              }}
            >
              CLOSE
            </Button>
          )}
        </div>

        <h3 id="confirm-dialog-header">
          {goodHairCutMined && "Haircut Marked as Good!"}
          {!goodHairCutMined &&
            !showGoodHairCutSign &&
            "Marking The Haircut Quality"}
          {!goodHairCutMined && showGoodHairCutSign && "Please Sign to Confirm"}
        </h3>

        <div style={{ textAlign: "left", padding: "0px 20px 20px 20px" }}>
          {!goodHairCutMined && !showGoodHairCutSign && (
            <div>
              <p>Please wait while the haircut quality is being stored...</p>
            </div>
          )}
          {!goodHairCutMined && showGoodHairCutSign && (
            <div>
              <p>
                Please sign the transaction from your wallet to confirm the
                haircut quality...
              </p>
            </div>
          )}

          {goodHairCutMined && (
            <div>
              Haircut has been successfully marked as good quality.<br></br>
              <p>
                <a
                  target="_blank"
                  href={`https://mumbai.polygonscan.com/tx/${goodHairCutTransactionHash}`}
                >
                  View transaction on Mumbai Polygonscan
                </a>
              </p>
            </div>
          )}
        </div>

        <div style={{ textAlign: "center", paddingBottom: "30px" }}>
          {!goodHairCutMined && <CircularProgress />}
        </div>
      </Dialog>
    );
  };

  // popup for when the arbiter is marking a haircut as not up to standard
  const BadHairCutDialog = () => {
    return (
      <Dialog id="confirm-dialog" open={true}>
        <div style={{ textAlign: "right", padding: "0px 0px 0px 0px" }}>
          {goodHairCutMined && (
            <Button
              onClick={() => {
                setBadHairCutShowDialog(false);
                getData();
              }}
            >
              CLOSE
            </Button>
          )}
        </div>

        <h3 id="confirm-dialog-header">
          {badHairCutMined && "Haircut Marked as Not Up To Standard!"}
          {!badHairCutMined &&
            !showBadHairCutSign &&
            "Marking The Haircut Quality"}
          {!badHairCutMined && showBadHairCutSign && "Please Sign to Confirm"}
        </h3>

        <div style={{ textAlign: "left", padding: "0px 20px 20px 20px" }}>
          {!badHairCutMined && !showBadHairCutSign && (
            <div>
              <p>Please wait while the haircut quality is being stored...</p>
            </div>
          )}
          {!badHairCutMined && showBadHairCutSign && (
            <div>
              <p>
                Please sign the transaction from your wallet to confirm the
                haircut quality...
              </p>
            </div>
          )}

          {badHairCutMined && (
            <div>
              Haircut has been successfully marked as not up to standard.
              <br></br>
              <p>
                <a
                  target="_blank"
                  href={`https://mumbai.polygonscan.com/tx/${badHairCutTransactionHash}`}
                >
                  View transaction on Mumbai Polygonscan
                </a>
              </p>
            </div>
          )}
        </div>

        <div style={{ textAlign: "center", paddingBottom: "30px" }}>
          {!badHairCutMined && <CircularProgress />}
        </div>
      </Dialog>
    );
  };

  // popup for when the arbiter is marking that a customer did not show up
  const NoShowDialog = () => {
    return (
      <Dialog id="confirm-dialog" open={true}>
        <div style={{ textAlign: "right", padding: "0px 0px 0px 0px" }}>
          {noShowMined && (
            <Button
              onClick={() => {
                setNoShowShowDialog(false);
                getData();
              }}
            >
              CLOSE
            </Button>
          )}
        </div>

        <h3 id="confirm-dialog-header">
          {noShowMined && "Appointment Marked As No Show!"}
          {!noShowMined &&
            !showNoShowShowSign &&
            "Marking The Haircut As No Show"}
          {!badHairCutMined && showNoShowShowSign && "Please Sign to Confirm"}
        </h3>

        <div style={{ textAlign: "left", padding: "0px 20px 20px 20px" }}>
          {!noShowMined && !showNoShowShowSign && (
            <div>
              <p>
                Please wait while the haircut is being marked as a no show...
              </p>
            </div>
          )}
          {!noShowMined && showNoShowShowSign && (
            <div>
              <p>
                Please sign the transaction from your wallet to confirm that
                this appointment is a no show...
              </p>
            </div>
          )}

          {noShowMined && (
            <div>
              Appointment has been successfully marked as a no show.
              <br></br>
              <p>
                <a
                  target="_blank"
                  href={`https://mumbai.polygonscan.com/tx/${noShowTransactionHash}`}
                >
                  View transaction on Mumbai Polygonscan
                </a>
              </p>
            </div>
          )}
        </div>

        <div style={{ textAlign: "center", paddingBottom: "30px" }}>
          {!noShowMined && <CircularProgress />}
        </div>
      </Dialog>
    );
  };

  return (
    <div>
      {/* <div id="get-tokens">
        <button id="get-matic">Get MATIC</button>
        <button id="get-wmatic">Get WMATIC</button>
      </div> */}

      <hr id="line-under-title"></hr>

      <div id="booking-state">
        {currentBookingState && <h2>Bookings Are Open</h2>}
        {!currentBookingState && <h2>Bookings Are Currently Closed</h2>}
      </div>

      {/* if the barber is connected, show the barber's custom page */}
      {isBarber && <Barber />}

      {/* if the arbiter is connected, show the arbiter's custom page */}
      {isArbiter && (
        // <Arbiter />
        <div id="arbiter">
          <h3>Arbiter Tools</h3>

          <Button>
            <div id="arbiter-good-haircut">
              <b>Good Standard</b>
              <div>
                <p>Input the booking ID:</p>
                <p>
                  <input
                    // id=""
                    // name=""
                    type={"tel"}
                    placeholder="1"
                    onChange={onGoodHairCutIDChange}
                  ></input>
                </p>
                <Button type="submit" id="submit" onClick={goodHairCut}>
                  Confirm
                </Button>
              </div>
            </div>
          </Button>

          <Button>
            <div id="arbiter-bad-haircut">
              <b>Not Up To Standard</b>
              <div>
                <p>Input the booking ID:</p>
                <p>
                  <input
                    id=""
                    name=""
                    type={"text"}
                    placeholder="1"
                    onChange={onBadHairCutIDChange}
                  ></input>
                </p>
                <Button type="submit" id="submit" onClick={badHairCut}>
                  Confirm
                </Button>
              </div>
            </div>
          </Button>

          <Button>
            <div id="arbiter-no-show">
              <b>No Show</b>
              <div>
                <p>Input the booking ID:</p>
                <p>
                  <input
                    id=""
                    name=""
                    type={"text"}
                    placeholder="1"
                    onChange={onNoShowIDChange}
                  ></input>
                </p>
                <Button type="submit" id="no-show-submit" onClick={noShow}>
                  Confirm
                </Button>
              </div>
            </div>
          </Button>
        </div>
      )}

      <div id="prices">
        {<h4 id="on-screen-fade-price">Fade Price: {fadePrice} WMATIC</h4>}
        {
          <h4 id="on-screen-levelcut-price">
            Level Cut Price: {levelCutPrice} WMATIC
          </h4>
        }
      </div>

      <div id="select-a-haircut">
        <h4 id="select-haircut-header">Select Haircut Type:</h4>
        <form name="myForm">
          <label id="fade-label">
            <input
              type={"radio"}
              // name="select-a-haircut"
              name="myRadios"
              id="fade-checkbox"
              value="Fade"
              // onClick={setSelectedHaircutType(true)}
              onClick={onChangeHaircutFade}
            ></input>
            Fade
          </label>

          <label id="levelcut-label">
            <input
              type={"radio"}
              // name="select-a-haircut"
              name="myRadios"
              id="levelcut-checkbox"
              value="LevelCut"
              // onClick={setSelectedHaircutType(false)}
              onClick={onChangeHaircutLevelCut}
              // onSelect=""
            ></input>
            Level Cut
          </label>
        </form>
      </div>

      <div>
        <p id="text-above-calendar">
          Book a time below by double-clicking a cell,<br></br> and enter your
          name in the "Title" section
        </p>
      </div>

      {/* The booking calendar  */}
      <div id="calendar">
        <Paper>
          <Scheduler
            // data={schedulerData} // dummy data
            data={appointments}
            firstDayOfWeek={0}
            // height={680}
          >
            <ViewState />
            <Toolbar />
            <EditingState onCommitChanges={sendAppointment} />
            <IntegratedEditing />
            <WeekView
              startDayHour={8}
              endDayHour={19}
              excludedDays={[0]}
              cellDuration={60}
              intervalCount={1.1}
            />{" "}
            {/*Excluding sunday*/}
            <DateNavigator />
            {/* <TodayButton /> */}
            <Appointments />
            <AppointmentForm deleteButton="false" />
          </Scheduler>
        </Paper>
      </div>

      <div id="cancel-booking">
        <h3>Cancel A Booking</h3>
        <p>Input the booking ID:</p>
        <p>
          <input
            id=""
            name=""
            type={"text"}
            placeholder="1"
            onChange={onCancelBookingIDChange}
          ></input>
        </p>
        <Button
          type="submit"
          id="cancel-booking-submit"
          onClick={cancelBooking}
        >
          Cancel
        </Button>
      </div>

      <div id="tip-the-barber">
        <h3>Tip The Barber</h3>
        <p>WMATIC amount:</p>
        <p>
          <input
            id=""
            name=""
            type={"text"}
            placeholder="1"
            onChange={onTipAmountChange}
          ></input>
        </p>
        <Button type="submit" id="tip-the-barber-submit" onClick={tipTheBarber}>
          Send Tip
        </Button>
      </div>

      {/* show the booking dialog when someone is booking an appointment  */}
      {bookingHaircutShowDialog && (
        <BookHaircutConfirmDialog></BookHaircutConfirmDialog>
      )}

      {/* show the cancel booking dialog when someone is cancelling a booking  */}
      {cancelBookingShowDialog && <CancelBookingDialog></CancelBookingDialog>}

      {/* show the tip the barber dialog when someon is tipping the barber  */}
      {tipTheBarberShowDialog && <TipTheBarberDialog></TipTheBarberDialog>}

      {/* show the open bookings dialog when the barber is opening up the bookings  */}
      {openBookingsShowDialog && (
        <OpenTheBookingsDialog></OpenTheBookingsDialog>
      )}

      {/* show the close bookings dialog when the barber is closing the bookings  */}
      {closeBookingsShowDialog && (
        <CloseTheBookingsDialog></CloseTheBookingsDialog>
      )}

      {/* show the change haircut price dialog when the barber is changing the booking price  */}
      {changeHaircutPriceShowDialog && (
        <ChangeHaircutPriceDialog></ChangeHaircutPriceDialog>
      )}

      {/* show the good haircut dialog when the arbiter marks the haircut as good quality  */}
      {goodHairCutShowDialoag && <GoodHairCutDialog></GoodHairCutDialog>}

      {/* show the bad haircut dialog when the arbiter marks the haircut as not up to standard */}
      {badHairCutShowDialog && <BadHairCutDialog></BadHairCutDialog>}

      {/* show the no show dialog when the arbiter marks that the customer did not turn up  */}
      {noShowShowDialog && <NoShowDialog></NoShowDialog>}
    </div>
  );
};

export default Calendar;
