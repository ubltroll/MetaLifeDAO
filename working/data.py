
import peewee

db_config = {
    'host':'0.0.0.0',
    'port':3306,
    'user':'root',
    'passwd':'XX!',
    'database':'X',
}

db=PooledMySQLDatabase(host=db_config['host'],
                      port=db_config['port'],
                      user=db_config['user'],
                      passwd=db_config['passwd'],
                      database=db_config['database'],
                      charset='utf8',
                      stale_timeout=1000,
                      max_connections=100)

class Address(peewee.Model):
    address = peewee.CharField(unique = True, index = True)

class DAOs(peewee.Model):
    dao_id = peewee.AutoField()
    name = peewee.CharField()
    uri = peewee.CharField()
    info = peewee.CharField()
    version = peewee.CharField()
    creator = peewee.ForeignKeyField(Address, backref='create_DAOs', null = True) 
    erc20_address = peewee.CharField(index=True, null=True)
    erc721_address = peewee.CharField(index=True, null=True)
    proposal_counts  = peewee.IntegerField()
    immutables = peewee.CharField()
    createBlock = peewee.IntegerField()
    lastUpdateBlock = peewee.IntegerField()

class Proposals(peewee.Model):
    proposal_id = peewee.AutoField()
    dao = peewee.ForeignKeyField(DAOs, backref='proposals') 
    id_in_dao = peewee.IntegerField(index=True)
    vote_for = peewee.CharField()
    vote_against = peewee.CharField()
    vote_abstain = peewee.CharField()
    quorum = peewee.CharField()
    status = peewee.IntegerField()
    start_block = peewee.IntegerField()
    end_block = peewee.IntegerField()
    lastUpdateBlock = peewee.IntegerField()

class ProposalCommands(peewee.Model):
    proposal = peewee.ForeignKeyField(Proposals, backref='commands') 
    pos = peewee.IntegerField(index=True)
    target = peewee.CharField()
    call_value = peewee.CharField()
    call_data = peewee.CharField()

class Votes(peewee.Model):
    dao = peewee.ForeignKeyField(DAOs)
    proposal = peewee.ForeignKeyField(Proposals, backref='commands') 
    voter = peewee.ForeignKeyField(Address, backref='votes', null = True) 
    weight = peewee.CharField() #or token_id in Votes for NFT
    option = peewee.IntegerField()
    createBlock = peewee.IntegerField()

class ERC20Trace(peewee.Model):
    dao = peewee.ForeignKeyField(DAOs, backref='erc20')
    holder = peewee.ForeignKeyField(Address, backref='votes', null = True) 
    address = peewee.CharField()
    balance = peewee.CharField(default='0')
    lastUpdateBlock = peewee.IntegerField()

class Delegates(peewee.Model):
    dao = peewee.ForeignKeyField(DAOs, backref='erc721')
    delegator = peewee.ForeignKeyField(Address, backref='as_delegator')
    delegatee = peewee.ForeignKeyField(Address, backref='as_delegatee')
    lastUpdateBlock = peewee.IntegerField()

class ERC721Trace(peewee.Model):
    dao = peewee.ForeignKeyField(DAOs, backref='erc721')
    holder = peewee.ForeignKeyField(Address, backref='votes', null = True) 
    address = peewee.CharField()
    token_id = peewee.IntegerField(index=True)
    delegatee = peewee.CharField(null=True, index=True)
    lastUpdateBlock = peewee.IntegerField()

class System(peewee.Model):
    key = peewee.CharField(index=True)
    value = peewee.CharField()

try:
    System.get()
except peewee.ProgrammingError:
    _init = True
else:
    _init = False

if _init:
    print('initing database')
    db.create_tables([Address, DAOs, Proposals, ProposalCommands, Votes, ERC20Trace, ERC721Trace, System])
    System.create(key='block', value='9280473')
    System.create(key='factory', value='0xCe1Fb1Fd381BdEf930aAc419d9fddaC4FD18840F')