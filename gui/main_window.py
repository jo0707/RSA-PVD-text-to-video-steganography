from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QTabWidget, QLabel, QLineEdit, QStackedWidget)
from PyQt6.QtCore import Qt
import os
from . import constants as c
from .widgets import PrimaryButton, SecondaryButton, FileInput, MessageLabel
import src.rsa as rsa
import src.pvd as pvd
import src.video_parser as video_parser
import main

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RSA-PVD Steganography")
        self.setMinimumSize(c.WINDOW_WIDTH, c.WINDOW_HEIGHT)
        
        # Initialize RSA keys
        rsa.generate_rsa_keys()
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Create tab widget
        tabs = QTabWidget()
        main_layout.addWidget(tabs)
        
        # Create tabs for different operations
        video_tab = self.create_video_tab()
        image_tab = self.create_image_tab()
        
        tabs.addTab(video_tab, "Video Steganography")
        tabs.addTab(image_tab, "Image Steganography")
        
        # Status message label
        self.status_label = MessageLabel()
        main_layout.addWidget(self.status_label)
    
    def create_video_tab(self):
        video_widget = QWidget()
        layout = QVBoxLayout(video_widget)
        layout.setSpacing(c.PADDING)
        
        # Input video section
        self.video_input = FileInput("Select input video file...")
        browse_video_btn = SecondaryButton("Browse")
        browse_video_btn.clicked.connect(
            lambda: self.video_input.browse_file("Video Files (*.mp4 *.avi)")
        )
        
        # Message input
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Enter message to hide...")
        self.message_input.setStyleSheet(
            """
            QLineEdit {
                padding: 8px;
                border: 1px solid #BDBDBD;
                border-radius: 4px;
                font-size: 14px;
            }
            """
        )
        
        # Layout for input fields
        input_layout = QVBoxLayout()
        for widget, label, browse_btn in [
            (self.video_input, "Input Video:", browse_video_btn),
            (self.message_input, "Message:", None)
        ]:
            row = QHBoxLayout()
            row.addWidget(QLabel(label))
            row.addWidget(widget)
            if browse_btn:
                row.addWidget(browse_btn)
            input_layout.addLayout(row)
        
        layout.addLayout(input_layout)
        
        # Buttons
        btn_layout = QHBoxLayout()
        encrypt_btn = PrimaryButton("Encrypt and Hide")
        decrypt_btn = PrimaryButton("Extract and Decrypt")
        
        encrypt_btn.clicked.connect(self.encrypt_video)
        decrypt_btn.clicked.connect(self.decrypt_video)
        
        btn_layout.addWidget(encrypt_btn)
        btn_layout.addWidget(decrypt_btn)
        layout.addLayout(btn_layout)
        
        layout.addStretch()
        return video_widget
    
    def create_image_tab(self):
        image_widget = QWidget()
        layout = QVBoxLayout(image_widget)
        layout.setSpacing(c.PADDING)
        
        # Input image section
        self.image_input = FileInput("Select input image file...")
        browse_image_btn = SecondaryButton("Browse")
        browse_image_btn.clicked.connect(
            lambda: self.image_input.browse_file("Image Files (*.png *.jpg *.jpeg)")
        )
        
        # Message input for image
        self.image_message_input = QLineEdit()
        self.image_message_input.setPlaceholderText("Enter message to hide...")
        self.image_message_input.setStyleSheet(
            """
            QLineEdit {
                padding: 8px;
                border: 1px solid #BDBDBD;
                border-radius: 4px;
                font-size: 14px;
            }
            """
        )
        
        # Layout for input fields
        input_layout = QVBoxLayout()
        for widget, label, browse_btn in [
            (self.image_input, "Input Image:", browse_image_btn),
            (self.image_message_input, "Message:", None)
        ]:
            row = QHBoxLayout()
            row.addWidget(QLabel(label))
            row.addWidget(widget)
            if browse_btn:
                row.addWidget(browse_btn)
            input_layout.addLayout(row)
        
        layout.addLayout(input_layout)
        
        # Buttons
        btn_layout = QHBoxLayout()
        encrypt_btn = PrimaryButton("Encrypt and Hide")
        decrypt_btn = PrimaryButton("Extract and Decrypt")
        
        encrypt_btn.clicked.connect(self.encrypt_image)
        decrypt_btn.clicked.connect(self.decrypt_image)
        
        btn_layout.addWidget(encrypt_btn)
        btn_layout.addWidget(decrypt_btn)
        layout.addLayout(btn_layout)
        
        layout.addStretch()
        return image_widget
    
    def encrypt_video(self):
        try:
            video_path = self.video_input.text() or c.VIDEO_PATH
            output_path = c.OUTPUT_VIDEO_PATH
            message = self.message_input.text() or "Test message"
            
            main.encrypt_video(video_path, message, output_path)
            
            self.status_label.show_success(
                f"Message encrypted and hidden in video: {output_path}"
            )
            
            # open the output video folder
            os.startfile(os.path.dirname(output_path))
        except Exception as e:
            self.status_label.show_error(f"Error: {str(e)}")

    def decrypt_video(self):
        try:
            video_path = self.video_input.text() or c.OUTPUT_VIDEO_PATH
            
            decrypted_message = main.decrypt_video(video_path)
            
            self.message_input.setText(decrypted_message)
            self.status_label.show_success(f"Message successfully extracted and decrypted! Message: {decrypted_message}")
        except Exception as e:
            self.status_label.show_error(f"Error: {str(e)}")
    
    def encrypt_image(self):
        try:
            image_path = self.image_input.text() or c.IMAGE_PATH
            input_filename = os.path.splitext(os.path.basename(image_path))[0]
            output_path = c.OUTPUT_IMAGE_PATH
            message = self.image_message_input.text() or "Test message"
            
            # Create output directory if it doesn't exist
            os.makedirs(c.OUTPUT_DIR, exist_ok=True)
            
            # Encrypt and embed
            encrypted_message = rsa.encrypt_message_base64(message)
            pvd.embed_pvd(image_path, encrypted_message, output_path)
            
            self.status_label.show_success(
                f"Message encrypted and hidden in image: {output_path}"
            )
            
            # open the output image folder
            os.startfile(os.path.dirname(output_path))
        except Exception as e:
            self.status_label.show_error(f"Error: {str(e)}")
    
    def decrypt_image(self):
        try:
            image_path = self.image_input.text()
            if not image_path:
                self.status_label.show_error("Please select an image file to decrypt")
                return
            
            # Extract and decrypt
            extracted_message = pvd.extract_pvd(image_path)
            decrypted_message = rsa.decrypt_message_base64(extracted_message)
            
            self.image_message_input.setText(decrypted_message)
            self.status_label.show_success("Message successfully extracted and decrypted!")
        except Exception as e:
            self.status_label.show_error(f"Error: {str(e)}")