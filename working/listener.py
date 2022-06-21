from web3 import Web3
from data import *

web3 = Web3(Web3.HTTPProvider("https://jsonapi1.smartmesh.io"))

factory = System.get(key='factory').value

def updateBalance(address, dao, delta_value, block, contract):
    if address == '0x0000000000000000000000000000000000000000':
        return
    account,_ = Address.get_or_create(address = web3.toChecksumAddress(address))
    try:
        erc20_account = ERC20Trace.get(holder = account, dao=dao)
    except peewee.DoesNoeExist:
        erc20_account = ERC20Trace.create(holder = account, dao=dao, address=contract)
    erc20_account.balance = str(int(erc20_account.balance) + delta_value)
    erc20_account.lastUpdateBlock = block
    erc20_account.save()
        

def erc20Transfer(log):
    #IERC20.Transfer
    try:
        dao = DAOs.get(erc20_address = log['address'])
    except peewee.DoesNoeExist:
        return
    from_ = log['topics'][1]
    to_ = log['topics'][2]
    value = log['data'][0]
    updateBalance(from_, dao, -value, log['block'], log['address'])
    updateBalance(to_, dao, value, log['block'], log['address'])
    
def newDAOListener(log):
    pass

def createProposalListener(log):
    pass

def newDAOListener(log):
    pass