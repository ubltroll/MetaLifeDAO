from web3 import Web3
from data import *
from control import *

web3 = Web3(Web3.HTTPProvider("https://jsonapi1.smartmesh.io"))
from eth_abi.abi import encode_abi
from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "MetaLifeDAO Web3 Server"

@app.route('/encode/command/mint', methods=['GET', 'POST'])
def command_mint():
    param = encode_abi([
        'address',
        'uint256'],[
        str(request.json['to']),
        int(request.json['amount'])])
    return jsonify({
    "value": 0,
    "param": Web3.keccak(text='mint(address,uint256)').hex()[:10]+param.hex()})

@app.route('/encode/command/transferERC20', methods=['GET', 'POST'])
def command_mtransferERC20():
    param = encode_abi([
        'address',
        'uint256'],[
        str(request.json['to']),
        int(request.json['amount'])])
    return jsonify({
    "value": 0,
    "param": Web3.keccak(text='transfer(address,uint256)').hex()[:10]+param.hex()})

@app.route('/encode/command/transferERC721', methods=['GET', 'POST'])
def command_transferERC721():
    param = encode_abi([
        'address',
        'uint256',
        'uint256'],[
        str(request.json['to']),
        int(request.json['amount']),
        int(request.json['token_id'])])
    return jsonify({
    "value": 0,
    "param": Web3.keccak(text='transfer(address,uint256,uint256)').hex()[:10]+param.hex()})

@app.route('/encode/command/transferSMT', methods=['GET', 'POST'])
def command_transferSMT():
    return jsonify({
    "value": int(request.json['amount']),
    "param": ''})

@app.route('/encode/command/setName', methods=['GET', 'POST'])
def command_setName():
    param = encode_abi([
        'string',],[
        str(request.json['name'])])
    return jsonify({
    "value": 0,
    "param": Web3.keccak(text='setName(string)').hex()[:10]+param.hex()})

@app.route('/encode/command/setURI', methods=['GET', 'POST'])
def command_setURI():
    param = encode_abi([
        'string',],[
        str(request.json['uri'])])
    return jsonify({
    "value": 0,
    "param": Web3.keccak(text='setURI(string)').hex()[:10]+param.hex()})

@app.route('/encode/command/setInfo', methods=['GET', 'POST'])
def command_setInfo():
    param = encode_abi([
        'string',],[
        str(request.json['info'])])
    return jsonify({
    "value": 0,
    "param": Web3.keccak(text='setInfo(string)').hex()[:10]+param.hex()})

@app.route('/encode/command/setVotingPeriod', methods=['GET', 'POST'])
def command_setVotingPeriod():
    param = encode_abi([
        'uint64',],[
        int(request.json['votingPeriod'])])
    return jsonify({
    "value": 0,
    "param": Web3.keccak(text='setVotingPeriod(uint64)').hex()[:10]+param.hex()})

@app.route('/encode/command/setQuorumFactorInBP', methods=['GET', 'POST'])
def command_setQuorumFactorInBP():
    param = encode_abi([
        'uint256',],[
        int(request.json['quorumFactorInBP'])])
    return jsonify({
    "value": 0,
    "param": Web3.keccak(text='setQuorumFactorInBP(uint256)').hex()[:10]+param.hex()})

@app.route('/encode/command/setProposalThreshold', methods=['GET', 'POST'])
def command_setProposalThreshold():
    param = encode_abi([
        'uint256',],[
        int(request.json['proposalThreshold'])])
    return jsonify({
    "value": 0,
    "param": Web3.keccak(text='setProposalThreshold(uint256)').hex()[:10]+param.hex()})


@app.route('/encode/creator/withCoin', methods=['GET', 'POST'])
def creator_withCoin():
    param = encode_abi([
        'string',
        'string',
        'string',
        'uint64',
        'uint256',
        'address[]',
        'uint256[]'],[
        str(request.json['daoName']),
        str(request.json['daoURI']),
        str(request.json['daoInfo']),
        int(request.json['votingPeriod']),
        int(request.json['quorumFactorInBP']),
        [web3.toChecksumAddress(address) for address in request.json['initialMembers']],
        [int(amount) for amount in request.json['initialSupplies']]])
    return jsonify({"param": '0x'+ param.hex()})

@app.route('/encode/creator/NFT', methods=['GET', 'POST'])
def creator_NFT():
    param = encode_abi([
        'string',
        'string',
        'string',
        'uint64',
        'uint256',
        'address'],[
        str(request.json['daoName']),
        str(request.json['daoURI']),
        str(request.json['daoInfo']),
        int(request.json['votingPeriod']),
        int(request.json['quorumFactorInBP']),
        web3.toChecksumAddress(str(request.json['bindedNFT']))])
    return jsonify({"param": '0x'+ param.hex()})

@app.route('/encode/creator/withMember', methods=['GET', 'POST'])
def creator_withMember():
    param = encode_abi([
        'string',
        'string',
        'string',
        'uint64',
        'uint256',
        'address[]'],[
        str(request.json['daoName']),
        str(request.json['daoURI']),
        str(request.json['daoInfo']),
        int(request.json['votingPeriod']),
        int(request.json['quorumFactorInBP']),
        [web3.toChecksumAddress(address) for address in request.json['initialMembers']]])
    return jsonify({"param": '0x'+ param.hex()})

@app.route('/encode/creator/NFTtoCoin', methods=['GET', 'POST'])
def creator_NFTtoCoin():
    param = encode_abi([
        'string',
        'string',
        'string',
        'uint64',
        'uint256',
        'address',
        'uint8',
        'uint256'],[
        str(request.json['daoName']),
        str(request.json['daoURI']),
        str(request.json['daoInfo']),
        int(request.json['votingPeriod']),
        int(request.json['quorumFactorInBP']),
        web3.toChecksumAddress(str(request.json['bindedNFT'])),
        int(request.json['decimals']),
            int(request.json['coinsPerNFT']) ])
    return jsonify({"param": '0x'+ param.hex()})

@app.route('/encode/creator/Crowdfund', methods=['GET', 'POST'])
def creator_crowdfund():
    param = encode_abi([
        'string',
        'string',
        'string',
        'uint64',
        'uint256',
        'address',
        'uint256',
        'uint256',
        'uint64',
        'address'],[
        str(request.json['daoName']),
        str(request.json['daoURI']),
        str(request.json['daoInfo']),
        int(request.json['votingPeriod']),
        int(request.json['quorumFactorInBP']),
        web3.toChecksumAddress(str(request.json['fundingToken'])),
        int(request.json['fundingGoal']),
        int(request.json['fundingTokenToVotes']),
        int(request.json['fundingPeriod']),
        web3.toChecksumAddress(str(request.json['starter']))
        ])
    return jsonify({"param": '0x'+ param.hex()})

@app.route('/dao/info', methods=['GET', 'POST'])
def query_get_DAO():
    dao = request.json['dao']
    return jsonify(get_DAO(dao))

@app.route('/dao/list', methods=['GET', 'POST'])
def query_get_DAO_list():
    limit = int(request.json.get('limit', 5))
    offset = int(request.json.get('offset', 0))
    res = get_daos()
    return jsonify(make_page(res, limit, offset))

@app.route('/dao/proposals', methods=['GET', 'POST'])
def query_get_proposal():
    dao = request.json['dao']
    limit = int(request.json.get('limit', 5))
    offset = int(request.json.get('offset', 0))
    status = request.json.get('status')
    res = get_proposals(dao)
    if status is not None:
        res = [item for item in res if item['status']==int(status)]
    return jsonify(make_page(res, limit, offset))

@app.route('/dao/vote', methods=['GET', 'POST'])
def query_get_vote():
    dao = request.json['dao']
    limit = int(request.json.get('limit', 5))
    offset = int(request.json.get('offset', 0))
    proposal_id = request.json.get('proposal_id')
    if proposal_id is not None:
        proposal_id = int(proposal_id)
    res = get_vote(dao, proposal_id)
    return jsonify(make_page(res, limit, offset))

@app.route('/dao/member', methods=['GET', 'POST'])
def query_get_dao_member():
    dao = request.json['dao']
    limit = int(request.json.get('limit', 5))
    offset = int(request.json.get('offset', 0))
    res = get_DAO_member(dao)
    return jsonify(make_page(res, limit, offset))

@app.route('/dao/erc20Trace', methods=['GET', 'POST'])
def query_get_dao_trace():
    dao = request.json['dao']
    limit = int(request.json.get('limit', 5))
    offset = int(request.json.get('offset', 0))
    res = get_DAO_trace(dao)
    return jsonify(make_page(res, limit, offset))

@app.route('/address/daos', methods=['GET', 'POST'])
def query_get_address_daos():
    res = get_address_dao(request.json['address'])
    limit = int(request.json.get('limit', 5))
    offset = int(request.json.get('offset', 0))
    return jsonify(make_page(res, limit, offset))

@app.route('/address/votes', methods=['GET', 'POST'])
def query_get_address_votes():
    res = get_address_vote(request.json['address'])
    limit = int(request.json.get('limit', 5))
    offset = int(request.json.get('offset', 0))
    return jsonify(make_page(res, limit, offset))

@app.route('/address/proposals', methods=['GET', 'POST'])
def query_get_address_proposals():
    res = get_address_proposal(request.json['address'])
    limit = int(request.json.get('limit', 5))
    offset = int(request.json.get('offset', 0))
    return jsonify(make_page(res, limit, offset))

if __name__ =='__main__':
    app.run(port=5050, debug = True)
