// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "./metaLifeDAO_Simple.sol";

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/token/ERC721/IERC721.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/IERC721Enumerable.sol";

contract metaLifeDAONFT is metaLifeDAOSimple{

    //------------
    //NFT binding
    //------------

    address public bindedNFT;

    mapping(uint256 => mapping(uint256 => uint256)) private _voteByTokenIdAndProposalId;

    function voteByTokenIdAndProposalId(uint256 tokenId, uint256 proposalId) public view returns (uint8){
        return uint8(_voteByTokenIdAndProposalId[tokenId][proposalId] - 1);
    }

    //------------
    //Override Interface: Extended Governance
    //------------

    string private constant _version="MetaLifeDAO:201:NFT";

    function version () public view virtual override returns (string memory){
        return _version;
    }

    function getVotes(address account, uint256 proposalId) public view virtual override returns (uint256 votes){
        //no snapshot for external governance token
        //uint256 blockNumber is reused as uint256 proposalId here
        uint256 balance = IERC20(bindedNFT).balanceOf(account);
        for (uint i; i < balance; i++){
            uint256 tokenId = IERC721Enumerable(bindedNFT).tokenOfOwnerByIndex(account, i);
            if (_voteByTokenIdAndProposalId[tokenId][proposalId] == 0){
                votes += 1;
            }
        }
    }

    function getVotes(address account) public view virtual returns (uint256 votes){
        return IERC721(bindedNFT).balanceOf(account);
    }

    function _checkVote(uint256 proposalId, address account) internal virtual override {}

    function _castVote(
        uint256 proposalId,
        address account,
        uint8 support
    ) internal virtual override returns (uint256 votes) {
        require(_state(proposalId) == ProposalState.Active, "Inactive");

        uint256 balance = IERC20(bindedNFT).balanceOf(account);
        for (uint i; i < balance; i++){
            uint256 tokenId = IERC721Enumerable(bindedNFT).tokenOfOwnerByIndex(account, i);
            if (_voteByTokenIdAndProposalId[tokenId][proposalId] == 0){
                _voteByTokenIdAndProposalId[tokenId][proposalId] = uint256(support) + 1;
                votes += 1;
            }
        }

        _countVote(proposalId, account, support, votes);

        emit VoteCast(account, proposalId, support, votes);

        return votes;
    }

    function _castVoteWithTokenId(
        uint256 proposalId,
        address account,
        uint8 support,
        uint256 tokenId
    ) internal virtual returns (uint256) {

        require(_state(proposalId) == ProposalState.Active, "Inactive");

        if (_voteByTokenIdAndProposalId[tokenId][proposalId] == 0){
            _voteByTokenIdAndProposalId[tokenId][proposalId] = uint256(support) + 1;
            _countVote(proposalId, account, support, 1);
            return 1;
        } else {
            return 0;
        }
    }

    function castVoteWithTokenId(
        uint256 proposalId,
        uint8 support,
        uint256 tokenId
    ) public virtual returns (uint256) {
        require(IERC721(bindedNFT).ownerOf(tokenId) == msg.sender);

        return _castVoteWithTokenId(proposalId, msg.sender, support, tokenId);
    }

    function castVoteWithTokenIdBySig(
        uint256 proposalId,
        uint8 support,
        uint256 tokenId,
        uint8 v,
        bytes32 r,
        bytes32 s
    ) public virtual returns (uint256) {
        address voter = ECDSA.recover(
            _hashTypedDataV4(
                keccak256(
                    abi.encode(
                        keccak256("Ballot(uint256 proposalId,uint8 support,uint256 tokenid)"),
                        proposalId,
                        support,
                        tokenId
                    )
                )
            ),
            v,
            r,
            s
        );

        require(IERC721(bindedNFT).ownerOf(tokenId) == voter);

        return _castVoteWithTokenId(proposalId, voter, support, tokenId);
    }

    function quorum(uint256 blockNumber) public view virtual override returns (uint256){
        return quorumSnapshot[blockNumber];
    }

    function quorum() public view virtual returns (uint256){
        return IERC20(bindedNFT).totalSupply();
    }

    mapping(uint256 => uint256) internal quorumSnapshot;

    function _afterProposalCreation(uint256 proposalId) internal virtual override {
        proposalId;
        quorumSnapshot[block.number] = quorum();
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
