from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QFileDialog,
                            QTextEdit, QProgressBar, QTabWidget)
from PyQt6.QtCore import Qt, pyqtSlot, QThread, pyqtSignal
from PyQt6.QtGui import QIcon, QPixmap
import os
from .embed_tab import EmbedTab
from .extract_tab import ExtractTab
from .evaluate_tab import EvaluateTab

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RSA-PVD Video Steganography")
        self.setMinimumSize(800, 600)
        
        # Create the main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # Create tab widget
        tabs = QTabWidget()
        
        # Add tabs
        self.embed_tab = EmbedTab()
        self.extract_tab = ExtractTab()
        self.evaluate_tab = EvaluateTab()
        
        tabs.addTab(self.embed_tab, "Embed Message")
        tabs.addTab(self.extract_tab, "Extract Message")
        tabs.addTab(self.evaluate_tab, "Evaluate Results")
        
        layout.addWidget(tabs)
        
        # Status bar
        self.statusBar().showMessage("Ready")
        
        # Set style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QTabWidget::pane {
                border: 1px solid #cccccc;
                background: white;
                border-radius: 4px;
            }
            QTabBar::tab {
                background: #e1e1e1;
                padding: 8px 12px;
                border: 1px solid #cccccc;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background: white;
            }
            QPushButton {
                background-color: #0078D4;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #106EBE;
            }
            QPushButton:pressed {
                background-color: #005A9E;
            }
            QProgressBar {
                border: 1px solid #cccccc;
                border-radius: 4px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #0078D4;
            }
        """)