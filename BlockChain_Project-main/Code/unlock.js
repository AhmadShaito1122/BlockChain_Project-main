/*
Node script for unlocking an account
Uses direct RPC calls to unlock an Ethereum account.
*/
var axios = require('axios');


// Define the account address, password, and unlock duration
var address = "0x15fc2f78d606900cb827025ac04617f13ab02e14";
var password = "password";
var duration = 1000; // in seconds

// Define the Ethereum node URL
var nodeUrl = "http://127.0.0.1:30305";

// Function to unlock an account
function unlockAccount(address, password, duration) {
    return axios.post(nodeUrl, {
        jsonrpc: "2.0",
        method: "personal_unlockAccount",
        params: [address, password, duration],
        id: 1
    });
}

// Unlock the account
unlockAccount(address, password, duration)
    .then(response => {
        console.log("Full Response:", response.data);
        if (response.data.result) {
            console.log("Account unlocked:", response.data.result);
        } else if (response.data.error) {
            console.error("Error unlocking account:", response.data.error);
        } else {
            console.error("Unexpected response format:", response.data);
        }
    })
    .catch(error => {
        console.error("Error making request:", error);
    });
