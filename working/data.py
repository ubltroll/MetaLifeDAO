
import peewee

db = peewee.SqliteDatabase('test.db')

class BaseModel(peewee.Model):
    class Meta:
        database = db

class DAOs(BaseModel):
    address = peewee.CharField(primary_key=True)
    version = peewee.CharField()
    erc20_address = peewee.CharField(index=True, null=True)
    erc721_address = peewee.CharField(index=True, null=True)
    name = peewee.CharField(null=True)
    uri = peewee.CharField(null=True)
    info = peewee.CharField(null=True)
    proposalThreshold = peewee.CharField(null=True)
    votingPeriod = peewee.CharField(null=True)
    quorumFactorInBP = peewee.CharField(null=True)
    immutables = peewee.CharField(null=True)
    createBlock = peewee.IntegerField()
    lastUpdateBlock = peewee.IntegerField(null=True)

class Proposals(BaseModel):
    dao = peewee.ForeignKeyField(DAOs, backref = 'proposals')
    idInDAO = peewee.IntegerField(index = True)
    description = peewee.CharField()
    proposer = peewee.CharField()
    voteFor = peewee.CharField(default='0')
    voteAgainst = peewee.CharField(default='0')
    voteAbstain = peewee.CharField(default='0')
    quorum = peewee.CharField(default='0')
    createBlock = peewee.IntegerField()
    startBlock = peewee.IntegerField()
    endBlock   = peewee.IntegerField()
    lastUpdateBlock = peewee.IntegerField(null=True)

class ProposalCommands(BaseModel):
    proposal = peewee.ForeignKeyField(Proposals, backref = 'commands')
    index = peewee.IntegerField()
    target = peewee.CharField()
    value = peewee.CharField()
    data = peewee.CharField()
    createBlock = peewee.IntegerField()

class Votes(BaseModel):
    dao = peewee.ForeignKeyField(DAOs, backref = 'votes')
    proposal = peewee.ForeignKeyField(Proposals, backref = 'votes')
    voter = peewee.CharField(index=True)
    weight = peewee.CharField() #or token_id in Votes for NFT
    support = peewee.IntegerField()
    createBlock = peewee.IntegerField()

class ERC20Trace(BaseModel):
    dao = peewee.ForeignKeyField(DAOs, backref='erc20')
    holder = peewee.CharField(index = True, null=True)
    address = peewee.CharField(null=True)
    balance = peewee.CharField(default='0')
    lastUpdateBlock = peewee.IntegerField(null=True)

class Delegates(BaseModel):
    dao = peewee.ForeignKeyField(DAOs, backref='delegates')
    delegator = peewee.CharField(index = True)
    delegatee = peewee.CharField(index = True)
    lastUpdateBlock = peewee.IntegerField()

class ERC721Trace(BaseModel):
    dao = peewee.ForeignKeyField(DAOs, backref='erc721')
    holder = peewee.CharField(index = True,null=True)
    address = peewee.CharField(null=True)
    tokenId = peewee.IntegerField(index=True,null=True)
    lastUpdateBlock = peewee.IntegerField(null=True)

class ERC20(BaseModel):
    address = peewee.CharField(primary_key=True)
    name = peewee.CharField()
    symbol = peewee.CharField()
    decimals = peewee.IntegerField()

class ERC20TraceForDAO(BaseModel):
    dao = peewee.ForeignKeyField(DAOs, backref='trace')
    from_ = peewee.CharField()
    to_ = peewee.CharField()
    token_address = peewee.ForeignKeyField(ERC20, backref='trace')
    amount = peewee.CharField()
    lastUpdateBlock = peewee.IntegerField()

class System(BaseModel):
    key = peewee.CharField(index=True)
    value = peewee.CharField()

try:
    System.get()
except peewee.OperationalError:
    _init = True
else:
    _init = False

if _init:
    print('initing database')
    db.create_tables([DAOs, Votes, ERC20Trace, ERC721Trace, Delegates, System, ERC20, ERC20TraceForDAO,
        Proposals, ProposalCommands])
    System.create(key='block', value='9289940')
    System.create(key='factory', value='0x84E72653155044a35FAd77FAFa122773Be28ad53')
