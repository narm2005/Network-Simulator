
import random
import time
import os

from simulation.BroadcastPipe import BroadcastPipe

import simpy
import collections

from simulation.log.loghandle import loghandle


log = loghandle(__name__)


"""

author: Narmadha Palanisamy

Simulator Class

This class hold simulator and internal flow handlings functions

Upgrade cycle:
Check-in #1: AP should set its download_firmware flag to TRUE

Process #1: AP should “download” the firmware in a random amount of time from 0.00
to 5.00 minutes

Check-in #2: AP should set its download_complete flag to TRUE

Process #2: AP should “upgrade” its firmware in a random amount of time from 0.00 to
5.00 minutes

Check-in #3: AP should set its upgrade_complete flag to TRUE

AP rules:
    Each AP checks in at precise 5.00 minute intervals beginning from its check-in offset time. If an
    AP has not finished its download or upgrade within the 5 minute interval, it shall not proceed to
    the next check-in state and must wait for the next 5 minute check-in.
GW rules:
    Each GW must wait to begin its upgrade process until each of its RPs have set its
    download_complete state to TRUE.
RP rules:
    A RP can only check in if neither it nor its GW have begun Process #2 OR both the RP and its
    GW have completed Process #2.

Flow of data throgh following class


start() ->  general_flow() -> initial_checkin() -> download_firmware() -> second_checkin() -> upgrade() -> third_checkin()

"""

class Simulator:
    def __init__(self, env, params):
        self.env = env
        self.params = params      

        #initializing pipe for communication
        self.bc_pipe = BroadcastPipe(self.env)

        #Initializing Running Time
        self.gw_running_time =0
        self.rp_running_time =0

        # for dumping each process status and
        self.metrics = collections.defaultdict(list)
        

    def start(self):
        """
        Start the simulator.
        """
        log.info("Starting simulation")            
            
        log.info('%.2f Starting time'%self.env.now)
       # self.env.timeout(random.randint(0,5))


        for node in range(self.params.no_of_rp):
            offset = random.expovariate(2.0 / self.params.CHECKIN_INTERVAL)
            
            #self.env.process(self.general_flow('REPEATER%2d'%node,'RP',3.48))
            self.env.process(self.general_flow('REPEATER%2d'%node,'RP',offset))

        # Setting up  No of Gateway and Repeater
        for node in range(self.params.no_of_gw):
            offset = random.uniform(0, self.params.CHECKIN_INTERVAL)
            
            self.env.process(self.general_flow('GATEWAY%2d'%node,'GW',offset) )
            #self.env.process(self.general_flow('GATEWAY%2d'%node,'GW',1.52) )
            

        
        

    def general_flow(self,name,access_point,offset):

        # Initiate check in cycle

        checkin_cycle = 1
        """
        #Check-in #1: AP should set its download_firmware flag to TRUE
        #Process #1: AP should “download” the firmware in a random amount of time from 0.00
        to 5.00 minutes

        AP rules:
            Each AP checks in at precise 5.00 minute intervals beginning from its check-in offset time. If an
            AP has not finished its download or upgrade within the 5 minute interval, it shall not proceed to
            the next check-in state and must wait for the next 5 minute check-in
        """
        yield self.env.process(self.initial_checkin(name,access_point,offset,checkin_cycle))

        """
        #Starting Second Checkin
        #Check-in #2: AP should set its download_complete flag to TRUE


        """
        yield self.env.process(self.second_checkin(name,access_point,offset,checkin_cycle))
       
        
            
            

    def initial_checkin(self,name,access_point,offset,checkin_cycle):
        """

        A gateway (GW) and a repeater (RP) are both access points (AP). Each AP should have a randomized
        check-in time offset from 0.00 to 5.00 minutes (two digit precision).

        #Check-in #1: AP should set its download_firmware flag to TRUE

        # Initial Check in for any access point
        """
        
        log.info('%s Initial checkin started:  %.2f'%(name,self.env.now))
        
        yield self.env.timeout(offset)
        
        log.info('%s Initial checkin finished:  %.2f'%(name,self.env.now))

        """
        #Check-in #1: AP should set its download_firmware flag to TRUE


        """
        #log.info('%s says download_firmware set to TRUE at %.2f' % (name, self.env.now))
        flag='DOWNLOAD_FIRMWARE'
        self.set_flag_true(name,flag,'TRUE')
        
        #Initialze download firmware flow
        yield self.env.process(self.download_firmware(name,access_point))
        checkin_cycle +=1
        

        

    def download_firmware(self,name,ap):

        # Downloading firmware 
        """

        Process #1: AP should “download” the firmware in a random amount of time from 0.00
        to 5.00 minutes
        """

        flag='DOWNLOAD_COMPLETE'                       
        if ap == 'GW':
            # Getting Download time from param
            tout =self.params.GW_DOWNLOAD_TIME

            #log.info('%s :  %.2f'%(name,tout))  
            log.info('%s download started:  %.2f'%(name,self.env.now))
            yield self.env.timeout(tout)
            log.info('%s download finished: %.2f'%(name,self.env.now))
            # Setting Download_complete flag TRUE
            self.set_flag_true(name,flag,'TRUE')       
            #log.info('%s says download_complete set to TRUE at %.2f' % (name, self.env.now))
       
        else:

            # Getting Download time from param
            tout =self.params.RP_DOWNLOAD_TIME


              
            log.info('%s download started:  %.2f'%(name,self.env.now))
            yield self.env.timeout(tout)
            #log.info('%s says download_complete set to TRUE at %.2f' % (name, self.env.now))

            # Setting Download_complete flag TRUE
            self.set_flag_true(name,flag,'TRUE')
       
            out_pipe=self.bc_pipe.get_output_conn()
            """
            #Once download completed access point trying to set DOWNLOAD FIRMWARE setting to TRUE"
            #messaging on the pipe to set to true
            #msg = (self.env.now, '%s says download_complete set to TRUE at %.2f' % (name, self.env.now))
            #out_pipe.put(msg)
            """
            log.info('%s download finished: %.2f'%(name,self.env.now))
        

        

    def second_checkin(self,name,ap,offset,checkin_cycle):


        # Handing PIPE For communications
        
        if ap == 'GW':        
            
            sf=offset+self.params.CHECKIN_INTERVAL
            if sf < self.env.now:
                
                log.info('%s Second Checkin trying seems download is taking more time skipping:  %.2f'%(name,self.env.now))
                checkin_cycle += 1
                sf=offset+(self.params.CHECKIN_INTERVAL * checkin_cycle)        
                
            #log.info('%s Second Checkin started:  %.2f'%
                 # (name,self.env.now))
            wait = sf - self.env.now    
            yield self.env.timeout(wait)        
            log.info('%s Second Checkin finished:  %.2f'%
                  (name,self.env.now))

            


            #Receiving broadcast message that Repeater sends
            in_pipe=self.bc_pipe.get_output_conn()
            while True:
                # Handing PIPE For communications
                
                #wait for receive signal from REPEATER that its finished second Checkin
                # After that Gateway can start Upgrade process
                #log.info('%s says waiting for pipe at %.2f' % (name, self.env.now))
                msg = yield in_pipe.get()
                
                if msg[0] < self.env.now:
                    log.info('LATE Getting Message: at time %.2f: %s received message: %s' %
                          (self.env.now, name, msg[1]))
                else:
                    # message_consumer is synchronized with message_generator
                    log.info('at time %.2f: %s received message: %s.' %
                          (self.env.now, name, msg[1]))

                log.info('%s says UPGRADE Starting at %.2f' % (name, self.env.now))
                yield self.env.process(self.upgrade(name,ap,offset,checkin_cycle))
        
            
        else:

            # Handing PIPE For communications
            out_pipe=self.bc_pipe
            
            sf=offset+self.params.CHECKIN_INTERVAL

            if sf < self.env.now:
                
                log.info('%s Second Checkin trying seems download is taking more time skipping:  %.2f'%(name,self.env.now))
                checkin_cycle += 1
                sf=offset+(self.params.CHECKIN_INTERVAL * checkin_cycle )
                
                
            
            wait = sf - self.env.now
            log.info('%s Second Checkin started:  %.2f'%(name,self.env.now))           
            
            
            yield self.env.timeout(wait)
        
            log.info('%s Second Checkin finished:  %.2f'%(name,self.env.now))


            
            """
            # messages are time stamped to later check if the consumer was
            # late getting them.  Note, using event.triggered to do this may
            # result in failure due to FIFO nature of simulation yields.
            # (i.e. if at the same env.now, message_generator puts a message
            # in the pipe first and then message_consumer gets from pipe,
            # the event.triggered will be True in the other order it will be
            # False

            
            
            #Broadcasting message on the pipe to Gateway
            """
            
            msg = (self.env.now, '%s says second_checkin set to TRUE at %.2f' % (name, self.env.now))
            out_pipe.put(msg)

            """

            Starting UPGRADE cycle after REPEATER BROADCAST MESSAGE to GATEWAY
            """
            
            log.info('%s upgrade started:  %.2f'%(name,self.env.now))
            d=self.params.RP_UPGRADE_TIME
            yield self.env.timeout(d)
            log.info('%s upgrade finished: %.2f'%(name,self.env.now))

            #Updating Checkin Cycle
            checkin_cycle += 1


            """
            
            #Starting CHECKIN : 3

            """
            yield self.env.process(self.third_checkin(name,ap,offset,checkin_cycle))


          
   
    
        
    def upgrade(self,name,ap,offset,checkin_cycle):

        """

        Process #2: AP should “upgrade” its firmware in a random amount of time from 0.00 to
        5.00 minutes
        """
        
        if ap == 'GW':
            d=self.params.GW_UPGRADE_TIME
            log.info('%s upgrade started:  %.2f'%(name,self.env.now))
       

            yield self.env.timeout(d)
            log.info('%s upgrade finished: %.2f'%(name,self.env.now))
            # Updating Checkin Flag
            checkin_cycle += 1
            #Starting CHECKIN : 3
            yield self.env.process(self.third_checkin(name,ap,offset,checkin_cycle))        
        
        

        
        

        

    def third_checkin(self,name,ap,offset,checkin_cycle):

        """
        Check-in #3: AP should set its upgrade_complete flag to TRUE
        """
        
        sf=offset+(self.params.CHECKIN_INTERVAL * checkin_cycle)  
        flag='UPGRADE_COMPLETE'

        """

        If Check-in #3 passed the third interval. Skipping current cycle

        Each AP checks in at precise 5.00 minute intervals beginning from its check-in offset time. If an
        AP has not finished its download or upgrade within the 5 minute interval, it shall not proceed to
        the next check-in state and must wait for the next 5 minute check-in.

        """

        if sf < self.env.now:
                
                log.info('%s Third Checkin trying seems Upgrade is taking more time skipping:  %.2f'%(name,self.env.now))
                checkin_cycle += 1
                sf= offset+(self.params.CHECKIN_INTERVAL * checkin_cycle)
                


           
        try:
            wait = sf - self.env.now           
            log.info('%s Third Checkin started:  %.2f'%(name,self.env.now))
            yield self.env.timeout(wait)
            log.info('%s Third Checkin finished:  %.2f'%(name,self.env.now))

            # Setting upgrade_complete flag TRUE
            self.set_flag_true(name,flag,'TRUE')
       
        except:
            log.info("Runtime Error")
            log.info('%s Third Checkin Unable to complete:  %.2f'%(name,self.env.now))
            # Setting upgrade_complete flag TRUE
            self.set_flag_true(name,flag,'FALSE')
                             
                                   


        # For Calculating Total Running time   
        if ap == 'GW':
            self.gw_running_time=self.env.now
        else:
            self.rp_running_time=self.env.now



    def set_flag_true(self,name,flag,value):

        """

        EACH should set flag to TRUE when each check in finished.
        Check-in #1: AP should set its download_firmware flag to TRUE
        
        Check-in #2: AP should set its download_complete flag to TRUE
        Check-in #3: AP should set its upgrade_complete flag to TRUE
    
        """
        log.info('%s says %s set to %s at %.2f' % (name,flag,value,self.env.now))

        t=('%s:%s:%s:%2f'%(name,flag,value,self.env.now))
        
        self.metrics[name].append(t)
        #print(self.metrics[name])
        
