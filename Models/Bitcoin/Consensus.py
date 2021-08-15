import numpy as np
from InputsConfig import InputsConfig as p
from Models.Bitcoin.Node import Node
from Models.Consensus import Consensus as BaseConsensus
import random


class Consensus(BaseConsensus):
    """
	We modelled PoW consensus protocol by drawing the time it takes the miner to finish the PoW from an exponential distribution
        based on the invested hash power (computing power) fraction
    """

    def Protocol(miner):
        ##### Start solving a fresh PoW on top of last block appended #####
        TOTAL_HASHPOWER = sum([miner.hashPower for miner in p.NODES])
        hashPower = miner.hashPower / TOTAL_HASHPOWER
        return random.expovariate(hashPower * 1 / p.Binterval)

    """
	This method apply the longest-chain approach to resolve the forks that occur when nodes have multiple differeing copies of the blockchain ledger
    """

    def fork_resolution():
        BaseConsensus.global_chain = []  # reset the global chain before filling it

        a = []
        for i in p.NODES:
            # Add each node's chain
            a += [i.blockchain_length()]
        x = max(a)

        b = []
        z = 0
        for i in p.NODES:
            # Add to longest chain
            if i.blockchain_length() == x:
                b += [i.id]
                z = i.id

        # if there are multiple same length of longest chain, see which miner involve the most
        if len(b) > 1:
            c = []
            for i in p.NODES:
                if i.blockchain_length() == x:
                    c += [i.last_block().miner]
            z = np.bincount(c)
            z = np.argmax(z)

        for i in p.NODES:

            # if implementing in a centralised setting, the global chain is the ledger of the admin node
            if i.id == p.adminNode and p.hasMulti is False:
                for bc in range(len(i.blockchain)):
                    BaseConsensus.global_chain.append(i.blockchain[bc])
                break

            if i.blockchain_length() == x and i.last_block().miner == z:
                for bc in range(len(i.blockchain)):
                    BaseConsensus.global_chain.append(i.blockchain[bc])
                break
