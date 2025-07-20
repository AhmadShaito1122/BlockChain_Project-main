/*
Node script for the miner
Checks the hashes of the firmware binaries installed on each device and compares with manufacturer hash
*/

var fs = require('fs');
var path = require('path');
const { Web3 } = require('web3');
var crypto = require('crypto');
var cron = require('node-cron');
const { Client } = require('ssh2'); // Replacing scp2 with ssh2 for stability

const web3 = new Web3('http://127.0.0.1:30305');
var addr = "0xc21b34efb431c0a8494be88c8b76fd3018a61241";
const publicKey = fs.readFileSync('/home/kali/Desktop/BlockChain_Project-main/BlockChain_Project-main/nodes/public.pem', 'utf-8');

console.log('Contract Location: ' + addr);

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

var contract = new web3.eth.Contract(abi, addr);
var interval = 5;

console.log('-----------------------------------');
console.log('-----------------------------------');

let device_array = ['192.168.28.134']; 
var numDevices = device_array.length;
var manufacturer_firmware;

function uploadFirmware(deviceIP, localPath, remotePath) {
	return new Promise((resolve, reject) => {
		const conn = new Client();
		conn.on('ready', () => {
			console.log(`Connected to ${deviceIP}`);
			conn.sftp((err, sftp) => {
				if (err) return reject(err);

				const readStream = fs.createReadStream(localPath);
				const writeStream = sftp.createWriteStream(remotePath);

				writeStream.on('close', () => {
					console.log('Firmware uploaded successfully');
					conn.end();
					resolve();
				});

				writeStream.on('error', reject);
				readStream.pipe(writeStream);
			});
		}).on('error', reject).connect({
			host: deviceIP,
			port: 22,
			username: 'root',
			password: 'ahmad1122'
		});
	});
}

var cronJob = cron.schedule('*/'+interval+' * * * * *', function(){
	contract.methods.firmware().call()
	.then(function(response){
		const verifier = crypto.createVerify('sha256');
		manufacturer_signature = response.substring(2,514).trim();
		manufacturer_firmware = response.substring(514, response.length).trim();

		var signature = Buffer.from(manufacturer_signature, 'hex');
		verifier.update(manufacturer_firmware);
		verifier.end();

		var verified = verifier.verify(publicKey, signature);
		if (verified){
			console.log("Manufactuere signature verified")
			var writepath = path.join(__dirname, "FIRMWARE.hex")
			fs.writeFile(writepath, manufacturer_firmware, function(err) {
				if(err) {
					return console.log(err);
				}
				console.log("Latest firmware saved");

				for (var i = 0; i < numDevices; ++i) {
					var filepath = path.join(__dirname, 'sensorRequests' + i.toString() + '.txt');
					var buffer = fs.readFileSync(filepath);
					console.log('Device', i.toString(), 'firmware:', buffer.toString());

					if (buffer.toString() != manufacturer_firmware) {
						console.log("this is the buffer ", buffer);
						console.log("this is the manufacturer firmware  ", manufacturer_firmware);
						console.log('Update Required for Device ' + i.toString());

					uploadFirmware(
						device_array[i],
						path.join(__dirname, 'FIRMWARE.hex'),  // ✅ correct local path
						'/root/Devices/FYP/FIRMWARE_0.hex'               // ✅ correct remote path
					).catch(err => {
							console.error("Error during SCP transfer:", err.message || err);
						});
					} else {
						console.log("Device firmware up to date!");
					}
				}
				console.log('\n');
			}); 
		}else{
			console.log("Manufacturer Signature not verified. Package will be discarded.")
		}
	});
});
