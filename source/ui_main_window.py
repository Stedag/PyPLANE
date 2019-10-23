"""
Draws the main window of the PyPLANE Qt5 interface
"""

import sys

from PyQt5.QtGui import *
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QAction,
)
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from equations import DifferentialEquation, SystemOfEquations
from trajectory import PhaseSpacePlotter
from defaults import psp_by_dimensions, default_1D, default_2D
from errors import *

VERSION = "0.0-pre-alpha"

class MainWindow(QMainWindow):
    """
    TODO: Insert docstring
    """

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self: QMainWindow) -> None:
        """
        Adds components (buttons, text boxes, etc.) and draws the window
        """
        
        self.setStyleSheet(open("source/styles.css").read())

        # Define central widget
        cent_widget = QWidget(self)
        self.setCentralWidget(cent_widget)

        # Menu Bar
        menu_bar = self.menuBar()
        menu_file = menu_bar.addMenu("File")
        menu_edit = menu_bar.addMenu("Edit")
        menu_plot_opts = menu_edit.addMenu("Plot Options")

        # self.action_new_window = QAction("New Window", self)
        self.action_quit = QAction("Quit", self)
        # menu_file.addAction(self.action_new_window)
        menu_file.addAction(self.action_quit)

        self.action_quit.triggered.connect(self.close)

        self.action_nullclines = QAction("Plot Nullclines", self, checkable=True)
        menu_plot_opts.addAction(self.action_nullclines)

        # print(action_nullclines.isChecked())

        # Canvas to show the phase plot as part of the main window
        # By default, open application displaying a two dimensional system
        self.default_dims = 2
        self.psp_canvas_default(self.default_dims)

        # Window Features
        self.x_prime_label = QLabel(self.phase_plot.system.system_coords[0] + "' =")
        self.y_prime_label = QLabel(self.phase_plot.system.system_coords[1] + "' =")
        self.x_prime_entry = QLineEdit(self.phase_plot.system.ode_expr_strings[0])
        self.y_prime_entry = QLineEdit(self.phase_plot.system.ode_expr_strings[1])
        self.plot_button = QPushButton("Plot")

        # Nullclines are set to toggle with the "Plot Nullclines" menu option
        self.action_nullclines.changed.connect(self.phase_plot.toggle_nullclines)

        # Parameter inputs
        param_names = list(self.setup_dict["params"].keys())
        param_vals = list(self.setup_dict["params"].values())

        self.parameter_input_boxes = {}
        self.no_of_params = 5  # Number of user defined parameters
        for param_num in range(self.no_of_params):
            # Fills parameter input boxes with parameter vars and corresponding vals
            if param_num < len(self.setup_dict["params"].keys()):
                self.parameter_input_boxes[
                    "param_" + str(param_num) + "_name"
                ] = QLineEdit(param_names[param_num])
                self.parameter_input_boxes[
                    "param_" + str(param_num) + "_val"
                ] = QLineEdit(str(param_vals[param_num]))
            # Allows for the situation where self.no_of_params > len(self.setup_dict["params"].keys())
            else:
                self.parameter_input_boxes[
                    "param_" + str(param_num) + "_name"
                ] = QLineEdit()
                self.parameter_input_boxes[
                    "param_" + str(param_num) + "_val"
                ] = QLineEdit()

        # Axes limit imputs
        self.limits_heading = QLabel("Limits of Axes:")
        self.x_max_label = QLabel(
            "Max " + self.phase_plot.system.system_coords[0] + " ="
        )
        self.x_max_input = QLineEdit(str(self.phase_plot.axes_limits[0][1]))
        self.x_min_label = QLabel(
            "Min " + self.phase_plot.system.system_coords[0] + " ="
        )
        self.x_min_input = QLineEdit(str(self.phase_plot.axes_limits[0][0]))
        xlim_layout = QHBoxLayout()
        xlim_layout.addWidget(self.x_max_label)
        xlim_layout.addWidget(self.x_max_input)
        xlim_layout.addWidget(self.x_min_label)
        xlim_layout.addWidget(self.x_min_input)

        self.y_max_label = QLabel(
            "Max " + self.phase_plot.system.system_coords[1] + " ="
        )
        self.y_max_input = QLineEdit(str(self.phase_plot.axes_limits[1][1]))
        self.y_min_label = QLabel(
            "Min " + self.phase_plot.system.system_coords[1] + " ="
        )
        self.y_min_input = QLineEdit(str(self.phase_plot.axes_limits[1][0]))
        ylim_layout = QHBoxLayout()
        ylim_layout.addWidget(self.y_max_label)
        ylim_layout.addWidget(self.y_max_input)
        ylim_layout.addWidget(self.y_min_label)
        ylim_layout.addWidget(self.y_min_input)

        # Layouts
        x_prime_layout = QHBoxLayout()  # Input box for first equation
        y_prime_layout = QHBoxLayout()  # Input box for second equation
        button_layout = QHBoxLayout()

        self.parameter_layouts = (
            {}
        )  # Each layout contains two input boxes (parameter name and value) and an equals sign
        for param_num in range(self.no_of_params):
            self.parameter_layouts[
                "param_" + str(param_num) + "_layout"
            ] = QHBoxLayout()
            self.equals_sign = QLabel("=")
            self.parameter_layouts["param_" + str(param_num) + "_layout"].addWidget(
                self.parameter_input_boxes["param_" + str(param_num) + "_name"]
            )
            self.parameter_layouts["param_" + str(param_num) + "_layout"].addWidget(
                self.equals_sign
            )
            self.parameter_layouts["param_" + str(param_num) + "_layout"].addWidget(
                self.parameter_input_boxes["param_" + str(param_num) + "_val"]
            )

        x_prime_layout.addWidget(self.x_prime_label)
        x_prime_layout.addWidget(self.x_prime_entry)
        y_prime_layout.addWidget(self.y_prime_label)
        y_prime_layout.addWidget(self.y_prime_entry)

        button_layout.addStretch()
        button_layout.addWidget(self.plot_button)
        button_layout.addStretch()

        equation_entry_layout = QVBoxLayout()  # Contains input boxes for both eqations
        equation_entry_layout.addLayout(x_prime_layout)
        equation_entry_layout.addLayout(y_prime_layout)
        equation_entry_layout.addLayout(button_layout)

        self.parameters_layout = QVBoxLayout()  # Inputs for all parameters
        self.parameters_layout.addWidget(QLabel("Parameters (Optional) :"))
        for param_num in range(self.no_of_params):
            self.parameters_layout.addLayout(
                self.parameter_layouts["param_" + str(param_num) + "_layout"]
            )

        inputs_layout = QVBoxLayout()  # All input boxes
        inputs_layout.addLayout(equation_entry_layout)

        inputs_layout.addWidget(self.limits_heading)
        inputs_layout.addLayout(xlim_layout)
        inputs_layout.addLayout(ylim_layout)

        inputs_layout.addLayout(self.parameters_layout)
        inputs_layout.addStretch()

        plot_layout = QVBoxLayout()
        plot_layout.addWidget(NavigationToolbar(self.phase_plot, self))
        plot_layout.addWidget(self.phase_plot)

        self.overall_layout = QHBoxLayout()  # Input boxes and phase plot
        self.overall_layout.addLayout(inputs_layout)
        self.overall_layout.addLayout(plot_layout)

        cent_widget.setLayout(self.overall_layout)

        # Button Actions
        self.plot_button.clicked.connect(self.plot_button_clicked)

        # Set window title and show
        self.setWindowTitle("PyPLANE " + VERSION)
        self.show()

    def psp_canvas_default(self: QMainWindow, dimensions: int) -> None:
        """
        Initialises default PSP
        """
        if dimensions == 1:
            self.setup_dict = default_1D

        elif dimensions == 2:
            self.setup_dict = default_2D

        # Unpacks self.setup_dict into SOE.
        sys = SystemOfEquations(**self.setup_dict)
        self.phase_plot = PhaseSpacePlotter(sys, **self.setup_dict)

    def plot_button_clicked(self: QMainWindow) -> None:
        """
        Gathers phase_coords and passed_params to feed into GUI checks.
        If GUI checks pass, self.update_psp is called.
        Else, self.handle_empty_entry is called.
        """
        phase_coords = ["x", "y"]

        # Grab parameters
        passed_params = {}
        for param_num in range(self.no_of_params):
            if self.parameter_input_boxes["param_" + str(param_num) + "_name"].text():
                passed_params[
                    self.parameter_input_boxes[
                        "param_" + str(param_num) + "_name"
                    ].text()
                ] = self.parameter_input_boxes[
                    "param_" + str(param_num) + "_val"
                ].text()

        # print(self.parameter_input_boxes)

        try:
            self.update_psp(phase_coords, passed_params)

        except ParameterTypeError as pte:
            print(pte.message)
            self.handle_pte(pte.args)

        except ParameterValidityError as pve:
            print(pve.message)
            self.handle_pve(pve.args)

        except LimitTypeError as lte:
            print(lte.message)
            self.handle_lte(lte.args)

        except LimitMagnitudeError as lme:
            print(lme.message)
            self.handle_lme(lme.args)

        except PPException as ppe:
            print(ppe.message)

        except Exception as e:
            print("Generic Exception caught:")
            print(e)

    def update_psp(self: QMainWindow, phase_coords: list, passed_params: dict) -> None:
        """
        Gathers entry information from GUI and updates phase plot
        """
        f_1 = self.x_prime_entry.text()
        f_2 = self.y_prime_entry.text()
        eqns = [f_1, f_2]

        system_of_eqns = SystemOfEquations(phase_coords, eqns, params=passed_params)

        self.action_nullclines.setChecked(False)

        x_min = float(self.x_min_input.text())
        x_max = float(self.x_max_input.text())
        y_min = float(self.y_min_input.text())
        y_max = float(self.y_max_input.text())

        self.phase_plot.update_system(
            system_of_eqns, axes_limits=((x_min, x_max), (y_min, y_max))
        )

    def handle_pte(self: QMainWindow, pte_args: tuple) -> None:
        self.plot_button.setProperty("warning-indicator", True)

    def handle_pve(self: QMainWindow, pve_args: tuple) -> None:
        print(pve_args)
        print(type(pve_args))

    def handle_lte(self: QMainWindow, lte_args: tuple) -> None:
        print(lte_args)
        print(type(lte_args))

    def handle_lme(self: QMainWindow, lme_args: tuple) -> None:
        print(lme_args)
        print(type(lme_args))


if __name__ == "__main__":
    PyPLANE = QApplication(sys.argv)
    PyPLANE_main_window = MainWindow()
    sys.exit(PyPLANE.exec_())
