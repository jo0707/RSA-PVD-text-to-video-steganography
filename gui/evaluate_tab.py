from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                            QPushButton, QLabel, QFileDialog, QTextEdit,
                            QProgressBar, QTableWidget, QTableWidgetItem)
from PyQt6.QtCore import Qt, pyqtSlot, QThread, pyqtSignal
import os
import cv2
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from src import pvd, rsa, video_parser

class EvaluateWorker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, original_video, stego_video):
        super().__init__()
        self.original_video = original_video
        self.stego_video = stego_video

    def calculate_psnr(self, original, modified):
        mse = np.mean((original - modified) ** 2)
        if mse == 0:
            return float('inf')
        max_pixel = 255.0
        psnr = 20 * np.log10(max_pixel / np.sqrt(mse))
        return psnr

    def run(self):
        try:
            # Read first frames
            cap_original = cv2.VideoCapture(self.original_video)
            cap_stego = cv2.VideoCapture(self.stego_video)
            
            ret1, frame1 = cap_original.read()
            ret2, frame2 = cap_stego.read()
            
            if ret1 and ret2:
                psnr = self.calculate_psnr(frame1, frame2)
                
                # Calculate other metrics if needed
                results = {
                    'PSNR': psnr,
                    'File Size Original (MB)': os.path.getsize(self.original_video) / (1024 * 1024),
                    'File Size Stego (MB)': os.path.getsize(self.stego_video) / (1024 * 1024)
                }
                
                self.finished.emit(results)
            else:
                self.error.emit("Could not read video frames")
                
            cap_original.release()
            cap_stego.release()
            
        except Exception as e:
            self.error.emit(str(e))

class EvaluateTab(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.worker = None

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)

        # File selection
        file_layout = QVBoxLayout()
        
        # Original video selection
        original_layout = QHBoxLayout()
        self.original_path_label = QLabel("No original video selected")
        select_original_btn = QPushButton("Select Original Video")
        select_original_btn.clicked.connect(self.select_original)
        original_layout.addWidget(self.original_path_label, stretch=1)
        original_layout.addWidget(select_original_btn)
        file_layout.addLayout(original_layout)

        # Stego video selection
        stego_layout = QHBoxLayout()
        self.stego_path_label = QLabel("No stego video selected")
        select_stego_btn = QPushButton("Select Stego Video")
        select_stego_btn.clicked.connect(self.select_stego)
        stego_layout.addWidget(self.stego_path_label, stretch=1)
        stego_layout.addWidget(select_stego_btn)
        file_layout.addLayout(stego_layout)
        
        layout.addLayout(file_layout)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Evaluate button
        self.evaluate_btn = QPushButton("Evaluate")
        self.evaluate_btn.clicked.connect(self.start_evaluation)
        self.evaluate_btn.setEnabled(False)
        layout.addWidget(self.evaluate_btn)

        # Results table
        self.results_table = QTableWidget(0, 2)
        self.results_table.setHorizontalHeaderLabels(['Metric', 'Value'])
        self.results_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.results_table)

        # Plot area
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        # Status label
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

    def select_original(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Original Video", "", "Video Files (*.mp4 *.avi)"
        )
        if file_path:
            self.original_path_label.setText(file_path)
            self.check_enable_evaluate()

    def select_stego(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Stego Video", "", "Video Files (*.mp4 *.avi)"
        )
        if file_path:
            self.stego_path_label.setText(file_path)
            self.check_enable_evaluate()

    def check_enable_evaluate(self):
        has_original = self.original_path_label.text() != "No original video selected"
        has_stego = self.stego_path_label.text() != "No stego video selected"
        self.evaluate_btn.setEnabled(has_original and has_stego)

    def start_evaluation(self):
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.evaluate_btn.setEnabled(False)
        self.status_label.setText("Evaluating...")
        self.results_table.setRowCount(0)

        self.worker = EvaluateWorker(
            self.original_path_label.text(),
            self.stego_path_label.text()
        )
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.evaluation_finished)
        self.worker.error.connect(self.evaluation_error)
        self.worker.start()

    def update_results_table(self, results):
        self.results_table.setRowCount(len(results))
        for i, (metric, value) in enumerate(results.items()):
            self.results_table.setItem(i, 0, QTableWidgetItem(metric))
            self.results_table.setItem(i, 1, QTableWidgetItem(f"{value:.2f}"))

    @pyqtSlot(int)
    def update_progress(self, value):
        self.progress_bar.setValue(value)

    @pyqtSlot(dict)
    def evaluation_finished(self, results):
        self.update_results_table(results)
        self.status_label.setText("Evaluation completed!")
        self.progress_bar.setVisible(False)
        self.evaluate_btn.setEnabled(True)
        
        # Update plot
        self.ax.clear()
        metrics = list(results.keys())
        values = list(results.values())
        self.ax.bar(metrics, values)
        self.ax.set_title('Evaluation Results')
        self.ax.tick_params(axis='x', rotation=45)
        self.figure.tight_layout()
        self.canvas.draw()

    @pyqtSlot(str)
    def evaluation_error(self, error_message):
        self.status_label.setText(f"Error: {error_message}")
        self.progress_bar.setVisible(False)
        self.evaluate_btn.setEnabled(True)