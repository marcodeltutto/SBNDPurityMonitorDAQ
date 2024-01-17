'''
Contains a class to store PrM configuration
'''
from PyQt5 import QtWidgets

#pylint: disable=invalid-name,too-many-instance-attributes
class Form(QtWidgets.QDialog):
    '''
    A form to store PrM configuration
    '''

    def __init__(self, parent=None):
        '''
        Contructor

        Args:
            parent (QtWidgets): the parent widget
        '''
        super().__init__(parent)

        # setting window title
        self.setWindowTitle("Purity Monitor Configuration")

        # setting geometry to the window
        self.setGeometry(100, 100, 300, 400)

        self._tabs = [QtWidgets.QWidget(), QtWidgets.QWidget(), QtWidgets.QWidget()]

        self._tabwidget = QtWidgets.QTabWidget()

        for i, tab in enumerate(self._tabs):
            self._tabwidget.addTab(tab, f"PrM {i+1}")


        self.setup()
        self.create_form(prm_id=1)
        self.create_form(prm_id=2)
        self.create_form(prm_id=3)

        self.create_buttons()



        # creating a vertical layout
        mainLayout = QtWidgets.QVBoxLayout()

        # adding form group box to the layout
        mainLayout.addWidget(self._tabwidget)

        # adding button box to the layout
        mainLayout.addWidget(self.buttonBox)

        # setting lay out
        self.setLayout(mainLayout)

        self._output = [{}, {}, {}]


    def get_info(self, prm_id=1):
        '''
        Get info method called when form is accepted
        '''

        prm = prm_id - 1

        self._output[prm] = {
            'location': self._location[prm].currentText(),
            'vessel': self._vessel[prm].currentText(),
            'medium': self._medium[prm].currentText(),
            'pressure': self._pressure[prm].text(),
            'photocathode': self._photocathode[prm].text(),
            'fibers': self._fibers[prm].text(),
            'n_fibers': self._n_fibers[prm].text(),
            'optical_ft': self._optical_ft[prm].text(),
            'hv_ft': self._hv_ft[prm].text(),
            'hv_warm_cables': self._hv_warm_cables[prm].text(),

            'flash_lamp': self._flash_lamp[prm].text(),
            'flash_lamp_energy': self._flash_lamp_energy[prm].text(),
            'flash_lamp_frequency': self._flash_lamp_frequency[prm].text(),
            'flash_lamp_settings': self._flash_lamp_settings[prm].currentText(),
            'flash_lamp_trigger': self._flash_lamp_trigger[prm].text(),

            'pm_elec': self._pm_elec[prm].currentText(),
            'pm_elec_cha': self._pm_elec_cha[prm].currentText(),
            'pm_elec_chc': self._pm_elec_chc[prm].currentText(),
            'pm_elec_out_ch1': self._pm_elec_out_ch1[prm].currentText(),
            'pm_elec_out_ch2': self._pm_elec_out_ch2[prm].currentText(),

            'nim_bin': self._nim_bin[prm].text(),
            'nim_bin_pwr_supp': self._nim_bin_pwr_supp[prm].text(),

            'hv_crate': self._hv_crate[prm].currentText(),
        }

        # closing the window
        self.close()

    def get_values(self, prm_id=None):
        '''
        Returns the values of the form
        '''

        if prm_id is None:
            return self._output

        return self._output[prm_id-1]


    def create_buttons(self):
        '''
        Creates the buttons in the form
        '''

        # creating a dialog button for ok and cancel
        self.buttonBox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)

        # adding action when form is accepted
        self.buttonBox.accepted.connect(self.get_info)

        # adding action when form is rejected
        self.buttonBox.rejected.connect(self.reject)

    def setup(self):
        '''
        Sets up theform
        '''

        # self._form_layouts = [QtWidgets.QFormLayout()] * 3

        self._location = [QtWidgets.QComboBox(), QtWidgets.QComboBox(), QtWidgets.QComboBox()]
        self._vessel = [QtWidgets.QComboBox(), QtWidgets.QComboBox(), QtWidgets.QComboBox()]
        self._medium = [QtWidgets.QComboBox(), QtWidgets.QComboBox(), QtWidgets.QComboBox()]
        self._pressure = [QtWidgets.QLineEdit(), QtWidgets.QLineEdit(), QtWidgets.QLineEdit()]

        self._photocathode = [QtWidgets.QLineEdit(), QtWidgets.QLineEdit(), QtWidgets.QLineEdit()]
        self._fibers = [QtWidgets.QLineEdit(), QtWidgets.QLineEdit(), QtWidgets.QLineEdit()]
        self._n_fibers = [QtWidgets.QSpinBox(), QtWidgets.QSpinBox(), QtWidgets.QSpinBox()]

        self._optical_ft = [QtWidgets.QLineEdit(), QtWidgets.QLineEdit(), QtWidgets.QLineEdit()]
        self._hv_ft = [QtWidgets.QLineEdit(), QtWidgets.QLineEdit(), QtWidgets.QLineEdit()]
        self._hv_warm_cables = [QtWidgets.QLineEdit(), QtWidgets.QLineEdit(), QtWidgets.QLineEdit()]

        self._flash_lamp = [QtWidgets.QLineEdit(), QtWidgets.QLineEdit(), QtWidgets.QLineEdit()]
        self._flash_lamp_energy = [QtWidgets.QLineEdit(), QtWidgets.QLineEdit(), QtWidgets.QLineEdit()]
        self._flash_lamp_frequency = [QtWidgets.QLineEdit(), QtWidgets.QLineEdit(), QtWidgets.QLineEdit()]
        self._flash_lamp_settings = [QtWidgets.QComboBox(), QtWidgets.QComboBox(), QtWidgets.QComboBox()]
        self._flash_lamp_trigger = [QtWidgets.QLineEdit(), QtWidgets.QLineEdit(), QtWidgets.QLineEdit()]

        self._pm_elec = [QtWidgets.QComboBox(), QtWidgets.QComboBox(), QtWidgets.QComboBox()]
        self._pm_elec_cha = [QtWidgets.QComboBox(), QtWidgets.QComboBox(), QtWidgets.QComboBox()]
        self._pm_elec_chc = [QtWidgets.QComboBox(), QtWidgets.QComboBox(), QtWidgets.QComboBox()]
        self._pm_elec_out_ch1 = [QtWidgets.QComboBox(), QtWidgets.QComboBox(), QtWidgets.QComboBox()]
        self._pm_elec_out_ch2 = [QtWidgets.QComboBox(), QtWidgets.QComboBox(), QtWidgets.QComboBox()]

        self._nim_bin = [QtWidgets.QLineEdit(), QtWidgets.QLineEdit(), QtWidgets.QLineEdit()]
        self._nim_bin_pwr_supp = [QtWidgets.QLineEdit(), QtWidgets.QLineEdit(), QtWidgets.QLineEdit()]

        self._hv_crate = [QtWidgets.QComboBox(), QtWidgets.QComboBox(), QtWidgets.QComboBox()]

    def config(self, prm_id):
        '''
        Configures the form
        '''

        self._location[prm_id-1].addItems(["SBN-ND", "PAB", "Other"])
        self._vessel[prm_id-1].addItems(["SBND", "Rocket", "Other"])
        self._medium[prm_id-1].addItems(["LAr", "GAr", "Vacuum", "Other"])
        self._pressure[prm_id-1].setText("0")

        self._photocathode[prm_id-1].setText("LAPD")
        self._fibers[prm_id-1].setText("LAPD")
        self._n_fibers[prm_id-1].setValue(3)

        self._optical_ft[prm_id-1].setText("LAPD")
        self._hv_ft[prm_id-1].setText("LAPD")
        self._hv_warm_cables[prm_id-1].setText("PAB")

        self._flash_lamp[prm_id-1].setText("uB old")
        self._flash_lamp_energy[prm_id-1].setText("?")
        self._flash_lamp_frequency[prm_id-1].setText("?")
        self._flash_lamp_settings[prm_id-1].addItems(["INT TRIG", "EXT TRIG", "LINE TRIG"])
        self._flash_lamp_trigger[prm_id-1].setText("Pickup Coil")

        self._pm_elec[prm_id-1].addItems(["Module 1", "Module 2", "Module 3"])
        self._pm_elec_cha[prm_id-1].addItems(["Anode", "Cathode"])
        self._pm_elec_chc[prm_id-1].addItems(["Anode", "Cathode"])
        self._pm_elec_out_ch1[prm_id-1].addItems(["Digitizer A", "Digitizer B"])
        self._pm_elec_out_ch2[prm_id-1].addItems(["Digitizer A", "Digitizer B"])

        self._nim_bin[prm_id-1].setText("PREP")
        self._nim_bin_pwr_supp[prm_id-1].setText("NIN Bin")

        self._hv_crate[prm_id-1].addItems(["Module 1", "Module 2", "Module 3"])


    def create_form(self, prm_id=1):
        '''
        Creates the forms
        '''

        prm = prm_id - 1

        layout = QtWidgets.QFormLayout()

        layout.addRow(QtWidgets.QLabel("Location"), self._location[prm])
        layout.addRow(QtWidgets.QLabel("Vessel"), self._vessel[prm])
        layout.addRow(QtWidgets.QLabel("Medium"), self._medium[prm])
        layout.addRow(QtWidgets.QLabel("Pressure []"), self._pressure[prm])

        layout.addRow(QtWidgets.QLabel("Photocathode"), self._photocathode[prm])
        layout.addRow(QtWidgets.QLabel("Fibers"), self._fibers[prm])
        layout.addRow(QtWidgets.QLabel("Number of Fibers"), self._n_fibers[prm])

        layout.addRow(QtWidgets.QLabel("Optical Feedthrough"), self._optical_ft[prm])
        layout.addRow(QtWidgets.QLabel("HV Feedthrough"), self._hv_ft[prm])
        layout.addRow(QtWidgets.QLabel("HV Warm Cable"), self._hv_warm_cables[prm])

        layout.addRow(QtWidgets.QLabel("Flash Lamp"), self._flash_lamp[prm])
        layout.addRow(QtWidgets.QLabel("Flash Lamp Energy [J]"), self._flash_lamp_energy[prm])
        layout.addRow(QtWidgets.QLabel("Flash Lamp Frequency [Hz]"), self._flash_lamp_frequency[prm])
        layout.addRow(QtWidgets.QLabel("Flash Lamp Settings"), self._flash_lamp_settings[prm])
        layout.addRow(QtWidgets.QLabel("Flash Lamp Trigger"), self._flash_lamp_trigger[prm])

        layout.addRow(QtWidgets.QLabel("PrM Electronics"), self._pm_elec[prm])
        layout.addRow(QtWidgets.QLabel("PrM Electronics Channel A"), self._pm_elec_cha[prm])
        layout.addRow(QtWidgets.QLabel("PrM Electronics Channel B"), self._pm_elec_chc[prm])
        layout.addRow(QtWidgets.QLabel("PrM Electronics Output Ch 1"), self._pm_elec_out_ch1[prm])
        layout.addRow(QtWidgets.QLabel("PrM Electronics Output Ch 2"), self._pm_elec_out_ch2[prm])

        layout.addRow(QtWidgets.QLabel("NIM Bin"), self._nim_bin[prm])
        layout.addRow(QtWidgets.QLabel("NIM Bin Power Supply"), self._nim_bin_pwr_supp[prm])

        layout.addRow(QtWidgets.QLabel("HV Crate"), self._hv_crate[prm])


        self.config(prm_id)

        self._tabs[prm].setLayout(layout)
