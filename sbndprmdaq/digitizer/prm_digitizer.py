'''
Contains an overall digitizer control class
'''
import logging

from sbndprmdaq.digitizer.digitizer_base import DigitizerBase
try:
    import sbndprmdaq.digitizer.atsapi as ats
except:
    pass
from sbndprmdaq.digitizer.ats310 import ATS310
from sbndprmdaq.digitizer.adpro_control import ADProControl

class PrMDigitizer(DigitizerBase):
    '''
    This class manages all the PrM digitizers
    '''

    def __init__(self, config=None):
        '''
        Contructor.

        Args:
            config (dict): The configuration dictionary.
        '''

        self._logger = logging.getLogger(__name__)
        self._digitizers = {}

        print('prm_id_to_ats_systemid', config['prm_id_to_ats_systemid'])
        print('prm_id_to_adpro_channels', config['prm_id_to_adpro_channels'])
        print('prm_id_to_digitizer_type', config['prm_id_to_digitizer_type'])

        self._bounded_prms = {}

        # Loop over all PrM IDs to digitzer type
        for prm_id, digitizer_type in config['prm_id_to_digitizer_type'].items():
            self._logger.info(f"Setting up PrM {prm_id} with digitizer {digitizer_type}.")

            if prm_id in config['bound_prms']:
                self._logger.info(f"PrM {prm_id} is controlled and digitized via PrM {config['bound_prms'][prm_id]}.")
                self._bounded_prms[prm_id] = config['bound_prms'][prm_id]
                continue

            if digitizer_type == 'adpro':
                digitizer = self._get_adpro_digitizer(prm_id, config) #channels=config['prm_id_to_adpro_channels'][prm_id])
            elif digitizer_type == 'ats310':
                digitizer = self._get_ats310_digitizer(systemid=config['prm_id_to_ats_systemid'][prm_id])
            else:
                self._logger.critical('Digitizer option not recognized: {digitizer_type}.')
                digitizer = None

            if digitizer is None:
                if self._window is not None:
                    self._window.missing_digitizer(prm_id)
                    self._digitizers[prm_id] = None
                continue

            self._digitizers[prm_id] = digitizer

    def _get_adpro_digitizer(self, prm_id, config):
        '''
        Returns an ADProControl Digitzer. Right now, we assume this is
        only returned once, since multiple ADPro digitizers are not supported.

        Args:
            prm_ids (list): unused
            config (dict): The configuration dictionary.
        '''
        return ADProControl(prm_ids=None, config=config)

    def _get_ats310_digitizer(self, systemid):
        '''
        Returns an ATS310 Digitzer object. There are multiple
        ATS310 boards in the server, and the systemid allows us to
        select the board.

        Args:
            systemid (int): The digiter ID to use
        '''

        ats310 = None

        n_systems = ats.numOfSystems()
        n_boards = ats.boardsFound()

        self._logger.info(f'Number of ATS systems: {n_systems}.')
        self._logger.info(f'Number of ATS boards: {n_boards}.')

        # Check that we have an available digitizer for this systemid
        n_boards = ats.boardsInSystemBySystemID(systemid)
        if n_boards == 1:
            ats310 = ATS310(systemId=systemid, boardId=1)

        return ats310

    def n_digitizers(self):
        return len(self._digitizers)

    def _process_prm_id(self, prm_id):
        '''
        Given a real PrM ID, returns the actual PrM ID to use.
        For ex, if we pass prm_id=2 and PrM 2 is bounded to PrM 1,
        this will return prm_id=1

        Args:
            prm_id (int): The PrM ID to process

        Returns:
            int: the processed PrM ID 
        '''
        if prm_id in self._digitizers:
            return prm_id

        if prm_id in self._bounded_prms:
            if self._bounded_prms[prm_id] in self._digitizers:
                # self._logger.info(f'Asked for prm_id {prm_id}. Returning digitizer for prm_id {self._bounded_prms[prm_id]}')
                return self._bounded_prms[prm_id]

        self._logger.error(f'PrM {prm_id} not available.')
        raise Exception()

    def busy(self, prm_id=1):

        prm_id = self._process_prm_id(prm_id)
        return self._digitizers[prm_id].busy()


    def get_trigger_sample(self, prm_id=1):

        prm_id = self._process_prm_id(prm_id)
        return self._digitizers[prm_id].get_trigger_sample()


    def get_samples_per_second(self, prm_id=1):

        prm_id = self._process_prm_id(prm_id)
        return self._digitizers[prm_id].get_samples_per_second()

    def set_samples_per_second(self, n, prm_id=1):

        prm_id = self._process_prm_id(prm_id)
        return self._digitizers[prm_id].set_samples_per_second(n)

    def get_number_acquisitions(self, prm_id=1):

        prm_id = self._process_prm_id(prm_id)
        return self._digitizers[prm_id].get_number_acquisitions()

    def set_number_acquisitions(self, n, prm_id=1):

        prm_id = self._process_prm_id(prm_id)
        return self._digitizers[prm_id].set_number_acquisitions(n)

    def get_pre_trigger_samples(self, prm_id=1):

        prm_id = self._process_prm_id(prm_id)
        return self._digitizers[prm_id].get_pre_trigger_samples()

    def get_post_trigger_samples(self, prm_id=1):

        prm_id = self._process_prm_id(prm_id)
        return self._digitizers[prm_id].get_post_trigger_samples()

    def get_input_range_volts(self, prm_id=1):

        prm_id = self._process_prm_id(prm_id)
        return self._digitizers[prm_id].get_input_range_volts()

    def start_capture(self, prm_id=1):

        prm_id = self._process_prm_id(prm_id)
        return self._digitizers[prm_id].start_capture()

    def check_capture(self, prm_id=1):

        prm_id = self._process_prm_id(prm_id)
        return self._digitizers[prm_id].check_capture()


    def get_data(self, prm_id=1):

        prm_id = self._process_prm_id(prm_id)
        return self._digitizers[prm_id].get_data()


    def lamp_on(self, prm_id=1):

        prm_id = self._process_prm_id(prm_id)
        return self._digitizers[prm_id].lamp_on()

    def lamp_off(self, prm_id=1):

        prm_id = self._process_prm_id(prm_id)
        return self._digitizers[prm_id].lamp_off()

    def lamp_frequency(self, freq, prm_id=1):
        '''
        prm_id PrM ID
        freq Lamp frequency in Hz
        '''

        prm_id = self._process_prm_id(prm_id)
        return self._digitizers[prm_id].lamp_frequency(freq)
