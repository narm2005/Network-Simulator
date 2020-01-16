import logging





def loghandle(name):
    log = logging.getLogger(name)
     # logging Handling
    logging.basicConfig(level=logging.INFO)
    fh = logging.FileHandler('sim.log')
    fh.setLevel(logging.DEBUG)
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.ERROR)
    log.addHandler(ch)
    log.addHandler(fh)

    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    fh.setFormatter(formatter)
    return log
