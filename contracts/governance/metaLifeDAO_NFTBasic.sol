// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "./metaLifeDAO_NFT.sol";

contract metaLifeDAONFTBasic is _metaLifeDAONFT{
    string private constant _version="MetaLifeDAO:200:NFTBasic";

    function getVotes(address account, uint256 proposalId) public view virtual override returns (uint256 votes){
        //no snapshot for external governance token
        proposalId;
        return getVotes(account);
    }

    constructor (string memory _daoName,
        string memory _daoURI,
        string memory _daoInfo,
        uint64 votingPeriod_,
        uint256 quorumFactorInBP_,
        address bindedNFT_
    ) metaLifeDAOConfig(_daoName, _daoURI, _daoInfo, _version) {
        bindedNFT = bindedNFT_;
        _votingPeriod = votingPeriod_;
        _quorumFactorInBP = quorumFactorInBP_;
    }
}
