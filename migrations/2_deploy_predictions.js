const Predictions = artifacts.require("Predictions");

module.exports = function (deployer) {
  deployer.deploy(Predictions);
};
