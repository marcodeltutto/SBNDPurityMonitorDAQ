import sys
import logging

def get_logging(filename):
    '''
    Returns a logging properly setup to use.
    '''
    logging.basicConfig(filename=filename,
                        filemode='w',
                        level=logging.INFO,
                        format='%(asctime)s %(levelname)-8s %(message)s')

    # Remove the qdarkstyle logger, not needed
    logging.getLogger('qdarkstyle').propagate = False

    # Change formatting for stream handler
    # formatter = logging.Formatter("%(asctime)s;%(levelname)s;%(message)s")
    # sh = logging.StreamHandler()
    # sh.setFormatter(formatter)
    # logging.getLogger().addHandler(sh)
    logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))


    return logging