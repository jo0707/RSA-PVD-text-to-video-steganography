from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                            QPushButton, QLabel, QFileDialog, QTextEdit,
                            QProgressBar)
from PyQt6.QtCore import Qt, pyqtSlot, QThread, pyqtSignal
from PyQt6.QtGui import QIcon, QPixmap
import os
import cv2
from src import pvd, rsa, video_parser

class EmbedWorker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, video_path, message, output_path):
        super().__init__()
        self.video_path = video_path
        self.message = message
        self.output_path = output_path

    def run(self):
        try:
            # Load the public key
            with open('keys/public_key.pem', 'rb') as key_file:
                public_key = key_file.read()
            
            # First encrypt the message using RSA
            encrypted_message = rsa.encrypt_message(self.message, public_key)
            
            # Create video frames and embed the message
            self.progress.emit(10)
            
            # Parse video into frames
            cap = cv2.VideoCapture(self.video_path)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            size = (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), 
                   int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
            
            # Create VideoWriter
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(self.output_path, fourcc, fps, size)
            
            # Read first frame for embedding
            ret, frame = cap.read()
            if not ret:
                raise Exception("Could not read video frame")
                
            self.progress.emit(30)
            
            # Embed message in first frame
            stego_frame = pvd.embed_data(frame, encrypted_message)
            out.write(stego_frame)
            
            self.progress.emit(60)
            
            # Copy remaining frames
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                out.write(frame)
            
            cap.release()
            out.release()
            
            self.progress.emit(100)
            self.finished.emit("Message embedded successfully!")
            
        except Exception as e:
            self.error.emit(str(e))

class EmbedTab(QWidget):
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

        # Message input
        layout.addWidget(QLabel("Enter Message:"))
        self.message_text = QTextEdit()
        self.message_text.setPlaceholderText("Type your secret message here...")
        layout.addWidget(self.message_text)

        # Output path selection
        output_layout = QHBoxLayout()
        self.output_path_label = QLabel("No output location selected")
        select_output_btn = QPushButton("Select Output Location")
        select_output_btn.clicked.connect(self.select_output)
        output_layout.addWidget(self.output_path_label, stretch=1)
        output_layout.addWidget(select_output_btn)
        layout.addLayout(output_layout)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Embed button
        self.embed_btn = QPushButton("Embed Message")
        self.embed_btn.clicked.connect(self.start_embedding)
        self.embed_btn.setEnabled(False)
        layout.addWidget(self.embed_btn)

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
            self.check_enable_embed()

    def select_output(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Output Video", "", "Video Files (*.mp4)"
        )
        if file_path:
            self.output_path_label.setText(file_path)
            self.check_enable_embed()

    def check_enable_embed(self):
        has_video = self.video_path_label.text() != "No video selected"
        has_output = self.output_path_label.text() != "No output location selected"
        has_message = len(self.message_text.toPlainText().strip()) > 0
        self.embed_btn.setEnabled(has_video and has_output and has_message)

    def start_embedding(self):
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.embed_btn.setEnabled(False)
        self.status_label.setText("Embedding message...")

        self.worker = EmbedWorker(
            self.video_path_label.text(),
            self.message_text.toPlainText(),
            self.output_path_label.text()
        )
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.embedding_finished)
        self.worker.error.connect(self.embedding_error)
        self.worker.start()

    @pyqtSlot(int)
    def update_progress(self, value):
        self.progress_bar.setValue(value)

    @pyqtSlot(str)
    def embedding_finished(self, message):
        self.status_label.setText(message)
        self.progress_bar.setVisible(False)
        self.embed_btn.setEnabled(True)

    @pyqtSlot(str)
    def embedding_error(self, error_message):
        self.status_label.setText(f"Error: {error_message}")
        self.progress_bar.setVisible(False)
        self.embed_btn.setEnabled(True)