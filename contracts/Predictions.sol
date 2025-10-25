// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;


contract Predictions {
struct Prediction {
uint256 id;
uint256 timestamp; // unix time
string symbol;
int256 priceTimes100; // store price * 100 to avoid decimals
address reporter;
}


uint256 public nextId = 1;
mapping(uint256 => Prediction) public predictions;
event PredictionStored(uint256 id, string symbol, int256 priceTimes100, uint256 timestamp, address reporter);


function storePrediction(string calldata symbol, int256 priceTimes100) external returns (uint256) {
uint256 id = nextId;
predictions[id] = Prediction(id, block.timestamp, symbol, priceTimes100, msg.sender);
emit PredictionStored(id, symbol, priceTimes100, block.timestamp, msg.sender);
nextId++;
return id;
}


function getPrediction(uint256 id) external view returns (uint256, uint256, string memory, int256, address) {
Prediction storage p = predictions[id];
return (p.id, p.timestamp, p.symbol, p.priceTimes100, p.reporter);
}
}