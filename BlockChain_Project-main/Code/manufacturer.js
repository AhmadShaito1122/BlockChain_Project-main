// Require files module
var fs = require('fs');
var path = require('path');

// Require crypto module
var crypto = require('crypto');

// Add the axios module for HTTP requests
var axios = require('axios');

// Initialize web3 instance
const { Web3 } = require('web3');
const web3 = new Web3('http://127.0.0.1:30305');

// The contract address
var addr = "0xc21b34efb431c0a8494be88c8b76fd3018a61241";

// Define the private key (manufacturer's key)
const privateKey = fs.readFileSync('/home/kali/Desktop/BlockChain_Project-main/BlockChain_Project-main/nodes/private.pem', 'utf-8').trim();

// Show the Hash in the console.
console.log('Contract Location: ' + addr);

// Define the contract ABI
var abi = [
	{
		"constant": false,
		"inputs": [
			{
				"name": "_device",
				"type": "address"
			},
			{
				"name": "_name",
				"type": "string"
			},
			{
				"name": "_permissions",
				"type": "bytes1"
			}
		],
		"name": "addActuator",
		"outputs": [],
		"payable": false,
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"constant": false,
		"inputs": [
			{
				"name": "new_firmware",
				"type": "bytes"
			}
		],
		"name": "pushUpdate",
		"outputs": [],
		"payable": false,
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"constant": false,
		"inputs": [],
		"name": "kill",
		"outputs": [],
		"payable": false,
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"constant": true,
		"inputs": [
			{
				"name": "",
				"type": "address"
			}
		],
		"name": "actuators",
		"outputs": [
			{
				"name": "name",
				"type": "string"
			},
			{
				"name": "permissions",
				"type": "bytes1"
			}
		],
		"payable": false,
		"stateMutability": "view",
		"type": "function"
	},
	{
		"constant": true,
		"inputs": [],
		"name": "firmware",
		"outputs": [
			{
				"name": "",
				"type": "bytes"
			}
		],
		"payable": false,
		"stateMutability": "view",
		"type": "function"
	},
	{
		"constant": true,
		"inputs": [],
		"name": "owner",
		"outputs": [
			{
				"name": "",
				"type": "address"
			}
		],
		"payable": false,
		"stateMutability": "view",
		"type": "function"
	},
	{
		"constant": true,
		"inputs": [
			{
				"name": "myFirmware",
				"type": "bytes"
			}
		],
		"name": "checkForUpdate",
		"outputs": [
			{
				"name": "updateRequired",
				"type": "bool"
			}
		],
		"payable": false,
		"stateMutability": "view",
		"type": "function"
	},
	{
		"constant": true,
		"inputs": [
			{
				"name": "",
				"type": "address"
			}
		],
		"name": "sensors",
		"outputs": [
			{
				"name": "name",
				"type": "string"
			},
			{
				"name": "permissions",
				"type": "bytes1"
			}
		],
		"payable": false,
		"stateMutability": "view",
		"type": "function"
	},
	{
		"constant": false,
		"inputs": [
			{
				"name": "_device",
				"type": "address"
			},
			{
				"name": "_name",
				"type": "string"
			},
			{
				"name": "_permissions",
				"type": "bytes1"
			}
		],
		"name": "addSensor",
		"outputs": [],
		"payable": false,
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [],
		"payable": false,
		"stateMutability": "nonpayable",
		"type": "constructor"
	}
];

// Create contract instance
const contract = new web3.eth.Contract(abi, addr);  

// Grab the latest binary
const message = fs.readFileSync('/home/kali/Desktop/BlockChain_Project-main/FIRMWARE/ahmad.hex', 'utf-8').replace(/\s+/g, ''); // Remove all whitespace

// Define signer object
const signer = crypto.createSign('sha256');

// Load signer buffer
signer.update(message);
signer.end();

const signature = signer.sign(privateKey, 'hex');
//console.log("this is the sig : ",signature);//for debugging
// Construct the package
//const packagepp = `0x${signature}${message}`;
const packagepp = web3.utils.hexToBytes(`0x${signature}${message}`);


// Function to start mining
function startMining() {
    return axios.post('http://127.0.0.1:30305', {
        jsonrpc: "2.0",
        method: "miner_start",
        params: [],
        id: 1
    });
}

// Function to stop mining
function stopMining() {
    return axios.post('http://127.0.0.1:30305', {
        jsonrpc: "2.0",
        method: "miner_stop",
        params: [],
        id: 1
    });
}

// Function to get coinbase address
function getCoinbase() {
    return axios.post('http://127.0.0.1:30305', {
        jsonrpc: "2.0",
        method: "eth_coinbase",
        params: [],
        id: 1
    }).then(response => response.data.result);
	
}

// Start mining, push update, then stop mining
getCoinbase().then(function(coinbase) {
    startMining().then(() => {
        console.log("Mining started. Waiting for transaction to be mined...");

         //contract.methods.pushUpdate(packagepp).send({ from: coinbase, gas: 4700000 }) 
		contract.methods.pushUpdate(packagepp).send({
    from: coinbase,
    gas: 5000000,
    gasPrice: web3.utils.toWei('20', 'gwei')
})
//console.log("this is : ",packagepp) 
.then(tx => {
    console.log("Transaction sent! Transaction hash:", tx.transactionHash);
    return web3.eth.getTransactionReceipt(tx.transactionHash);
	
})
.then(receipt => {
    if (receipt && receipt.status) {
        console.log("Transaction mined successfully.");
		//console.log(contract.methods.getFirmware().call());
        return contract.methods.firmware().call(); 
		stopMining();
    } else {
        throw new Error("Transaction failed.");
    }
})
.then(response => {

    console.log("Firmware:", response);
})
.catch(error => {
	
    console.error('Error sending transaction or fetching firmware:', error);
    stopMining();
});
    });
}).catch(function(error) {
    console.error('Error:', error);
});