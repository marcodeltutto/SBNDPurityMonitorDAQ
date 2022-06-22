import os
import logging
import numpy as np
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5 import uic
from PyQt5.QtCore import QTimer
import pyqtgraph as pg

from sbndprmdaq.prm_settings.settings import HVSettings
from sbndprmdaq.prm_settings.settings import DigitizerSettings
from sbndprmdaq.configuration_form import Form

ICON_RED_LED = os.path.join(os.path.dirname(
               os.path.realpath(__file__)),
               'icons/led-red-on.png')
ICON_GREEN_LED = os.path.join(os.path.dirname(
                 os.path.realpath(__file__)),
                 'icons/green-led-on.png')

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
        self._mode_toggle.setNames('Auto', 'Manual')
        self._mode_toggle.isSimpleOption()
        self._running = False

        self._progress_bar.setValue(0)
        self._progress_label.setText('')

        self._lcd_cathode_hv.display('199')
        self._lcd_anode_hv.display('199')


    def get_id(self):
        '''
        Getter for the PrM ID.

        Returns:
            int: The purity monitor ID.
        '''
        return self._id

    def is_running(self):
        '''
        '''
        return self._running


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
            raise Exception('perc can pnly be between 0 and 100')

        self._progress_label.setText(name)
        self._progress_bar.setValue(perc)

        if 'color' in kwargs:
            self._progress_label.setStyleSheet("color: " + kwargs['color']);


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
            self._progress_label.setStyleSheet("color: " + kwargs['color']);



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

    def set_latest_data(self, qa, qc, tau, time):
        '''
        Sets the latest data for display.

        Returns:
            qa: The anode charge.
            qc: The cathode charge.
            tau: The lifetime.
            time: The timestamp.
        '''
        text = f'Qa = {qa}\nQc = {qc}\nLifetime = {tau}'
        self._text.setText(text)
        self._date.setText(time.strftime("%B %d, %Y  %H:%M:%S"))


class MainWindow(QtWidgets.QMainWindow):
    '''
    The main window.
    '''

    def __init__(self, logs):
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
        # self._settings_btn.clicked.connect(self._settings.show)

        self._hv_settings = HVSettings(self)
        self._digitizer_settings = DigitizerSettings(self)

        self._prm_manager = None

        self._status_timer = QTimer()
        self._status_timer.timeout.connect(self._check_status)
        self._status_timer.start(1000)

        self._prm_controls = {
            1: Control(prm_id=1, name='PrM 1', description='Cryo Bottom'),
            2: Control(prm_id=2, name='PrM 2', description='Cryo Top'),
            3: Control(prm_id=3, name='PrM 3', description='Inline'),
        }
        # self._prm_controls[0].setStyleSheet("background-color: rgba(0,0,0,0.1);")

        self._graphs = {}
        self._show_graph = {'all': False}

        for control in self._prm_controls.values():
            self.setup_control(control)
            self._controls_layout.addWidget(control)
            self._graphs[control.get_id()] = {
                'A': self._plot.plot(),
                'B': self._plot.plot(),
            }
            self._show_graph[control.get_id()] = False

        # self._graph_a = self._plot.plot()
        # self._graph_b = self._plot.plot()
        self._plot.setLabel(axis='left', text='Signal [mV]')
        self._plot.setLabel(axis='bottom', text='Time [ms]')

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
        control.setStyleSheet("background-color: rgba(0,0,0,0.1);")
        control._start_stop_btn.clicked.connect(lambda: self.start_stop_prm(prm_id=prm_id))
        control._mode_toggle.clicked.connect(lambda: self._set_mode(prm_id=prm_id))

    def setup_latest_data(self, latest_data):
        '''
        Sets up a single purity monitor latest-data widget.

        Args:
            control (DataDisply): The purity monitor DataDisplay widget.
        '''
        prm_id = latest_data.get_id()
        latest_data.setStyleSheet("background-color: rgba(0,0,0,0.1);")



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
        self._digitizer_settings.set_digitizer_control(self._prm_manager._digitizers)

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

    def reset_progress(self, prm_id, name=None, **kwargs):
        '''
        Resets the progress in the progress bar.

        Args:
            prm_id (int): The purity monitor ID.
            name (str): The name of the current task.
            color (hex): The color of the text.
        '''
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
        Tells the manager how to set the HV.

        Args:
            prm_id (int): The purity monitor ID.
        '''
        control = self._prm_controls[prm_id]
        if control._mode_toggle.isChecked():
            self._prm_manager.set_mode(prm_id, 'auto')
        else:
            self._prm_manager.set_mode(prm_id, 'manual')


    def _check_status(self):
        '''
        Callback that checks the status.
        '''

        for control in self._prm_controls.values():

            if not control.isEnabled():
                continue

            control._running = self._prm_manager.is_running(control.get_id())

            cathode_hv, anode_hv, anodegrid_hv = self._prm_manager.get_hv(control.get_id())
            cathode_hv_onoff, anode_hv_onoff, anodegrid_hv_onoff = self._prm_manager.get_hv_status(control.get_id())

            control.update(cathode_hv, anode_hv, anodegrid_hv,\
                           cathode_hv_onoff, anode_hv_onoff, anodegrid_hv_onoff)

            control._lcd_n_acquisitions.display(f'{self._prm_manager.get_n_acquisitions(control.get_id())}')
            control._lcd_run.display(f'{self._prm_manager.get_run_number(control.get_id())}')

            if self._prm_manager.digitizer_busy(control.get_id()):
                control._digi_status_label.setText('Busy')
                control._digi_status_label.setStyleSheet("color: red;")
                self.repaint()
            else:
                control._digi_status_label.setText('Ready')
                control._digi_status_label.setStyleSheet("color: green;")
                self.repaint()

            data = self._prm_manager.get_data(control.get_id())
            # print('From mainwindow', data)

            if data is None:
                continue

            # for el in data['A']:
            #     print('av of el in data A', np.mean(el))

            # for el in data['B']:
            #     print('av of el in data B', np.mean(el))

            s_to_ms = 1e3
            v_to_mv = 1e3

            if 'A' in data and data['A'] is not None:
                # print('------------------------------ len data', len(data['A']))
                av_waveform = np.mean(data['A'], axis=0)
                # print('------------------------------ len av_waveform', len(av_waveform))
                x = np.arange(len(av_waveform)) / self._prm_manager.ats_samples_per_sec() * s_to_ms
                y = av_waveform * v_to_mv
                # self._graph_a.setData(x, y, pen=pg.mkPen('b'))

                if self._show_graph[control.get_id()]:
                    self._graphs[control.get_id()]['A'].setData(x, y, pen=pg.mkPen('b'))
                else:
                    self._graphs[control.get_id()]['A'].setData([], [])

            if 'B' in data and data['B'] is not None:
                av_waveform = np.mean(data['B'], axis=0)
                x = np.arange(len(av_waveform)) / self._prm_manager.ats_samples_per_sec() * s_to_ms
                y = av_waveform * v_to_mv
                # self._graph_b.setData(x, y, pen=pg.mkPen('r'))
                if self._show_graph[control.get_id()]:
                    self._graphs[control.get_id()]['B'].setData(x, y, pen=pg.mkPen('r'))
                else:
                    self._graphs[control.get_id()]['B'].setData([], [])

            qa, qc, tau = self._extract_values(data['A'], data['B'])

            self._latest_data[control.get_id()].set_latest_data(qa, qc, tau, data['time'])

    def _extract_values(self, a, b):
        '''
        Extracts the Qa, Qc, tau from the latest data. To be implemented in a separate
        analysis class.

        Args:
            a (array): Waveform for channel A.
            b (array): Waveform for channel B.

        Returns:
            float: The extracted Qa.
            float: The extracted Qc.
            float: The extracted Lifetime.
        '''
        return 1, 2, 3

    def missing_digitizer(self, prm_id):
        '''
        Setter for a missing digitizer.

        Args:
            prm_id (int): The purity monitor ID
        '''
        self._status_bar.showMessage(f'Cannot find digitizer for PrM ID {prm_id}.')
        self._prm_controls[prm_id].setEnabled(False)


    def show_comment(self):
        '''
        '''
        comment, _ = QtWidgets.QInputDialog.getText(
             self, 'Input Dialog', 'Enter your comment:')
        self._prm_manager.set_comment(comment)



    def get_config_values(self, prm_id=1):
        '''
        '''
        self._config_form.get_values(prm_id)

    # def save_settings(self, values):
    #     for prm_id, values in values.items():
    #         print(prm_id, values)

    #         for name, value in values.items():
    #             if name == 'cathode_hv':
    #                 self._prm_manager._hv_control.set_hv_value('neg', value, prm_id)
    #             elif name == 'anode_hv':
    #                 self._prm_manager._hv_control.set_hv_value('pos', value, prm_id)
    #             else:
    #                 print(name, value)
    #                 raise Exception('Not an option')


