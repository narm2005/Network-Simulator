import logging
import time
import os
import argparse

import simpy
import random
import numpy



from simulation.simulator import Simulator
from simulation.simulatorparams import SimulatorParams
from simulation.log.loghandle import loghandle



log = loghandle(__name__)


def main():
    args = parse_args()
    start_time = time.time()
    total_running_time=0

    #Log_handling
    
    # Seed the random generator
    random.seed(args.seed)
    numpy.random.seed(args.seed)

    params=SimulatorParams(args.seed,args.no_of_gw,args.no_of_rp,args.duration,args.checkin_interval)

    for no_of_run in range(args.total_runs):

        # Create a SimPy environment
        env = simpy.Environment()

        # Create a Simulator object, pass the SimPy environment and params objects
        simulator = Simulator(env, params)

        # Start the simulation
        simulator.start()

        # Run the simpy environment for the specified duration
        env.run(until=args.duration)

        # Record endtime and running_time metrics
        end_time = time.time()
        if simulator.gw_running_time > simulator.rp_running_time :
            running_time=simulator.gw_running_time
        else:
            running_time=simulator.rp_running_time

        #Dumping metrics
        #log.info(simulator.metrics)
             
        
        log.info("SIMULATION CYCLE :%d Total upgrade time :%.2f"%(no_of_run,running_time))
        total_running_time +=running_time

    #Calculating average running time
    average_running_time=total_running_time / args.total_runs
    
    log.info("Average simulation running time for %d runs :(foreach run %d Gateway & %d Repeater) :%.2f"%
             (args.total_runs,args.no_of_gw,args.no_of_rp,average_running_time))    

# parse CLI args (when using simulator as stand-alone)
def parse_args():
    parser = argparse.ArgumentParser(description="Network-Simulation tool")
    parser.add_argument('-d', '--duration', required=True, dest="duration", type=int,
                        help="The duration of the simulation (simulates milliseconds).")
    parser.add_argument('-s', '--seed', required=True, default=random.randint(0, 9999), dest='seed', type=int,
                        help="Random seed")

    parser.add_argument('-g', '--no of Gateways', required=True, default=random.randint(0,10), dest='no_of_gw', type=int,
                        help="No Of Gateway available in the network")

    parser.add_argument('-r', '--no of Repeater', required=True, default=random.randint(0,5), dest='no_of_rp', type=int,
                        help="No Of Repeater available in the network")
    parser.add_argument('-i', '--interval', required=True, default=random.randint(0, 10), dest='checkin_interval', type=int,
                        help="check in mark")

    parser.add_argument('-n', '--No of Runs', required=False, default=1, dest='total_runs', type=int,
                        help="NO Of Runs")

    
    return parser.parse_args()

   



if __name__ == '__main__':
    main()


