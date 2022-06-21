// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "./governance/metaLifeDAO_withCoin.sol";
import "./governance/metaLifeDAO_withMember.sol";
import "./governance/metaLifeDAO_NFT.sol";
import "./governance/metaLifeDAO_NFTtoCoin.sol";
import "./governance/metaLifeDAO_Crowdfund.sol";


interface ImetaLifeDAOFactory{
    function isMetaLifeDAOFactory() external view returns(bool);
}

interface ImetaLifeDAOCreator{
    function version() external view returns(string memory);
    function createDAO(bytes memory param) external returns(address dao);
}

contract creator_withCoin is ImetaLifeDAOCreator{
    function version() external pure override returns(string memory){
        return "MetaLifeDAO:101:withCoin";
    }

    function createDAO(bytes memory param) external override returns(address dao){
        (string memory _daoName,
        string memory _daoURI,
        string memory _daoInfo,
        uint64 votingPeriod_,
        uint256 quorumFactorInBP_,
        address[] memory initialMembers,
        uint256[] memory initialSupplies)= abi.decode(param, (string,string,string,uint64,uint256,address[],uint256[]));
        dao = address(new metaLifeDAOwithCoin(_daoName, _daoURI, _daoInfo, votingPeriod_, quorumFactorInBP_, initialMembers, initialSupplies));
    }
}

contract creator_withMember is ImetaLifeDAOCreator{
    function version() external pure override returns(string memory){
        return "MetaLifeDAO:105:withMember";
    }

    function createDAO(bytes memory param) external override returns(address dao){
        (string memory _daoName,
        string memory _daoURI,
        string memory _daoInfo,
        uint64 votingPeriod_,
        uint256 quorumFactorInBP_,
        address[] memory initialMembers)= abi.decode(param, (string,string,string,uint64,uint256,address[]));
        dao = address(new metaLifeDAOwithMember(_daoName, _daoURI, _daoInfo, votingPeriod_, quorumFactorInBP_, initialMembers));
    }
}

contract creator_NFT is ImetaLifeDAOCreator{
    function version() external pure override returns(string memory){
        return "MetaLifeDAO:201:NFT";
    }

    function createDAO(bytes memory param) external override returns(address dao){
        (string memory _daoName,
        string memory _daoURI,
        string memory _daoInfo,
        uint64 votingPeriod_,
        uint256 quorumFactorInBP_,
        address bindedNFT_)= abi.decode(param, (string,string,string,uint64,uint256,address));
        dao = address(new metaLifeDAONFT(_daoName, _daoURI, _daoInfo, votingPeriod_, quorumFactorInBP_, bindedNFT_));
    }
}

contract creator_NFTtoCoin is ImetaLifeDAOCreator{
    function version() external pure override returns(string memory){
        return "MetaLifeDAO:202:NFTtoCoin";
    }

    function createDAO(bytes memory param) external override returns(address dao){
        (string memory _daoName,
        string memory _daoURI,
        string memory _daoInfo,
        uint64 votingPeriod_,
        uint256 quorumFactorInBP_,
        address bindedNFT_,
        uint8 decimals_,
        uint256 coinsPerNFT_)= abi.decode(param, (string,string,string,uint64,uint256,address,uint8,uint256));
        dao = address(new metaLifeDAONFTtoCoin(_daoName, _daoURI, _daoInfo, votingPeriod_, quorumFactorInBP_, bindedNFT_, decimals_, coinsPerNFT_));
    }
}

contract creator_Crowdfund is ImetaLifeDAOCreator{
    function version() external pure override returns(string memory){
        return "MetaLifeDAO:203:Crowdfund";
    }
        
    function createDAO(bytes memory param) external override returns(address dao){
        (string memory _daoName,
        string memory _daoURI,
        string memory _daoInfo,
        uint64 votingPeriod_,
        uint256 quorumFactorInBP_,
        address _fundingToken,
        uint256 _fundingGoal,
        uint256 _fundingTokenToVotes,
        uint64 _fundingPeriod,
        address _starter)= abi.decode(param, (string,string,string,uint64,uint256,address,uint256,uint256,uint64,address));
        dao = address(new metaLifeDAOCrowdfund(_daoName, _daoURI, _daoInfo, votingPeriod_, quorumFactorInBP_,
         _fundingToken, _fundingGoal, _fundingTokenToVotes, _fundingPeriod, _starter));
    }
}