import "./App.css";
import detectEthereumProvider from "@metamask/detect-provider";
import { useEffect, useState } from "react";
import { utils } from "ethers";
import Calendar from "./components/Calendar";

function App() {
  const [account, setAccount] = useState(false);

  useEffect(() => {
    isConnected();
  }, []);

  const isConnected = async () => {
    const provider = await detectEthereumProvider();
    const accounts = await provider.request({ method: "eth_accounts" });

    if (accounts.length > 0) {
      setAccount(accounts[0]);
    } else {
      console.log("No authorised account found");
    }
  };

  const connect = async () => {
    try {
      const provider = await detectEthereumProvider();

      // getting the chainid of the current network the user is connected to
      const chainId = await provider.request({ method: "eth_chainId" });

      const mumbai = utils.hexValue(80001);
      if (chainId !== mumbai) {
        // switching the user's network to Mumbai
        await window.ethereum.request({
          method: "wallet_switchEthereumChain",
          params: [{ chainId: mumbai }],
        });
      }

      // returns an array of accounts
      const accounts = await provider.request({
        method: "eth_requestAccounts",
      });

      // check if the array is at least 1 element
      if (accounts.length > 0) {
        console.log("Account found:", accounts);
        setAccount(accounts[0]);
        console.log(account);
      } else {
        console.log("No account found");
      }
    } catch (error) {
      console.log(error);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        {account && (
          <div id="get-tokens">
            <a target={"_blank"} href="https://mumbaifaucet.com/">
              <button id="get-matic">Get MATIC</button>
            </a>
            <a
              target={"_blank"}
              href="https://legacy.quickswap.exchange/#/swap"
            >
              <button id="get-wmatic">Get WMATIC</button>
            </a>
          </div>
        )}

        <h1>Barber to Customer Escrow</h1>

        {/* <br></br> */}
        <div id="slogan">Book in advance and earn cashback</div>

        {!account && <button onClick={connect}>Connect Wallet</button>}

        {account && <Calendar account={account} />}
      </header>
    </div>
  );
}

export default App;
