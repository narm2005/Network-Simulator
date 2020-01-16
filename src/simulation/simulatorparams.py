

"""
author: Narmadha Palanisamy


Simulator parameters.
- Allows for clean and quick access to parameters from the flow simulator.
- Facilitates the quick changing of schedule decisions and
other parameters for the simulator.

"""




class SimulatorParams:    
        def __init__(self,seed,no_of_gw,no_of_rp,run_duration,checkin_interval):              
            
            ## Seed for the random generator: int
            self.RANDOM_SEED = seed


            # A gateway (GW) and a repeater (RP) are both access points (AP).
            #Each AP should have a randomized check-in time offset from 0.00 to 5.00 minutes (two digit precision).
            self.CHECKIN_INTERVAL = checkin_interval #

            # Dummy Data Gateway OFFSET value
            self.GW_OFFSET = 1.52

            # Dummy Data Repeater OFFSET value
            self.RP_OFFSET = 3.48

            # Dummy Data Gateway Download value
            self.GW_DOWNLOAD_TIME = 3.27

            # Dummy Data Repeater Download value
            self.GW_UPGRADE_TIME = 4.11

            # Dummy Data Gateway Upgrade time value
            self.RP_DOWNLOAD_TIME = 2.28

            # Dummy Data Gateway Upgrade time value
            self.RP_UPGRADE_TIME = 1.23

            # Dummy Data Gateway no of gateway in network simulator

            self.no_of_gw = no_of_gw

            # Dummy Data Gateway no of Repeater in network simulator
            self.no_of_rp = no_of_rp

            self.run_duration = run_duration
