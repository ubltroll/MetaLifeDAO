from web3 import Web3
from data import *
import abi
from eth_abi.abi import decode_abi

web3 = Web3(Web3.HTTPProvider("https://jsonapi1.smartmesh.io"))

def get_DAO(dao_address):
    dao_address = web3.toChecksumAddress(dao_address)
    try:
        dao = DAOs.get(address = web3.toChecksumAddress(dao_address))
    except peewee.DoesNotExist:
        return
    res = {
        'address': dao_address,
        'name': dao.name,
        'uri': dao.uri,
        'info': dao.info,
        'version': dao.version,
        'createBlock': dao.createBlock,
        # 'proposals': make_page(get_proposals(dao_address)),
        # 'votes': make_page(get_vote(dao_address)),
        # 'erc20Trace': make_page(get_DAO_trace(dao_address))
        }
    return res

def is_with_coin(dao_instance):
    return dao_instance.version in ['MetaLifeDAO:101:withCoin', 'MetaLifeDAO:105:withMember',
        'MetaLifeDAO:202:NFTtoCoin', 'MetaLifeDAO:203:Crowdfund']

def adjust_value(str_value, dao_instance):
    if is_with_coin(dao_instance):
        return '%.2f'%(int(str_value)/10**18)
    else:
        return str_value

def get_proposals(dao_address):
    dao_address = web3.toChecksumAddress(dao_address)
    try:
        dao = DAOs.get(address = web3.toChecksumAddress(dao_address))
    except peewee.DoesNotExist:
        return []
    items = Proposals.select().order_by(Proposals.idInDAO.desc())
    return get_proposals_core(items)

def get_proposals_core(items):
    res =[]
    for item in items:
        res.append({
            'id': item.idInDAO,
            'proposer': item.proposer,
            'voteFor' : adjust_value(item.voteFor, item.dao),
            'voteAbstain': adjust_value(item.voteAbstain, item.dao),
            'voteAgainst': adjust_value(item.voteAgainst, item.dao),
            'quorum': adjust_value(item.quorum, item.dao),
            'startBlock': item.startBlock,
            'endBlock': item.endBlock,
            'commands': [],
            'status': get_proposal_status(item.dao.address, item.idInDAO)
            })
        for command in item.commands:
            res[-1]['commands'].append({
                'index': command.index,
                'target': command.target,
                'value': '%.2f SMT'%(int(command.value)/10**18),
                'data': command.data,
                'detail': command_explainer(command.data)
                })
    return res

def get_proposal_status(dao_address, index):
    dao_address = web3.toChecksumAddress(dao_address)
    dao_contract = web3.eth.contract(address=dao_address,abi=abi.MetaLifeDAOSimple)
    return dao_contract.functions.proposalState(index).call()

def get_vote(dao_address, proposal_id = None):
    dao_address = web3.toChecksumAddress(dao_address)
    try:
        dao = DAOs.get(address = web3.toChecksumAddress(dao_address))
    except peewee.DoesNotExist:
        return []
    if proposal_id:
        try:
            proposal = Proposals.get(dao = dao_address, idInDAO = proposal_id)
            items = Votes.select().where(Votes.proposal==proposal).order_by(Votes.createBlock.desc())
        except peewee.DoesNotExist:
            return []
    else:
        items = Votes.select().order_by(Votes.createBlock.desc())
    return get_vote_core(items)

def get_vote_core(items):
    res = []
    for item in items:
        res.append({
            'voter': item.voter,
            'support': item.support,
            'weight': adjust_value(item.weight, item.dao),
            'createBlock': item.createBlock
            })
    return res

def get_DAO_member(dao_address):
    dao_address = web3.toChecksumAddress(dao_address)
    try:
        dao = DAOs.get(address = web3.toChecksumAddress(dao_address))
    except peewee.DoesNotExist:
        return []
    res = []
    if is_with_coin(dao):
        for item in dao.erc20:
            res.append({
                'holder': item.holder,
                'weight': adjust_value(item.balance, dao)
                })
    else:
        balance = {}
        for item in dao.erc721:
            balance[item.holder] = balance.get(item.holder) + 1
        for k,v in balance.items():
            res.append({
                'holder': k,
                'weight': v
                })
    return res

def adjust_erc20(erc20, str_value):
    if type(erc20) is str:
        try:
            erc20 = web3.toChecksumAddress(erc20)
            erc20 = ERC20.get(address = web3.toChecksumAddress(erc20))
        except peewee.DoesNotExist:
            return
        token = web3.eth.contract(address=erc20,abi=abi.IERC20)
        erc20 = ERC20.create(address = log['address'],
            name=token.functions.name().call(),
            symbol=token.functions.symbol().call(),
            decimals=token.functions.decimals().call())
    return '%.2f'%(int(str_value)/10**erc20.decimals), str_value, erc20.symbol

def get_DAO_trace(dao_address):
    try:
        dao = DAOs.get(address = web3.toChecksumAddress(dao_address))
    except peewee.DoesNotExist:
        return []
    res = []
    for item in dao.trace.order_by(ERC20TraceForDAO.lastUpdateBlock.desc()):
        adjusted = adjust_erc20(item.token_address, item.amount)
        res.append({
            'from': item.from_,
            'to': item.to_,
            'token': item.token_address.address,
            'amount': adjusted[0],
            'amountRaw': adjusted[1],
            'symbol': adjusted[2],
            'createBlock': item.lastUpdateBlock
            })
    return res

def get_address_vote(address):
    address = web3.toChecksumAddress(address)
    items = Votes.select().where(Votes.voter==address).order_by(Votes.createBlock.desc())
    return get_vote_core(items)

def get_address_proposal(address):
    address = web3.toChecksumAddress(address)
    items = Proposals.select().where(Proposals.proposer==address).order_by(Proposals.createBlock.desc())
    return get_proposals_core(items)

def get_address_dao(address):
    res = []
    dao_addresses = []
    for item in ERC20Trace.select().where(ERC20Trace.holder==address):
        dao_addresses.append(item.dao.address)
    for item in ERC721Trace.select().where(ERC721Trace.holder==address):
        dao_addresses.append(item.dao.address)
    dao_addresses = list(set(dao_addresses))
    for dao_address in dao_addresses:
        try:
            dao = DAOs.get(address = web3.toChecksumAddress(dao_address))
        except peewee.DoesNotExist:
            continue
        res.append({'address': dao_address, 'name': dao.name, 'uri': dao.uri})
    return res

def get_daos():
    res = []
    for dao in DAOs.select().order_by(DAOs.createBlock.desc()):
        res.append({'address': dao.address, 'name': dao.name, 'uri': dao.uri})
    return res

def make_page(data, limit=5, offset=0):
    res = {
        'total': 0,
        'limit': limit,
        'offset': offset,
        'data':[]}
    if data:
        res['total'] = len(data)
        res['data'] = data[offset:offset+limit]
    return res

known_functions_raw=[
    'mint(address,uint256)',
    'transfer(address,uint256)',
    'transfer(address,uint256,uint256)',
    'setProposalThreshold(uint256)',
    'setVotingPeriod(uint64)',
    'setQuorumFactorInBP(uint256)',
    'setName(string)',
    'setURI(string)',
    'setInfo(string)',
    'approve(address,uint256)',
    'approve(address,uint256,uint256)'
    ]
known_functions = {}
for func in known_functions_raw:
    known_functions[Web3.keccak(text=func).hex()[:10]] = {
        'func': func,
        'decode': lambda x: decode_abi(func.split('(')[1].split(')')[0].split(','),
            bytes.fromhex(x[10:]))}

def command_explainer(call_data):
    if call_data[:2] != '0x':
        call_data = '0x' + call_data
    try:
        return {
            'func': known_functions[call_data[:10]]['func'],
            'params': known_functions[call_data[:10]]['decode'](call_data)
            }
    except:
        return None
