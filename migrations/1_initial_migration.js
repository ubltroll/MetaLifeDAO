const DAOwithCoin = artifacts.require("metaLifeDAOwithCoin");
const DAOwithMember = artifacts.require("metaLifeDAOwithMember");

module.exports = function (deployer) {
    deployer.deploy(DAOwithCoin,"test", "test", "test", 100, 4500, [], []);
};
