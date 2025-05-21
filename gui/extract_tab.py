from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                            QPushButton, QLabel, QFileDialog, QTextEdit,
                            QProgressBar)
from PyQt6.QtCore import Qt, pyqtSlot, QThread, pyqtSignal
import os
from src import pvd, rsa, video_parser
import cv2

class ExtractWorker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, video_path):
        super().__init__()
        self.video_path = video_path

    def run(self):
        try:
            # Load the private key
            with open('keys/private_key.pem', 'rb') as key_file:
                private_key = key_file.read()
            
            # Read first frame of video
            cap = cv2.VideoCapture(self.video_path)
            ret, frame = cap.read()
            cap.release()
            
            if not ret:
                raise Exception("Could not read video frame")
            
            self.progress.emit(30)
            
            # Extract encrypted message from frame
            encrypted_message = pvd.extract_data(frame)
            
            self.progress.emit(60)
            
            # Decrypt the message using RSA
            decrypted_message = rsa.decrypt_message(encrypted_message, private_key)
            
            self.progress.emit(100)
            self.finished.emit(decrypted_message)
            
        except Exception as e:
            self.error.emit(str(e))

class ExtractTab(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.worker = None

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)

        # Video selection
        video_layout = QHBoxLayout()
        self.video_path_label = QLabel("No video selected")
        select_video_btn = QPushButton("Select Video")
        select_video_btn.clicked.connect(self.select_video)
        video_layout.addWidget(self.video_path_label, stretch=1)
        video_layout.addWidget(select_video_btn)
        layout.addLayout(video_layout)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Extract button
        self.extract_btn = QPushButton("Extract Message")
        self.extract_btn.clicked.connect(self.start_extracting)
        self.extract_btn.setEnabled(False)
        layout.addWidget(self.extract_btn)

        # Extracted message display
        layout.addWidget(QLabel("Extracted Message:"))
        self.message_display = QTextEdit()
        self.message_display.setReadOnly(True)
        self.message_display.setPlaceholderText("Extracted message will appear here...")
        layout.addWidget(self.message_display)

        # Status label
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

        layout.addStretch()

    def select_video(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Video", "", "Video Files (*.mp4 *.avi)"
        )
        if file_path:
            self.video_path_label.setText(file_path)
            self.extract_btn.setEnabled(True)

    def start_extracting(self):
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.extract_btn.setEnabled(False)
        self.status_label.setText("Extracting message...")
        self.message_display.clear()

        self.worker = ExtractWorker(self.video_path_label.text())
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.extracting_finished)
        self.worker.error.connect(self.extracting_error)
        self.worker.start()

    @pyqtSlot(int)
    def update_progress(self, value):
        self.progress_bar.setValue(value)

    @pyqtSlot(str)
    def extracting_finished(self, message):
        self.message_display.setText(message)
        self.status_label.setText("Message extracted successfully!")
        self.progress_bar.setVisible(False)
        self.extract_btn.setEnabled(True)

    @pyqtSlot(str)
    def extracting_error(self, error_message):
        self.status_label.setText(f"Error: {error_message}")
        self.progress_bar.setVisible(False)
        self.extract_btn.setEnabled(True)