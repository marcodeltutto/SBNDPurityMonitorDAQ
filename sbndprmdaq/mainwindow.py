'''
Contains the main GUI elements
'''
#pylint: disable=protected-access,too-many-locals,too-many-statements,too-many-branches

import os
import logging
import numpy as np
from PyQt5 import QtGui, QtWidgets
from PyQt5 import uic
from PyQt5.QtCore import QTimer
import pyqtgraph as pg

from sbndprmdaq.prm_settings.settings import HVSettings
from sbndprmdaq.prm_settings.settings import DigitizerSettings
from sbndprmdaq.configuration_form import Form
from sbndprmdaq.externals import pmt_hv_on, IgnitionAPI

ICON_RED_LED = os.path.join(os.path.dirname(
               os.path.realpath(__file__)),
               'icons/led-red-on.png')
ICON_GREEN_LED = os.path.join(os.path.dirname(
                 os.path.realpath(__file__)),
                 'icons/green-led-on.png')
ICON_BLUE_LED = os.path.join(os.path.dirname(
                os.path.realpath(__file__)),
                'icons/blue-led-on.png')

class Control(QtWidgets.QMainWindow):
    '''
    A widget to display a single purity monitor control panel.
    '''

    def __init__(self, prm_id=1, name='PrM 1', description='Cryo Bottom'):
        '''
        Contructor.

        Args:
            prm_id (int): The purity monitor ID
            name (str): The name of the monitor for display
            description (str): A description of the monitor.
        '''

        super().__init__()

        uifile = os.path.join(os.path.dirname(
            os.path.realpath(__file__)),
            "controls.ui")

        uic.loadUi(uifile, self)

        self._id = prm_id
        self._name = name
        self._description = description
        self._name_label.setText(self._name)
        self._description_label.setText(description)
        self._mode_toggle.set_names('Auto', 'Manual')
        self._mode_toggle.is_simple_option()
        self._running = False

        self._progress_bar.setValue(0)
        self._progress_label.setText('')

        self._lcd_cathode_hv.display('199')
        self._lcd_anode_hv.display('199')

        self._take_hvoff_run.setChecked(True)

        self._disabled_label.setVisible(False)


    def get_id(self):
        '''
        Getter for the PrM ID.

        Returns:
            int: The purity monitor ID.
        '''
        return self._id

    def is_running(self):
        '''
        Returns True if the PrM is running
        '''
        return self._running


    #pylint: disable=too-many-arguments, too-many-branches
    def update(self, hv_cathode=None, hv_anode=None, hv_anodegrid=None,
                     cathode_hv_onoff=None, anode_hv_onoff=None, anodegrid_hv_onoff=None):
        '''
        Updates the controller.

        Args:
            prm_id (int): The purity monitor ID.
        '''
        if self.is_running():
            self._start_stop_btn.setText("(Running)")
            self._start_stop_btn.setDisabled(True)
            self._run_status_label.setText('Running')
            self._status_led.setPixmap(QtGui.QPixmap(ICON_GREEN_LED))
        elif self._mode_toggle.value():
            self._start_stop_btn.setText("(Auto)")
            self._start_stop_btn.setDisabled(True)
            self._run_status_label.setText('Waiting')
            self._status_led.setPixmap(QtGui.QPixmap(ICON_BLUE_LED))
        else:
            self._start_stop_btn.setText("Start")
            self._start_stop_btn.setDisabled(False)
            self._run_status_label.setText('Not Running')
            self._status_led.setPixmap(QtGui.QPixmap(ICON_RED_LED))


        if hv_cathode is not None:
            self._lcd_cathode_hv.display(f'{float(hv_cathode):.0f}')

        if hv_anode is not None:
            self._lcd_anode_hv.display(f'{float(hv_anode):.0f}')

        if hv_anodegrid is not None:
            self._lcd_anodegrid_hv.display(f'{float(hv_anodegrid):.0f}')

        if cathode_hv_onoff is not None:
            if cathode_hv_onoff:
                self._led_cathode_hv.setPixmap(QtGui.QPixmap(ICON_GREEN_LED))
            else:
                self._led_cathode_hv.setPixmap(QtGui.QPixmap(ICON_RED_LED))

        if anode_hv_onoff is not None:
            if anode_hv_onoff:
                self._led_anode_hv.setPixmap(QtGui.QPixmap(ICON_GREEN_LED))
            else:
                self._led_anode_hv.setPixmap(QtGui.QPixmap(ICON_RED_LED))

        if anodegrid_hv_onoff is not None:
            if anodegrid_hv_onoff:
                self._led_anodegrid_hv.setPixmap(QtGui.QPixmap(ICON_GREEN_LED))
            else:
                self._led_anodegrid_hv.setPixmap(QtGui.QPixmap(ICON_RED_LED))


    def set_progress(self, name, perc, **kwargs):
        '''
        Sets the progress in the progress bar.

        Args:
            name (str): The name of the current task.
            perc (int): The progress, a number between 0 and 100.
            color (hex): The color of the text.
        '''
        name = str(name)
        if perc > 100 or perc < 0:
            raise ValueError('Percentage can only be between 0 and 100')

        self._progress_label.setText(name)
        self._progress_bar.setValue(perc)

        if 'color' in kwargs:
            self._progress_label.setStyleSheet("color: " + kwargs['color'])


    def reset_progress(self, name=None, **kwargs):
        '''
        Resets the progress in the progress bar.

        Args:
            name (str): The name of the current task.
            color (hex): The color of the text.
        '''
        self._progress_bar.setValue(0)

        if name is not None:
            self._progress_label.setText(name)
        else:
            self._progress_label.setText('')

        if 'color' in kwargs:
            self._progress_label.setStyleSheet("color: " + kwargs['color'])

    def disable_controls(self, disable=True):
        '''
        Disables controls

        Args:
            disable (bool): wether or not to disable.
        '''

        if disable:
            self._start_stop_btn.setVisible(False)
            self._disabled_label.setVisible(True)
            self._disabled_label.setText('This PrM is controlled\nby PrM 1')

            self._interval_label.setVisible(False)
            self._mode_toggle.setVisible(False)
            self._take_hvoff_run.setVisible(False)
            self._interval_spinbox.setVisible(False)

            self._status_led.setDisabled(True)
        else:
            self._start_stop_btn.setVisible(True)
            self._disabled_label.setVisible(False)

            self._interval_label.setVisible(True)
            self._mode_toggle.setVisible(True)
            self._take_hvoff_run.setVisible(True)
            self._interval_spinbox.setVisible(True)

            self._status_led.setDisabled(False)

    def hv_out_of_range(self, status):
        '''
        If the HV is out of range, it changes the text color to red

        Args:
            status: 0 if the HV is in range, otherwise list containing item
            with bad values ("cathode", "anode", "anodegrid")
        '''
        self._cathode_hv_label.setStyleSheet("color: white;")
        self._anodegrid_hv_label.setStyleSheet("color: white;")
        self._anode_hv_label.setStyleSheet("color: white;")

        if status == 0:
            return

        for item in status:
            if item == 'cathode':
                self._cathode_hv_label.setStyleSheet("color: red;")
            if item == 'anodegrid':
                self._anodegrid_hv_label.setStyleSheet("color: red;")
            if item == 'anode':
                self._anode_hv_label.setStyleSheet("color: red;")



class DataDisplay(QtWidgets.QMainWindow):
    '''
    A widget to display the latest data from a single purity monitor.
    '''

    def __init__(self, prm_id=1, name='PrM 1'):
        '''
        Contructor.

        Args:
            prm_id (int): The purity monitor ID
            name (str): The name of the monitor for display
        '''
        super().__init__()

        uifile = os.path.join(os.path.dirname(
            os.path.realpath(__file__)),
            "data_display.ui")

        uic.loadUi(uifile, self)

        self._id = prm_id
        self._name = name
        self._name_label.setText(self._name)

    def get_id(self):
        '''
        Getter for the PrM ID.

        Returns:
            int: The purity monitor ID.
        '''
        return self._id

    # pylint: disable=invalid-name
    def set_latest_data(self, qa, qc, tau, time):
        '''
        Sets the latest data for display.

        Returns:
            qa: The anode charge.
            qc: The cathode charge.
            tau: The lifetime.
            time: The timestamp.
        '''
        text = f'Qa = {qa:.1f} mV  -  Qc = {qc:.1f} mV\nQa/Qc = {qa/qc:.1f}  -  tau = {tau:.2f} ms'
        self._text.setText(text)
        self._date.setText(time.strftime("%B %d, %Y  %H:%M:%S"))


# pylint: disable=too-many-instance-attributes
class MainWindow(QtWidgets.QMainWindow):
    '''
    The main window.
    '''

    def __init__(self, logs, config):
        '''
        Contructor.

        Args:
            logs (PrMLogger): The widget for the logs.
        '''
        super().__init__()

        uifile = os.path.join(os.path.dirname(
            os.path.realpath(__file__)),
            "mainwindow.ui")

        uic.loadUi(uifile, self)

        self._logger = logging.getLogger(__name__)

        self._logs = logs

        self._logs_btn.clicked.connect(self._logs.show)

        # self._settings = Settings(self)
        self._settings_btn.clicked.connect(self.screenshot)

        self._hv_settings = HVSettings(config["prm_hv_default"], config["prm_hv_ranges"], self)
        self._digitizer_settings = DigitizerSettings(self)

        self._prm_manager = None

        self._status_timer = QTimer()
        self._status_timer.timeout.connect(self._check_status)
        self._status_timer.start(1000)

        self._external_status_timer = QTimer()
        self._external_status_timer.timeout.connect(self._check_external_status)
        self._external_status_timer.start(10000) # 10 seconds

        self._prm_controls = {
            1: Control(prm_id=1, name='PrM 1', description='Int Long (Top)'),
            2: Control(prm_id=2, name='PrM 2', description='Int Short (Bot)'),
            3: Control(prm_id=3, name='PrM 3', description='Inline'),
        }
        # self._prm_controls[0].setStyleSheet("background-color: rgba(0,0,0,0.1);")
        # self._prm_controls[1].setStyleSheet("border-color: rgb(0, 0, 0);")

        self._separator_lines = {
            1: QtWidgets.QFrame(),
            2: QtWidgets.QFrame(),
            3: QtWidgets.QFrame(),
        }

        self._graphs = {}
        self._show_graph = {'all': False}

        for i, control in self._prm_controls.items():
            self.setup_control(control)
            self._controls_layout.addWidget(control)

            self._separator_lines[i].setFrameShape(QtWidgets.QFrame.HLine)
            self._separator_lines[i].setFrameShadow(QtWidgets.QFrame.Sunken)
            self._controls_layout.addWidget(self._separator_lines[i])

            self._graphs[control.get_id()] = {
                'A': self._plot.plot(),
                'B': self._plot.plot(),
                'diff': self._plot.plot(),
            }
            self._show_graph[control.get_id()] = False

        # self._graph_a = self._plot.plot()
        # self._graph_b = self._plot.plot()
        self._plot.setLabel(axis='left', text='Signal [mV]')
        self._plot.setLabel(axis='bottom', text='Time [us]')

        self._infinite_line_1 = pg.InfiniteLine(pos=0)
        self._infinite_line_2 = pg.InfiniteLine(pos=0)
        self._plot.addItem(self._infinite_line_1)
        self._plot.addItem(self._infinite_line_2)

        # Connect the checkboxes for plot displaying
        self._show_choice_checkboxes = {
            'all': self._prmall_checkbox,
            1: self._prm1_checkbox,
            2: self._prm2_checkbox,
            3: self._prm3_checkbox,
        }

        self._show_choice_checkboxes['all'].clicked.connect(lambda: self._update_plot_choice('all'))
        self._show_choice_checkboxes[1].clicked.connect(lambda: self._update_plot_choice(1))
        self._show_choice_checkboxes[2].clicked.connect(lambda: self._update_plot_choice(2))
        self._show_choice_checkboxes[3].clicked.connect(lambda: self._update_plot_choice(3))

        self._latest_data = {
            1: DataDisplay(prm_id=1, name='PrM 1'),
            2: DataDisplay(prm_id=2, name='PrM 2'),
            3: DataDisplay(prm_id=3, name='PrM 3'),
        }

        for latest_data in self._latest_data.values():
            self._latest_data_layout.addWidget(latest_data)
            self.setup_latest_data(latest_data)

        self._config_form = Form(self)

        self.menuMenu.actions()[0].triggered.connect(self._logs.show)
        self.menuMenu.actions()[1].triggered.connect(self.show_comment)
        self.menuMenu.actions()[2].triggered.connect(self._config_form.show)
        self.menuMenu.actions()[3].triggered.connect(self._hv_settings.show)
        self.menuMenu.actions()[4].triggered.connect(self._digitizer_settings.show)

        self._can_exit = True

        self._ignition_api = None

        if config['check_lar_level']:
            self._ignition_api = IgnitionAPI()

        self._config = config

    # pylint: disable=invalid-name
    def closeEvent(self, event):
        '''
        Override closeEvent. This is called when user closes the window.
        '''
        self._logger.info('Requested to close DAQ.')
        if self._can_exit:
            self._prm_manager.exit()
            self._logger.info('Event accepted.')
            event.accept()
        else:
            QtWidgets.QMessageBox.critical(self, 'Error', 'Cannot close the DAQ right now.')
            self._logger.info('Event rejected.')
            event.ignore()

    def setup_control(self, control):
        '''
        Sets up a single purity monitor control widget.

        Args:
            control (Control): The purity monitor Control widget.
        '''
        prm_id = control.get_id()
        # control.setStyleSheet("background-color: rgba(0,0,0,0.1);")
        # control.setStyleSheet("border-color: rgb(0, 0, 0);")
        control._start_stop_btn.clicked.connect(lambda: self.start_stop_prm(prm_id=prm_id))
        control._mode_toggle.clicked.connect(lambda: self._set_mode(prm_id=prm_id))
        control._interval_spinbox.valueChanged.connect(lambda: self._set_interval(prm_id=prm_id))
        control._take_hvoff_run.clicked.connect(lambda: self._set_hvoff_run(prm_id=prm_id))


    def set_start_button_status(self, prm_id=1, status=True):
        '''
        Disables the start/stop button for a certain PrM

        Args:
            prm_id (int): The purity monitor id
        '''
        self._prm_controls[prm_id]._start_stop_btn.setDisabled(status)


    def setup_latest_data(self, latest_data):
        '''
        Sets up a single purity monitor latest-data widget.

        Args:
            control (DataDisply): The purity monitor DataDisplay widget.
        '''
        # latest_data.setStyleSheet("background-color: rgba(0,0,0,0.1);")
        style = "QWidget#centralwidget{border: 1px solid #455364; border-radius: 5px;}"
        latest_data.setStyleSheet(style)



    def _update_plot_choice(self, prm_id):
        '''
        Updates the plot choice.

        Args:
            prm_id (int): The purity monitor ID.
        '''
        if prm_id == 'all':
            if self._prmall_checkbox.isChecked():
                for pid in [1, 2, 3]:
                    self._show_graph[pid] = True
                    self._show_choice_checkboxes[pid].setChecked(False)
            else:
                for pid in [1, 2, 3]:
                    self._show_graph[pid] = False
                    self._show_choice_checkboxes[pid].setChecked(False)

        else:
            if self._show_choice_checkboxes[prm_id].isChecked():
                self._show_graph[prm_id] = True
                self._prmall_checkbox.setChecked(False)
            else:
                self._show_graph[prm_id] = False


    def set_manager(self, manager):
        '''
        Sets the purity monitor manager.

        Args:
            manager (PrMManager): The purity monitor manager.
        '''
        self._prm_manager = manager
        self._hv_settings.set_hv_control(self._prm_manager._hv_control)
        # self._digitizer_settings.set_digitizer_control(self._prm_manager._prm_digitizer)
        self._digitizer_settings.set_manager(self._prm_manager)


    def set_progress(self, prm_id, name, perc, **kwargs):
        '''
        Sets the current progress for a certain task.

        Args:
            prm_id (int): The purity monitor ID.
            name (str): The name of the current task.
            perc (int): The progress, a number between 0 and 100.
            color (hex): The color of the text.
        '''
        self._prm_controls[prm_id].set_progress(name, perc, **kwargs)

    def reset_progress(self, prm_ids, name=None, **kwargs):
        '''
        Resets the progress in the progress bar.

        Args:
            prm_ids (list): The list of purity monitor IDs.
            name (str): The name of the current task.
            color (hex): The color of the text.
        '''
        for prm_id in prm_ids:
            self._prm_controls[prm_id].reset_progress(name, **kwargs)


    def start_stop_prm(self, prm_id):
        '''
        Starts or stops the purity monitor depending on the current status.

        Args:
            prm_id (int): The purity monitor ID.
        '''

        self._prm_controls[prm_id]._running = not self._prm_controls[prm_id]._running

        if self._prm_controls[prm_id].is_running():
            self._start_prm(prm_id)
        else:
            self._stop_prm(prm_id)


    def _start_prm(self, prm_id):
        '''
        Tells the manager to start the purity monitor.

        Args:
            prm_id (int): The purity monitor ID.
        '''
        self._prm_manager.start_prm(prm_id)
        # self._prm_controls[prm_id]._start_stop_btn.setText("Stop")
        # self._prm_controls[prm_id]._run_status_label.setText('Running')
        # self._prm_controls[prm_id]._status_led.setPixmap(QtGui.QPixmap(ICON_GREEN_LED))
        # self.repaint()


    def _stop_prm(self, prm_id):
        '''
        Tells the manager to stop the purity monitor.

        Args:
            prm_id (int): The purity monitor ID.
        '''
        self._prm_manager.stop_prm(prm_id)
        # self._prm_controls[prm_id]._start_stop_btn.setText("Start")
        # self._prm_controls[prm_id]._run_status_label.setText('Not Running')
       	# self._prm_controls[prm_id]._status_led.setPixmap(QtGui.QPixmap(ICON_RED_LED))
        # self.repaint()


    def _set_hv(self, prm_id):
        '''
        Tells the manager how to set the HV.

        Args:
            prm_id (int): The purity monitor ID.
        '''
        if self._prm_controls[prm_id]._hv_toggle.isChecked():
            self._prm_manager.hv_on(prm_id)
        else:
            self._prm_manager.hv_off(prm_id)


    def _set_mode(self, prm_id):
        '''
        Tells the manager to run in automatic more or not.

        Args:
            prm_id (int): The purity monitor ID.
        '''
        control = self._prm_controls[prm_id]
        if control._mode_toggle.isChecked():
            self._prm_manager.set_mode(prm_id, 'auto')
        else:
            self._prm_manager.set_mode(prm_id, 'manual')

    def _set_interval(self, prm_id):
        '''
        Tells the manager the time intrval if running in automatic mode.

        Args:
            prm_id (int): The purity monitor ID.
        '''
        control = self._prm_controls[prm_id]
        self._prm_manager.set_interval(prm_id, control._interval_spinbox.value() * 60)


    def _set_hvoff_run(self, prm_id):
        '''
        Tells the manager whether to take an initial run with no HV.

        Args:
            prm_id (int): The purity monitor ID.
        '''
        control = self._prm_controls[prm_id]
        self._prm_manager.take_hvoff_run(prm_id, control._take_hvoff_run.isChecked())


    def _check_status(self):
        '''
        Callback that checks the status.
        '''

        for control in self._prm_controls.values():

            if not control.isEnabled():
                continue

            control._running = self._prm_manager.is_running(control.get_id())

            status = self._prm_manager.check_hv_range(control.get_id())
            control.hv_out_of_range(status)

            cathode_hv, anode_hv, anodegrid_hv = self._prm_manager.get_hv(control.get_id())
            cathode_hv_onoff, anode_hv_onoff, anodegrid_hv_onoff = self._prm_manager.get_hv_status(control.get_id())

            control.update(cathode_hv, anode_hv, anodegrid_hv,\
                           cathode_hv_onoff, anode_hv_onoff, anodegrid_hv_onoff)

            control._lcd_n_acquisitions.display(f'{self._prm_manager.get_number_acquisitions(control.get_id())}')
            control._lcd_n_repetitions.display(f'{self._prm_manager.get_n_repetitions(control.get_id())}')
            control._lcd_run.display(f'{self._prm_manager.get_run_number(control.get_id())}')

            self._prm_manager.heartbeat()

            if self._prm_manager.digitizer_busy(control.get_id()):
                control._digi_status_label.setText('Busy')
                control._digi_status_label.setStyleSheet("color: red;")
                self.repaint()
            else:
                control._digi_status_label.setText('Ready')
                control._digi_status_label.setStyleSheet("color: green;")
                self.repaint()

            if control._mode_toggle.isChecked():
                rem_time = self._prm_manager.remaining_time(control.get_id()) / 1e3 # seconds
                minutes, seconds = divmod(rem_time, 60)
                control._start_stop_btn.setText(f"{minutes:.0f}:{seconds:.0f}")


            data = self._prm_manager.get_data(control.get_id())
            # print('From mainwindow', data)

            if data is None:
                continue

            # s_to_ms = 1e3
            s_to_us = 1e6
            v_to_mv = 1e3

            flash_time = 17 # ns

            x_a = None
            y_a = None
            x_b = None
            x_b = None

            #
            # Plot waveform from channel A
            #
            if 'A' in data and data['A'] is not None and len(data['A']):

                av_waveform = np.mean(data['A'], axis=0)

                x_a = np.arange(len(av_waveform)) / self._prm_manager.samples_per_sec() * s_to_us
                y_a = av_waveform * v_to_mv

                if self._show_graph[control.get_id()] and not self._diff_checkbox.isChecked():
                    self._graphs[control.get_id()]['A'].setData(x_a, y_a, pen=pg.mkPen('b'))
                else:
                    self._graphs[control.get_id()]['A'].setData([], [])

            #
            # Plot waveform from channel A
            #
            if 'B' in data and data['B'] is not None and len(data['B']):

                av_waveform = np.mean(data['B'], axis=0)

                x_b = np.arange(len(av_waveform)) / self._prm_manager.samples_per_sec() * s_to_us
                y_b = av_waveform * v_to_mv

                if self._show_graph[control.get_id()] and not self._diff_checkbox.isChecked():
                    self._graphs[control.get_id()]['B'].setData(x_b, y_b, pen=pg.mkPen('r'))
                else:
                    self._graphs[control.get_id()]['B'].setData([], [])

            #
            # Plot differnece of waveforms
            #
            if self._diff_checkbox.isChecked() and self._show_graph[control.get_id()] \
                and y_a is not None and y_b is not None:
                self._graphs[control.get_id()]['diff'].setData(x_a, y_a-y_b, pen=pg.mkPen('g'))
            else:
                self._graphs[control.get_id()]['diff'].setData([], [])

            #
            # Plot trigger time lines
            #
            trigger_x = self._prm_manager.trigger_sample() / self._prm_manager.samples_per_sec() * s_to_us
            self._infinite_line_1.setValue(trigger_x)
            self._infinite_line_2.setValue(trigger_x + flash_time)


            qa, qc, tau = self._prm_manager.get_latest_lifetime(control.get_id())

            self._latest_data[control.get_id()].set_latest_data(qa, qc, tau, data['time'])


    def _check_external_status(self):
        '''
        Checks the status of external components of SBND, e.g. the PMT HV
        '''
        if self._config['check_pmt_hv']:
            if pmt_hv_on():
                self._led_pmt_hv.setPixmap(QtGui.QPixmap(ICON_GREEN_LED))
                self.inhibit_run(True, [1, 2])
            else:
                self._led_pmt_hv.setPixmap(QtGui.QPixmap(ICON_RED_LED))
                self.inhibit_run(False, [1, 2])
        else:
            self._led_pmt_hv.setDisabled(True)


        if self._config['check_lar_level']:

            for prm_id in [1, 2, 3]:
                if self._ignition_api.prm_covered(prm_id=prm_id):
                    self._prm_controls[prm_id]._liquid_level_label.setText('Covered')
                    self._prm_controls[prm_id]._liquid_level_label.setStyleSheet("color: green;")
                    if self._config['enforce_level']:
                        self.inhibit_run(False, [prm_id])
                else:
                    self._prm_controls[prm_id]._liquid_level_label.setText('NOT Covered')
                    self._prm_controls[prm_id]._liquid_level_label.setStyleSheet("color: red;")
                    if self._config['enforce_level']:
                        self.inhibit_run(True, [prm_id])

        else:
            self._prm_controls[1]._liquid_level_label.setText('Disabled')
            self._prm_controls[1]._liquid_level_label.setDisabled(True)
            self._prm_controls[1]._digitizer_image.setDisabled(True)

            self._prm_controls[2]._liquid_level_label.setText('Disabled')
            self._prm_controls[2]._liquid_level_label.setDisabled(True)
            self._prm_controls[2]._digitizer_image.setDisabled(True)


    def inhibit_run(self, do_inhibit=True, prm_ids=(1, 2)):
        '''
        Inhibits running the specified PrMs

        Args:
            do_inhibit (bool): if True it inhibits running
            prm_ids (set): list of PrM IDs to inhibit
        '''

        for prm_id in prm_ids:
            if do_inhibit:
                self._status_bar.showMessage(f'Inhibiting PrM IDs {prm_ids}.')
                # self._prm_controls[prm_id].setEnabled(False)
                self._prm_manager.inhibit_run(prm_id, do_inhibit=True)

                # Make sure we are not in automatic mode
                # self._prm_controls[prm_id]._mode_toggle.setChecked(False)

            else:
                self._status_bar.showMessage(f'Enabling PrM IDs {prm_ids}.')
                # self._prm_controls[prm_id].setEnabled(True)
                self._prm_manager.inhibit_run(prm_id, do_inhibit=False)


    def missing_digitizer(self, prm_id):
        '''
        Setter for a missing digitizer.

        Args:
            prm_id (int): The purity monitor ID
        '''
        self._status_bar.showMessage(f'Cannot find digitizer for PrM ID {prm_id}.')
        self._prm_controls[prm_id].setEnabled(False)

    def disable_controls(self, prm_id):
        '''
        Disables controls for prm_id

        Args:
            prm_id (int): The purity monitor ID
        '''
        self._status_bar.showMessage(f'PrM ID {prm_id} controls are disabled.')
        self._prm_controls[prm_id].disable_controls()
        self._digitizer_settings.disable(prm_id)


    def show_comment(self):
        '''
        A QInputDialog appears is called
        '''
        comment, _ = QtWidgets.QInputDialog.getText(
             self, 'Input Dialog', 'Enter your comment:')
        self._prm_manager.set_comment(comment)


    def get_config_values(self, prm_id=1):
        '''
        Gets config values
        '''
        self._config_form.get_values(prm_id)

    def screenshot(self):
        '''
        Takes screenshot of current window
        '''
        screen = QtWidgets.QApplication.primaryScreen()
        window = self.windowHandle()
        if window:
            screen = window.screen()

        screenshot = screen.grabWindow(0)
        screenshot.save('shot.jpg', 'jpg')
