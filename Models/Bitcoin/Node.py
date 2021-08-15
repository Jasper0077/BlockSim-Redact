from Models.Block import Block
from Models.Node import Node as BaseNode
from CH.ChameleonHash import PK, SK, p, q, g


class Node(BaseNode):
    def __init__(self, id, hashPower):
        '''Initialize a new miner named name with hashrate measured in hashes per second.'''
        super().__init__(id)  # ,blockchain,transactionsPool,blocks,balance)
        self.hashPower = hashPower
        self.blockchain = []  # create an array for each miner to store chain state locally
        self.transactionsPool = []
        self.blocks = 0  # total number of blocks mined in the main chain
        self.balance = 0  # to count all reward that a miner made, including block rewards + uncle rewards + transactions fees
        self.PK = PK
        self.SK = SK
        # self.p = p
        # self.q = q
        # self.g = g

print(PK, SK, g)
