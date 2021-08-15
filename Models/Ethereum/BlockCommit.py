import hashlib
import json
import random
import time
import CH.ChameleonHash as ch
import CH.SecretSharing as ss

from CH.ChameleonHash import q, g, SK, PK, KeyGen, forge, forgeSplit, chameleonHash, chameleonHashSplit
from Scheduler import Scheduler
from InputsConfig import InputsConfig as p
from Models.Ethereum.Node import Node
from Statistics import Statistics
from Models.Ethereum.Transaction import LightTransaction as LT, FullTransaction as FT
from Models.Network import Network
from Models.Ethereum.Consensus import Consensus as c
from Models.BlockCommit import BlockCommit as BaseBlockCommit

SKlist = []
PKlist = []
# rlist = []


class BlockCommit(BaseBlockCommit):

    # Handling and running Events
    def handle_event(event):
        if event.type == "create_block":
            BlockCommit.generate_block(event)
        elif event.type == "receive_block":
            BlockCommit.receive_block(event)

    # Block Creation Event
    def generate_block(event):
        miner = p.NODES[event.block.miner]
        minerId = miner.id
        eventTime = event.time
        blockPrev = event.block.previous

        if blockPrev == miner.last_block().id:
            Statistics.totalBlocks += 1  # count # of total blocks created!
            if p.hasTrans:
                if p.Ttechnique == "Light":
                    blockTrans, blockSize = LT.execute_transactions()
                elif p.Ttechnique == "Full":
                    blockTrans, blockSize = FT.execute_transactions(miner, eventTime)

                event.block.transactions = blockTrans
                event.block.usedgas = blockSize
                if p.hasRedact:
                    event.block.r = random.randint(1, q)

                    # hash the transactions and previous hash value
                    x = json.dumps([[i.id for i in event.block.transactions], event.block.previous],
                                   sort_keys=True).encode()
                    print(x)
                    m = hashlib.sha256(x).hexdigest()
                    # if p.hasMulti:
                    #     event.block.r = ch.getr(len(p.NODES), q)
                    #     event.block.id = chameleonHashSplit(PKlist, miner.g, m, event.block.r, len(p.NODES))
                    # else:
                    event.block.id = chameleonHash(miner.PK, m, event.block.r)

            if p.hasUncles:
                BlockCommit.update_unclechain(miner)
                blockUncles = Node.add_uncles(miner)  # add uncles to the block
                event.block.uncles = blockUncles  # (only when uncles activated)

            miner.blockchain.append(event.block)

            if p.hasTrans and p.Ttechnique == "Light":
                LT.create_transactions()  # generate transactions
            BlockCommit.propagate_block(event.block)
            BlockCommit.generate_next_block(miner, eventTime)  # Start mining or working on the next block

    # Block Receiving Event
    def receive_block(event):

        miner = p.NODES[event.block.miner]
        minerId = miner.id
        currentTime = event.time
        blockPrev = event.block.previous  # previous block id

        node = p.NODES[event.node]  # recipint
        lastBlockId = node.last_block().id  # the id of last block

        #### case 1: the received block is built on top of the last block according to the recipient's blockchain ####
        if blockPrev == lastBlockId:
            node.blockchain.append(event.block)  # append the block to local blockchain

            if p.hasTrans and p.Ttechnique == "Full":
                BaseBlockCommit.update_transactionsPool(node, event.block)

            BlockCommit.generate_next_block(node, currentTime)  # Start mining or working on the next block

        #### case 2: the received block is  not built on top of the last block ####
        else:
            depth = event.block.depth + 1
            if (depth > len(node.blockchain)):
                BlockCommit.update_local_blockchain(node, miner, depth)
                BlockCommit.generate_next_block(node, currentTime)  # Start mining or working on the next block

            #### 2- if depth of the received block <= depth of the last block, then reject the block (add it to unclechain) ####
            else:
                uncle = event.block
                node.unclechain.append(uncle)

            if p.hasUncles:
                BlockCommit.update_unclechain(node)
            if p.hasTrans and p.Ttechnique == "Full":
                BaseBlockCommit.update_transactionsPool(node,
                                                        event.block)  # not sure yet.

    # Upon generating or receiving a block, the miner start working on the next block as in POW
    def generate_next_block(node, currentTime):
        if node.hashPower > 0:
            blockTime = currentTime + c.Protocol(node)  # time when miner x generate the next block
            print(f"Block Time: {blockTime}")
            Scheduler.create_block_event(node, blockTime)

    def generate_initial_events():
        currentTime = 0
        for node in p.NODES:
            BlockCommit.generate_next_block(node, currentTime)

    def propagate_block(block):
        for recipient in p.NODES:
            if recipient.id != block.miner:
                blockDelay = Network.block_prop_delay()  # draw block propagation delay from a distribution !! or you can assign 0 to ignore block propagation delay
                Scheduler.receive_block_event(recipient, block, blockDelay)

    def setupSecretSharing():
        print(ch.p, q, g)
        global SKlist, PKlist, rlist
        SKlist, PKlist = KeyGen(ch.p, q, g, len(p.NODES))
        rlist = ch.getr(len(p.NODES), q)
        for i, node in enumerate(p.NODES):
            node.PK = PKlist[i]
            node.SK = SKlist[i]

    def generate_redaction_event(redactRuns):
        i = 0
        miner_list = [node for node in p.NODES if node.hashPower > 0]
        while i < redactRuns:
            if p.hasMulti:
                miner = random.choice(miner_list)
            else:
                miner = p.NODES[p.adminNode]
            r = random.randint(1, 2)
            block_index = random.randint(1, len(miner.blockchain)-1)
            tx_index = random.randint(1, len(miner.blockchain[block_index].transactions)-1)
            if r == 1:
                BlockCommit.redact_tx(miner, block_index, tx_index)
            else:
                BlockCommit.delete_tx(miner, block_index, tx_index)
            i += 1
            print(f'i: {i}')

    def delete_tx(miner, i, tx_i):
        t1 = time.time()
        block = miner.blockchain[i]
        # Store the old block data
        x1 = json.dumps([[i.id for i in block.transactions], block.previous], sort_keys=True).encode()
        print(x1)
        m1 = hashlib.sha256(x1).hexdigest()
        # remove the tx which wanted to be deleted
        print(block.depth, block.id, block.previous, len(block.transactions))

        # record the block index and deleted transaction object, miner reward  = 0 and performance time = 0
        # and also the blockchain size, number of transaction of that action block
        miner.redacted_tx.append([i, block.transactions.pop(tx_i), 0, 0, miner.blockchain_length(), len(block.transactions)])

        # Store the modified block data
        x2 = json.dumps([[i.id for i in block.transactions], block.previous], sort_keys=True).encode()
        print(x2)
        m2 = hashlib.sha256(x2).hexdigest()
        if p.hasMulti:
            # rlist = block.r
            # print(f'rlist_temp: {rlist}')
            # print(f'block id: {block.id}')
            miner_list = [miner for miner in p.NODES if miner.hashPower > 0]
            # propagation delay in sharing secret key
            time.sleep(0.005)
            ss.secret_share(SK, minimum=len(miner_list), shares=len(p.NODES))
            r2 = forge(SK, m1, block.r, m2)
            # rlist[miner.id] = r2
            # print(f'rlist_temp: {rlist}')
            id2 = chameleonHash(PK, m2, r2)
            # print(f'block new id: {id2}')
            block.r = r2
            for node in p.NODES:
                if node.id != miner.id:
                    if node.blockchain[i]:
                        node.blockchain[i].transactions = block.transactions
                        node.blockchain[i].r = block.r
        else:
            r2 = forge(SK, m1, block.r, m2)
            id2 = chameleonHash(PK, m2, r2)
            block.r = r2
        # Calculate the performance time per operation
        t2 = time.time()
        t = (t2 - t1) * 1000 # in ms
        block.id = id2
        # redact operation is more expensive than mining
        reward = random.expovariate(1 / p.Rreward)
        miner.balance += reward
        miner.redacted_tx[-1][2] = reward
        miner.redacted_tx[-1][3] = t
        print(block.depth, block.id, block.previous, len(block.transactions))
        return miner

    def redact_tx(miner, i, tx_i):
        t1 = time.time()
        block = miner.blockchain[i]
        # Store the old block data
        x1 = json.dumps([[i.id for i in block.transactions], block.previous], sort_keys=True).encode()
        print(x1)
        m1 = hashlib.sha256(x1).hexdigest()
        # remove the tx which wanted to be deleted
        print(block.depth, block.id, block.previous, len(block.transactions))

        # change the tx fee with locating the gas price and used gas
        block.transactions[tx_i].usedGas = random.expovariate(1 / block.transactions[tx_i].usedGas)
        block.transactions[tx_i].gasPrice = random.expovariate(1 / block.transactions[tx_i].gasPrice)
        block.transactions[tx_i].fee = block.transactions[tx_i].usedGas * block.transactions[tx_i].gasPrice
        # recompute the transaction id
        block.transactions[tx_i].id = random.randrange(100000000000)
        # record the block depth, redacted transaction, miner reward = 0 and performance time = 0
        miner.redacted_tx.append([i, block.transactions[tx_i], 0, 0, miner.blockchain_length(), len(block.transactions)])
        # Store the modified block data
        x2 = json.dumps([[i.id for i in block.transactions], block.previous], sort_keys=True).encode()
        print(x2)
        m2 = hashlib.sha256(x2).hexdigest()
        # Forge new r
        if p.hasMulti:
            # rlist = block.r
            # print(f'rlist_temp: {rlist}')
            # print(f'block id: {block.id}')
            miner_list = [miner for miner in p.NODES if miner.hashPower > 0]
            # propagation delay in sharing secret
            time.sleep(0.005)
            ss.secret_share(SK, minimum=len(miner_list), shares=len(p.NODES))
            r2 = forge(SK, m1, block.r, m2)
            # rlist[miner.id] = r2
            # print(f'rlist_temp: {rlist}')
            id2 = chameleonHash(PK, m2, r2)
            # print(f'block new id: {id2}')
            block.r = r2
            for node in p.NODES:
                if node.id != miner.id:
                    if node.blockchain[i]:
                        node.blockchain[i].transactions = block.transactions
                        node.blockchain[i].r = block.r
        else:
            r2 = forge(SK, m1, block.r, m2)
            id2 = chameleonHash(PK, m2, r2)
            block.r = r2
        # Calculate the performance time per operation
        t2 = time.time()
        block.id = id2
        t = (t2 - t1) * 1000 # in ms
        # redact operation is more expensive than mining
        reward = random.expovariate(1 / p.Rreward)
        miner.balance += reward
        miner.redacted_tx[-1][2] = reward
        miner.redacted_tx[-1][3] = t
        print(block.depth, block.id, block.previous, len(block.transactions))
        return miner

    def update_local_blockchain(node, miner, depth):
        # the node here is the one that needs to update its blockchain, while miner here is the one who owns the last block generated
        # the node will update its blockchain to mach the miner's blockchain
        from InputsConfig import InputsConfig as p
        i = 0
        while i < depth:
            if i < len(node.blockchain):
                if (node.blockchain[i].id != miner.blockchain[
                    i].id):  # and (self.node.blockchain[i-1].id == Miner.blockchain[i].previous) and (i>=1):
                    node.unclechain.append(node.blockchain[i])  # move block to unclechain
                    newBlock = miner.blockchain[i]
                    node.blockchain[i] = newBlock
                    if p.hasTrans and p.Ttechnique == "Full":
                        BaseBlockCommit.update_transactionsPool(node, newBlock)
            else:
                newBlock = miner.blockchain[i]
                node.blockchain.append(newBlock)
                if p.hasTrans and p.Ttechnique == "Full":
                    BaseBlockCommit.update_transactionsPool(node, newBlock)
            i += 1

    # Upon receiving a block, update local unclechain to remove all uncles included in the received block
    def update_unclechain(node):
        ### remove all duplicates uncles in the miner's unclechain
        a = set()
        x = 0
        while x < len(node.unclechain):
            if node.unclechain[x].id in a:
                del node.unclechain[x]
                x -= 1
            else:
                a.add(node.unclechain[x].id)
            x += 1

        j = 0
        while j < len(node.unclechain):
            for k in node.blockchain:
                if node.unclechain[j].id == k.id:
                    del node.unclechain[j]  # delete uncle after inclusion
                    j -= 1
                    break
            j += 1

        j = 0
        while j < len(node.unclechain):
            c = "t"
            for k in node.blockchain:
                u = 0
                while u < len(k.uncles):
                    if node.unclechain[j].id == k.uncles[u].id:
                        del node.unclechain[j]  # delete uncle after inclusion
                        j -= 1
                        c = "f"
                        break
                    u += 1
                if c == "f":
                    break
            j += 1
