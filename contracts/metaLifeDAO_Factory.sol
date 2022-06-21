// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "./metaLifeDAO_creator.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

contract metaLifeDAOFactory is Ownable {
    event NewMetaLifeDAO(address indexed creator, address dao, string name, string version);

    mapping(address => bool) public acceptalToken;

    mapping(address => uint256) public createFee;

    function setTokenFee(address token, uint256 fee, bool accept) external onlyOwner{
        acceptalToken[token] = accept;
        createFee[token] = fee;
    }

    function getValue(address to, uint256 amount) external onlyOwner{
        payable(to).transfer(amount);
    }

    function getToken(address token, address to, uint256 amount) external onlyOwner{
        IERC20(token).transfer(to, amount);
    }

    mapping(bytes32 => address) internal _creatorForDAO;

    function creatorForDAO(string memory version) public view returns(address){
        return _creatorForDAO[keccak256(abi.encodePacked(version))];
    }

    function setDAOCreator(string memory version, address creator) external onlyOwner{
        require(keccak256(abi.encodePacked(ImetaLifeDAOCreator(creator).version())) == keccak256(abi.encodePacked(version)), "Wrong version");

        _creatorForDAO[keccak256(abi.encodePacked(version))] = creator;
    }

    function _create(string memory version, bytes memory param) internal returns(address dao){
        dao = ImetaLifeDAOCreator(creatorForDAO(version)).createDAO(param);

        emit NewMetaLifeDAO(msg.sender, dao, metaLifeDAOBase(payable(dao)).daoName(), version);
    }

    function createWithValue(string memory version, bytes memory param) external payable{
        require(acceptalToken[address(0)], "Wrong token");
        require(msg.value >= createFee[address(0)], "Value");

        _create(version, param);
    }

    function createWithToken(string memory version, bytes memory param, address token) external payable{
        require(acceptalToken[token], "Wrong token");
        IERC20(token).transferFrom(msg.sender, address(this), createFee[token]);

        _create(version, param);
    }

}