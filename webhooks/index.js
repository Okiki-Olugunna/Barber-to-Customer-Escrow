const express = require("express");
const bodyParser = require("body-parser");

const app = express();
const PORT = 3100;

// Twilio account info
const accountSid = process.env.TWILIO_ACCOUNT_SID;
const authToken = process.env.TWILIO_AUTH_TOKEN;
const client = require("twilio")(accountSid, authToken);
const fromPhone = process.env.FROM_PHONE;
const toPhone = process.env.TO_PHONE;

// JSON data
app.use(bodyParser.json());

// starting the server on port 3100
app.listen(PORT, () => console.log(`Running on PORT ${PORT}`));

// process GET request to http://localhost:3100/hello
app.get("/hello", (request, response) => {
  console.log(request.body);

  response.send("Testing 1, 2, 3! This is the test response.");
});

// POST request for Alchemy from Twilio
app.post("/webhook", (request, response) => {
  console.log(request.body);

  const activity = request.body.event.activity;
  const message = `🚀✂️💈 You have a booking!🚀✂️💈 \n The wallet address "${activity[0].fromAddress}" just booked a haircut. \n Their payment was ${activity[0].value} WMATIC. \n View the transaction here: https://mumbai.polygonscan.com/tx/${activity[0].hash}`;

  client.messages
    .create({
      body: message,
      from: fromPhone,
      to: toPhone,
    })
    .then((message) => console.log(message.sid));

  response.send(message);
});
