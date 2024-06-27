# coding=utf-8
"""
    Interactive graphic interface for simulate music input.

    (C) 2022 Sophia Corvaia, University of Palermo, Palermo, Italy
    Released under GNU Public License (GPL)
    Contacts: sophia.corvaia@unipa.it
"""
from sys import argv, exit
from threading import Thread, Event

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (
    QMainWindow,
    QApplication,
    QMessageBox,
    QDesktopWidget,
    QRadioButton
)
from PyQt5.uic import loadUi

from main import run

# Global simulation graphics parameters
data = robot = speak = show = None
event = Event()


def center(window: QMainWindow) -> None:
    """Center main window on screen.

    :param window: Window to be center
    :type window: QMainWindow
    """
    qr = window.frameGeometry()
    cp = QDesktopWidget().availableGeometry().center()
    qr.moveCenter(cp)
    window.move(qr.topLeft())


class Logging(QMainWindow):
    """Class implementing graphic interface for realtime log during simulation"""

    # PyqtSignals for manage changing signals from thread
    finished = pyqtSignal()
    updateTextArea = pyqtSignal(str)
    updateEmotion = pyqtSignal(str)
    exception = pyqtSignal()
    updateModel = pyqtSignal(int)

    def __init__(self, parent=None) -> None:
        """Constructor method."""

        super(Logging, self).__init__(parent)
        self.thread = None
        loadUi("./resources/gui/Logging.ui", self)
        # Init UI
        self.setWindowTitle("SUSAN: Running simulation...")
        self.text = "INFO: Starting simulation...\n"
        self.textEdit.setText(self.text)
        self.pushButton.clicked.connect(self.__stop)
        center(self)
        # Connect pyqtsignals to the methods to be executed
        self.updateEmotion.connect(self.set_emotion_gui)
        self.updateTextArea.connect(self.set_text_area)
        self.finished.connect(self.end_task)
        self.exception.connect(self.raise_exception)
        self.updateModel.connect(self.set_model_gui)
        self.signals = {'text_signal': self.updateTextArea, 'emo_signal': self.updateEmotion,
                        'mod_signal': self.updateModel, 'exc_signal': self.exception, 'fin_signal': self.finished}

    def start_task(self):
        """Start threading task"""
        self.thread = Thread(target=run, args=(data, self.signals, event, robot, speak, show))
        self.thread.start()

    def end_task(self):
        """End threading task"""
        self.pushButton.setText('Quit simulation')
        message = QMessageBox()
        message.setWindowTitle("Simulation completed")
        message.setText("Simulation is over! Thank you for join us!")
        message.setIcon(QMessageBox.Information)
        message.setStandardButtons(QMessageBox.Ok)
        message.exec_()
        self.label.setText('SUSAN: Simulation completed!')

    def show_window(self) -> None:
        """Show logging window and start thread"""
        # Thread to handle asynchronous message in window
        self.show()
        self.start_task()

    def raise_exception(self):
        """Show message box with generic error message"""
        self.pushButton.setText("Quit simulation")
        message = QMessageBox()
        message.setWindowTitle("Error detected")
        message.setText("Oh no! A sudden error occurred. Check your settings and try again.")
        message.setIcon(QMessageBox.Critical)
        message.setStandardButtons(QMessageBox.Retry)
        message.exec_()

    def set_text_area(self, text: str) -> None:
        """Set text area field in graphic and concat new text.

        :param text: Text to insert
        :type text: str
        """
        self.text = self.text + text + "\n"
        self.textEdit.setText(self.text)

    def set_model_gui(self, level: int) -> None:
        """Set model label image in view.

        :param level: Trace level inside the model
        :type level: int
        """
        pixmap = QPixmap('./resources/images/model/{0}.png'.format(str(level)))
        label = self.model_label
        label.setPixmap(pixmap)
        label.setFixedHeight(pixmap.height())
        label.setFixedWidth(pixmap.width())

    def set_emotion_gui(self, emotion: str) -> None:
        """Set all emotion elements in view with selected name.

        :param emotion: Selected emotion
        :type emotion: str
        """
        # Set EmBody element
        pixmap = QPixmap('./resources/images/emBody/{0}.jpg'.format(emotion))
        label = self.emo_body
        label.setPixmap(pixmap)
        label.setFixedHeight(pixmap.height())
        label.setFixedWidth(pixmap.width())
        # Set Robot Body element
        pixmap = QPixmap('./resources/images/Pepper/{0}.png'.format(emotion))
        label = self.robot_body
        label.setPixmap(pixmap)
        label.setFixedHeight(pixmap.height())
        label.setFixedWidth(pixmap.width())
        # Set emotion label
        self.emotion.setText("Selected emotion: " + emotion)

    def __stop(self) -> None:
        """Interrupt execution of simulation, showing message box"""

        message = QMessageBox()
        message.setWindowTitle("Info Status")
        if self.pushButton.text == 'Quit simulation':
            self.close()
            return
        event.set()
        message.setText("Simulation interrupted!")
        message.setIcon(QMessageBox.Critical)
        message.setStandardButtons(QMessageBox.Ok)
        message.exec_()
        self.close()


class Simulation(QMainWindow):
    """Class handle simulation graphic interface"""

    def __init__(self):
        """Constructor method."""

        super(Simulation, self).__init__()
        loadUi("./resources/gui/SUSAN.ui", self)
        # widget.setStyleSheet("""
        #                background-image: url('./resources/music.jpg')
        #            """)
        self.setWindowTitle("SUSAN: Music Interface")
        center(self)
        self.buttonBox.accepted.connect(self.__start)
        self.buttonBox.rejected.connect(self.__stop)
        self.check_robot.clicked.connect(self.__show_checked)
        self.check_speak.hide()
        self.check_emotion.hide()

    def __show_checked(self):
        """Show speak and emotion checkbox if robot interface is selected"""
        if self.check_robot.isChecked():
            self.check_speak.show()
            self.check_emotion.show()
        else:
            self.check_speak.hide()
            self.check_emotion.hide()
            self.check_speak.setChecked(False)
            self.check_emotion.setChecked(False)

    def __get_instrument(self) -> str:
        """Get instrument field with selected radio button for instrument.

        :return: Instrument's name
        :rtype: str
        """
        for rb in self.box_instrument.findChildren(QRadioButton):
            if rb.isChecked():
                return rb.text()

    def __get_pitch(self) -> str:
        """Get pitch field with selected radio button for instrument.

        :return: Pitch level
        :rtype: str
        """
        for rb in self.box_pitch.findChildren(QRadioButton):
            if rb.isChecked():
                return rb.text()

    @staticmethod
    def __stop():
        """Interrupt execution of simulation, showing message box"""

        message = QMessageBox()
        message.setWindowTitle("Info Status")
        message.setText("Simulation closed! See you again!")
        message.setIcon(QMessageBox.Information)
        message.setStandardButtons(QMessageBox.Ok)
        message.exec_()
        exit(app.exec_())

    def __start(self) -> None:
        """Get parameter from GUI and start simulation.
        Create a connection with main script."""

        global robot, speak, show, data

        # Get User's Value from GUI
        volume = self.volume_slicer.value()
        rhythm = self.rhythm_slicer.value()
        instrument = self.__get_instrument()
        pitch = self.__get_pitch()
        robot = self.check_robot.isChecked()
        speak = self.check_speak.isChecked()
        show = self.check_emotion.isChecked()

        if instrument is None:
            message = QMessageBox()
            message.setWindowTitle("Instrument Status")
            message.setText("You must select an instrument! Music required an instrument to be played!")
            message.setIcon(QMessageBox.Warning)
            message.setStandardButtons(QMessageBox.Retry)
            message.exec_()
            return

        if pitch is None:
            message = QMessageBox()
            message.setWindowTitle("Pitch Status")
            message.setText("You must select a pitch level! Music required a pitch to be played!")
            message.setIcon(QMessageBox.Warning)
            message.setStandardButtons(QMessageBox.Retry)
            message.exec_()
            return

        data = {'Volume': volume,
                'Rhythm': rhythm,
                'Instrument': instrument,
                'Pitch': pitch}

        self.logging = Logging(self)
        self.logging.show_window()


if __name__ == "__main__":
    app = QApplication(argv)
    main_window = Simulation()
    main_window.show()
    exit(app.exec_())
