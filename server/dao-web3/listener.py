
from data import *
import abi, time
from eth_abi.abi import decode_abi

factory = System.get(key='factory').value

def updateERC20Balance(address, dao, delta_value, block, contract):
    if address == '0x0000000000000000000000000000000000000000':
        return
    address = web3.toChecksumAddress(address)
    try:
        erc20_account = ERC20Trace.get(holder = address, dao=dao)
    except peewee.DoesNotExist:
        erc20_account = ERC20Trace.create(holder = address, dao=dao, address=contract)
    erc20_account.balance = str(int(erc20_account.balance) + delta_value)
    erc20_account.lastUpdateBlock = block
    erc20_account.save()

def erc20Transfer(log):
    #IERC20.Transfer'
    print('IERC20.Transfer @', log['address'])
    from_ = web3.toChecksumAddress(log['topics'][1].hex()[-40:])
    to_ = web3.toChecksumAddress(log['topics'][2].hex()[-40:])
    try:
        value, = decode_abi(['uint256'],bytes.fromhex(log['data'][2:]))
    except:
        value = 0
    try:
        dao = DAOs.get(erc20_address = log['address'])
    except peewee.DoesNotExist:
        print('pass')
    else:
        updateERC20Balance(from_, dao, -value, log['blockNumber'], log['address'])
        updateERC20Balance(to_, dao, value, log['blockNumber'], log['address'])
    dao = DAOs.get_or_none(address = from_) or DAOs.get_or_none(address = to_)
    if dao is None:
        print('no trace')
        return
    else:
        try:
            erc20 = ERC20.get(address = log['address'])
        except peewee.DoesNotExist:
            token = web3.eth.contract(address=log['address'],abi=abi.IERC20)
            ERC20.create(address = log['address'],
                name=token.functions.name().call(),
                symbol=token.functions.symbol().call(),
                decimals=token.functions.decimals().call())
        ERC20TraceForDAO.create(
            dao = dao,
            from_ = from_,
            to_ = to_,
            token_address = log['address'],
            amount = value,
            lastUpdateBlock = log['blockNumber'])

def updateERC721Balance(address, dao, token_id, block, contract):
    if address == '0x0000000000000000000000000000000000000000':
        return
    try:
        erc721_account = ERC721Trace.get(dao=dao, tokenId = token_id)
    except peewee.DoesNotExist:
        erc721_account = ERC721Trace.create(dao=dao, tokenId = token_id, address=contract)
    erc721_account.holder = web3.toChecksumAddress(address)
    erc721_account.lastUpdateBlock = block
    erc721_account.save()

def erc721Snapshot(address, dao, block):
    nft = web3.eth.contract(address=address,abi=abi.IERC721Enum)
    total_supply = nft.functions.totalSupply().call()
    for i in range(total_supply):
        updateERC721Balance(nft.functions.ownerOf(i+1).call(block_identifier=block),
            dao, i+1, block, address)

def erc721Transfer(log):
    #IERC721.Transfer
    try:
        dao = DAOs.get(erc721_address = log['address'])
    except peewee.DoesNotExist:
        return
    from_ = web3.toChecksumAddress(log['topics'][1].hex()[-40:])
    to_ = web3.toChecksumAddress(log['topics'][2].hex()[-40:])
    token_id = int(log['topics'][3].hex(),16)
    updateERC721Balance(to_, dao, token_id, log['blockNumber'], log['address'])

def newDAOListener(log):
    #event NewMetaLifeDAO(address indexed creator, address dao, string version);
    dao_address, version = decode_abi(['address', 'string'], bytes.fromhex(log['data'][2:]))
    dao_address = web3.toChecksumAddress(dao_address)
    dao = DAOs.create(address = dao_address, version = version,
        createBlock = log['blockNumber'], lastUpdateBlock = log['blockNumber'])
    updateDAOMetaInfo(dao_address, log['blockNumber'])
    #add ERC20/ERC721 Trace
    if version in ['MetaLifeDAO:101:withCoin', 'MetaLifeDAO:105:withMember',
        'MetaLifeDAO:202:NFTtoCoin', 'MetaLifeDAO:203:Crowdfund']:
        dao.erc20_address = web3.toChecksumAddress(dao_address)
        dao.save()
    if version == "MetaLifeDAO:201:NFT":
        dao_nft = web3.eth.contract(address=dao_address,abi=abi.MetaLifeDAONFT)
        print(dao_address)
        dao.erc721_address = dao_nft.functions.bindedNFT().call()
        dao.save()
        erc721Snapshot(dao.erc721_address, dao, log['blockNumber'])

def updateDAOMetaInfo(dao_address, block_number):
    dao_address = web3.toChecksumAddress(dao_address)
    dao_contract = web3.eth.contract(address=dao_address,abi=abi.MetaLifeDAOSimple)
    try:
        dao = DAOs.get(address = dao_address)
    except peewee.DoesNotExist:
        return
    dao.name = dao_contract.functions.daoName().call()
    dao.uri = dao_contract.functions.daoURI().call()
    dao.info = dao_contract.functions.daoInfo().call()
    dao.votingPeriod = str(dao_contract.functions.votingPeriod().call)
    dao.quorumFactorInBP = str(dao_contract.functions.quorumFactorInBP().call)
    dao.proposalThreshold = str(dao_contract.functions.proposalThreshold().call)
    dao.lastUpdateBlock = block_number
    dao.save()

def newProposal(log):
    try:
        dao = DAOs.get(address = web3.toChecksumAddress(log['address']))
    except peewee.DoesNotExist:
        return
    dao_contract = web3.eth.contract(address=log['address'],abi=abi.MetaLifeDAOSimple)
    (id_in_dao, proposer, start_block, end_block, description) = decode_abi(
        ['uint256','address','uint256','uint256', 'string'],
        bytes.fromhex(log['data'][2:]))
    proposal = Proposals.create(dao = dao, createBlock = log['blockNumber'],
        idInDAO = id_in_dao, proposer = web3.toChecksumAddress(proposer),
        description = description, startBlock = start_block, endBlock = end_block,
        lastUpdateBlock = log['blockNumber'])
    proposal.quorum = str(dao_contract.functions.quorum(start_block).call())
    proposal.save()
    (targets, values, calldatas,_,_,_,_) = dao_contract.functions.proposalInfo(0).call()
    for i in range(len(targets)):
        ProposalCommands.create(
            proposal = proposal,
            index = i,
            target = targets[i],
            value = str(values[i]),
            data = '0x'+calldatas[i].hex(),
            createBlock = log['blockNumber']
            )

def voteCast(log):
    #event VoteCast(address indexed voter, uint256 proposalId, uint8 support, uint256 weight);
    voter = web3.toChecksumAddress(log['topics'][1].hex()[-40:])
    proposal_id, support, weight = decode_abi(['uint256','uint8','uint256'], bytes.fromhex(log['data'][2:]))
    try:
        dao = DAOs.get(address = web3.toChecksumAddress(log['address']))
    except peewee.DoesNotExist:
        return
    proposal = Proposals.get(dao = dao, idInDAO = proposal_id)
    Votes.create(dao=dao, proposal= proposal,
        support = support, weight = str(weight), voter = voter, createBlock = log['blockNumber'])
    if support == 0:
        proposal.voteAgainst = str(int(proposal.voteAgainst) + weight)
    elif support == 1:
        proposal.voteFor = str(int(proposal.voteFor) + weight)
    elif support == 2:
        proposal.voteAbstain = str(int(proposal.voteAbstain) + weight)
    proposal.save()

def search_block(fromBlock , toBlock=None):
    #print(toBlock)
    if toBlock is None:
        toBlock = fromBlock
    logs = web3.eth.getLogs({"fromBlock":fromBlock , "toBlock": toBlock })
    for log in logs:
        #print(log['topics'][0].hex() )
        #look for NewMetaLifeDAO
        if (log['topics'][0].hex() == '0xfc56cfb07db536684194c9131a1fc720f6dbaf971d98eec304f9a04d85340d0e'
            and log.address == System.get(key='factory').value):
            print('newDAOListener')
            newDAOListener(log)
        #look for UpdateDAOMetaInfo
        elif (log['topics'][0].hex() == '0x0476831fbd909e3642e5bbb00a1eaaf8af1b39b2e2d7e3268d024f3769572676'):
            updateDAOMetaInfo(log.address, log['blockNumber'])
        #look for newProposal
        elif (log['topics'][0].hex() == '0xa00fcf4f5e03cc2f4818b8f380a8f2a06479e49bf0765e5fec09aebdaf922bbc'):
            newProposal(log)
        #look for Transfer ERC20
        elif (log['topics'][0].hex() == '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'):
            erc20Transfer(log)
        #look for Transfer ERC721
        elif (log['topics'][0].hex() == '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'):
            erc721Transfer(log)
        #look for VoteCast
        elif (log['topics'][0].hex() == '0x2c9deb38f462962eadbd85a9d3a4120503ee091f1582eaaa10aa8c6797651d29'):
            voteCast(log)

    System.update(value=str(toBlock)).where(System.key=='block').execute()

def search():
    block_now = int(System.get(key='block').value)
    block_chain = web3.eth.blockNumber
    if block_chain > block_now:
        print('sync %d / %d'%(block_now, block_chain))
        search_block(block_now+1, min(block_chain, block_now+200))

if __name__ == "__main__":
    while True:
        if db.is_closed():
            db.connect()
        search()
        time.sleep(1)
        db.close()
