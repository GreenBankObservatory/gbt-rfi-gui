import sys

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from screeninfo import get_monitors

class SelectionWindow(QMainWindow):
    """The selection window of the GUI"""

    def __init__(self):
        """Initializes the selection window"""
        super().__init__()

        self.setWindowTitle("GBT RFI Data Query")
        self._init_geometry(0.8)
        self._init_UI()

        self.show()

    def _init_geometry(self, mult):
        """
        Draws the GUI on the primary monitor

        Parameters
        ----------
            mult : int or float
                proportion of total size to draw window (0.8 = 80%)

        """
        for m in get_monitors():
            if m.is_primary:
                self.width = int(m.width * mult)
                self.height = int(m.height * mult)
                self.xpos = int(m.x + (m.width * (1 - mult)) / 2)
                self.ypos = int(m.y + (m.height * (1 - mult)) / 2)
        self.setGeometry(self.xpos, self.ypos, self.width, self.height)

    def _init_UI(self):
        """Creates the skeleton structure of the GUI"""
        
        self.main_widget = QWidget()
        self.main_layout = QGridLayout()
        self.main_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.main_widget)
        
        self._make_fonts()
        self._make_title()
        self._make_panel_rx()
        self._make_panel_freq()
        self._make_panel_dates()
        self._make_checkboxes()
        self._make_main_button()

        self.main_layout.addWidget(self.title_widget,       1, 0, 1, 3)
        self.main_layout.addWidget(self.rx_widget,          2, 0, 1, 3)
        self.main_layout.addWidget(self.freq_widget,        3, 0, 1, 3)
        self.main_layout.addWidget(self.dates_widget,       4, 0, 1, 3)
        self.main_layout.addWidget(self.checkbox_widget,    5, 1, 1, 2)
        self.main_layout.addWidget(self.main_button,        6, 1, 1, 1)

    def _make_fonts(self):
        """Make custom font rules without stylesheet"""

        self.font_h1 = QFont()
        self.font_h1.setBold(True)
        self.font_h1.setPointSize(36)

        self.font_h2 = QFont()
        self.font_h2.setBold(False)
        self.font_h2.setPointSize(24)

        self.font_p = QFont()
        self.font_p.setBold(False)
        self.font_p.setPointSize(18)

    def _make_title(self):
        """Makes the title area"""

        # Init the widget and layout
        self.title_widget = QWidget()
        self.title_layout = QGridLayout()
        self.title_widget.setLayout(self.title_layout)

        # Make and fill the panel-specific widget(s)
        self.title_0 = QLabel("Automated RFI Scan Data Reduction")
        self.title_0.setFont(self.font_h1)

        self.title_1 = QLabel("To facilitate the retrieval and reduction of RFI Data of interest")
        self.title_1.setFont(self.font_h2)

        self.title_2 = QLabel("Please hover over any widget to see details about possible input")
        self.title_2.setFont(self.font_p)

        # Add panel-specific widgets to panel layout
        self.title_layout.addWidget(self.title_0,   0, 0, 1, 1, Qt.AlignCenter)
        self.title_layout.addWidget(self.title_1,   1, 0, 1, 1, Qt.AlignCenter)
        self.title_layout.addWidget(self.title_2,   2, 0, 1, 1, Qt.AlignCenter)

    def _make_panel_rx(self):
        """RX selection"""

        # Init the widget and layout
        self.rx_widget = QWidget()
        self.rx_layout = QGridLayout()
        self.rx_widget.setLayout(self.rx_layout)

        # Load the list of receivers
        self.get_rx_list()       

        # Make and fill the panel-specific widget(s)
        self.rx_label = QLabel("Receivers")

        self.rx_combo = QComboBox()
        self.rx_combo.addItems(self.rcvrs) 

        # Add panel-specific widgets to panel layout
        self.rx_layout.addWidget(self.rx_label,     0, 0, 1, 1)
        self.rx_layout.addWidget(self.rx_combo,     0, 1, 1, 2)

    def _make_panel_freq(self):
        """Frequency selection"""

        # Init the widget and layout
        self.freq_widget = QWidget()
        self.freq_layout = QGridLayout()
        self.freq_widget.setLayout(self.freq_layout)

        # Make and fill the panel-specific widget(s)
        self.freq_lower_label = QLabel("Start Frequency (MHz)")
        self.freq_lower_box = QLineEdit()

        self.freq_upper_label = QLabel("End Frequency (MHz)")
        self.freq_upper_box = QLineEdit()

        # Add panel-specific widgets to panel layout
        self.freq_layout.addWidget(self.freq_lower_label,   0, 0, 1, 1)
        self.freq_layout.addWidget(self.freq_lower_box,     0, 1, 1, 2)
        self.freq_layout.addWidget(self.freq_upper_label,   1, 0, 1, 1)
        self.freq_layout.addWidget(self.freq_upper_box,     1, 1, 1, 2)

    def _make_panel_dates(self):
        """Date selection"""

        # Init the widget and layout
        self.dates_widget = QWidget()
        self.dates_layout = QGridLayout()
        self.dates_widget.setLayout(self.dates_layout)

        # Make and fill the panel-specific widget(s)
        self.date_start_label = QLabel("Start Date")
        self.date_start_pick = QDateEdit(calendarPopup=True)

        self.date_end_label = QLabel("End Date")
        self.date_end_pick = QDateEdit(calendarPopup=True)

        # Add panel-specific widgets to panel layout
        self.dates_layout.addWidget(self.date_start_label,  0, 0, 1, 1)
        self.dates_layout.addWidget(self.date_start_pick,   0, 1, 1, 2)
        self.dates_layout.addWidget(self.date_end_label,    1, 0, 1, 1)
        self.dates_layout.addWidget(self.date_end_pick,     1, 1, 1, 2)
        
    def _make_checkboxes(self):
        """Checkboxes"""

        # Init the widget and layout
        self.checkbox_widget = QWidget()
        self.checkbox_layout = QGridLayout()
        self.checkbox_widget.setLayout(self.checkbox_layout)

        # Make and fill the panel-specific widget(s)
        self.checkbox_fcc = QCheckBox()
        self.checkbox_fcc.setText("Annotate FCC Radio Spectrum Allocation")

        self.checkbox_csv = QCheckBox()
        self.checkbox_csv.setText("Save Data From This Plot in CSV Format")

        # Add panel-specific widgets to panel layout
        self.checkbox_layout.addWidget(self.checkbox_fcc,   0, 0, 1, 1)
        self.checkbox_layout.addWidget(self.checkbox_csv,   1, 0, 1, 1)

        # Connect the checkboxes to functions
        self.checkbox_fcc.stateChanged.connect(self.func_checkbox_fcc)
        self.checkbox_csv.stateChanged.connect(self.func_checkbox_csv)

    def _make_main_button(self):
        """Button to plot everything"""

        # Init the widget
        self.main_button = QPushButton("Plot with these Args")

        # Connect to a function
        self.main_button.clicked.connect(self.func_main_button)

    def get_rx_list(self):
        """Get the list of receivers"""
        # [TODO] Dynamically generate this list from some database

        self.rcvrs = [
            "Prime Focus 1",
            "L-band",
            "S-band",
            "C-band",
            "X-band",
            "Ku-band",
            "K-band FPA",
            "Ka-band",
            "Q-band",
        ]

    def func_checkbox_fcc(self, checked):
        """Function to call when the FCC checkbox is toggled"""

        # [TODO] Actually write stuff here
        if checked:
            print("You checked the FCC checkbox!")
        else:
            print("You unchecked the FCC checkbox!")

    def func_checkbox_csv(self, checked):
        """Function to call when the CSV checkbox is toggled"""

        # [TODO] Actually write stuff here
        if checked:
            print("You checked the CSV checkbox!")
        else:
            print("You unchecked the CSV checkbox!")

    def func_main_button(self):
        """Function to run when you hit the plot button"""
        
        # [TODO] Actually write stuff here
        print("You pressed the main button!")


class RFIApp(QApplication):
    """The overall app"""

    def __init__(self, *args):
        """Initialize the overall app and open the first window"""
        QApplication.__init__(self, *args)
        self.win_select = SelectionWindow()
        self.win_select.show()

if __name__ == "__main__":
    app = RFIApp(sys.argv)
    app.exec_()