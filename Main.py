from InputsConfig import InputsConfig as p
from Event import Event, Queue
from Scheduler import Scheduler
from Statistics import Statistics
import time

if p.model == 3:
    from Models.AppendableBlock.BlockCommit import BlockCommit
    from Models.Consensus import Consensus
    from Models.AppendableBlock.Transaction import FullTransaction as FT
    from Models.AppendableBlock.Node import Node
    from Models.Incentives import Incentives
    from Models.AppendableBlock.Statistics import Statistics
    from Models.AppendableBlock.Verification import Verification

elif p.model == 2:
    from Models.Ethereum.BlockCommit import BlockCommit
    from Models.Ethereum.Consensus import Consensus
    from Models.Ethereum.Transaction import LightTransaction as LT, FullTransaction as FT
    from Models.Ethereum.Node import Node
    from Models.Ethereum.Incentives import Incentives

elif p.model == 1:
    from Models.Bitcoin.BlockCommit import BlockCommit
    from Models.Bitcoin.Consensus import Consensus
    from Models.Transaction import LightTransaction as LT, FullTransaction as FT
    from Models.Bitcoin.Node import Node
    from Models.Incentives import Incentives

elif p.model == 0:
    from Models.BlockCommit import BlockCommit
    from Models.Consensus import Consensus
    from Models.Transaction import LightTransaction as LT, FullTransaction as FT
    from Models.Node import Node
    from Models.Incentives import Incentives

########################################################## Start Simulation ##############################################################


def main():
    print("test")
    for i in range(p.Runs):
        t1 = time.time()
        clock = 0  # set clock to 0 at the start of the simulation
        if p.hasTrans:
            if p.Ttechnique == "Light":
                LT.create_transactions()  # generate pending transactions
            elif p.Ttechnique == "Full":
                FT.create_transactions()  # generate pending transactions
        print('Finish create tx, start operation')

        # if has multiplayer in the secret sharing
        # if p.hasMulti:
        #     BlockCommit.setupSecretSharing()
        #     for i in p.NODES:
        #         print(f'NODE {i.id}: Public Key: {i.PK}, Secret Key: {i.SK}')


        Node.generate_genesis_block()  # generate the genesis block for all miners
        # initiate initial events >= 1 to start with
        BlockCommit.generate_initial_events()

        while not Queue.isEmpty() and clock <= p.simTime:
            print(Queue.event_list[-1].type, Queue.event_list[-1].node)
            next_event = Queue.get_next_event()
            clock = next_event.time  # move clock to the time of the event
            BlockCommit.handle_event(next_event)
            Queue.remove_event(next_event)
            for n in range(len(p.NODES)):
                print(len(p.NODES[n].blockchain))

        # test for chameleon hash forging
        if p.hasRedact:
            Consensus.fork_resolution()
            Statistics.original_global_chain()
            BlockCommit.generate_redaction_event(p.redactRuns)

        # for the AppendableBlock process transactions and
        # optionally verify the model implementation
        if p.model == 3:
            BlockCommit.process_gateway_transaction_pools()

            if i == 0 and p.VerifyImplemetation:
                Verification.perform_checks()

        Consensus.fork_resolution()  # apply the longest chain to resolve the forks
        # distribute the rewards between the participating nodes
        Incentives.distribute_rewards()
        # print the global chain
        t2 = time.time()
        t = t2 -t1


        # calculate the simulation results (e.g., block statistics and miners' rewards)
        Statistics.calculate(t)
        print(Statistics.redactResults)

        if p.model == 3:
            Statistics.print_to_excel(i, True)
            Statistics.reset()
        else:
            ########## reset all global variable before the next run #############
            Statistics.reset()  # reset all variables used to calculate the results
            Node.resetState()  # reset all the states (blockchains) for all nodes in the network
            fname = "{0}M_{1}_{2}K.xlsx".format(
                p.Bsize/1000000, p.Tn/1000, p.Tsize)
            # print all the simulation results in an excel file
            Statistics.print_to_excel(fname)
            Statistics.reset2()  # reset profit results
        # p.simTime += 200
        # p.redactRuns += 1

######################################################## Run Main method #####################################################################
if __name__ == '__main__':
    main()
