from PyQt6.QtWidgets import (QPushButton, QLabel, QLineEdit, QFileDialog)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from . import constants as c

class PrimaryButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {c.PRIMARY_COLOR};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 14px;
                min-height: {c.BUTTON_HEIGHT}px;
            }}
            QPushButton:hover {{
                background-color: #1976D2;
            }}
            QPushButton:pressed {{
                background-color: #0D47A1;
            }}
            """
        )

class SecondaryButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet(
            f"""
            QPushButton {{
                background-color: white;
                color: {c.PRIMARY_COLOR};
                border: 2px solid {c.PRIMARY_COLOR};
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 14px;
                min-height: {c.BUTTON_HEIGHT}px;
            }}
            QPushButton:hover {{
                background-color: #E3F2FD;
            }}
            QPushButton:pressed {{
                background-color: #BBDEFB;
            }}
            """
        )

class FileInput(QLineEdit):
    def __init__(self, placeholder="Select file...", parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setStyleSheet(
            """
            QLineEdit {
                padding: 8px;
                border: 1px solid #BDBDBD;
                border-radius: 4px;
                background: white;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #2196F3;
            }
            """
        )

    def browse_file(self, file_type="All Files (*.*)", start_dir="."):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select File", start_dir, file_type
        )
        if file_path:
            self.setText(file_path)
            return file_path
        return None

class MessageLabel(QLabel):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setWordWrap(True)
        self.setStyleSheet(
            """
            QLabel {
                padding: 8px;
                border-radius: 4px;
                font-size: 14px;
            }
            """
        )
        self.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.hide()

    def show_success(self, message):
        self.setText(message)
        self.setStyleSheet(
            f"""
            QLabel {{
                background-color: {c.SUCCESS_COLOR};
                color: white;
                padding: 8px;
                border-radius: 4px;
                font-size: 14px;
            }}
            """
        )
        self.show()

    def show_error(self, message):
        self.setText(message)
        self.setStyleSheet(
            f"""
            QLabel {{
                background-color: {c.ERROR_COLOR};
                color: white;
                padding: 8px;
                border-radius: 4px;
                font-size: 14px;
            }}
            """
        )
        self.show()