import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, 
                             QWidget, QFileDialog, QLabel, QLineEdit, QMessageBox, QTextEdit, 
                             QStackedWidget, QDialog)
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt
import fitz  # PyMuPDF
from analyser import get_suggested_name

class RenameConfirmDialog(QDialog):
    def __init__(self, current_name, suggested_name, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Confirm Rename")
        self.layout = QVBoxLayout()
        
        self.label = QLabel(f"Rename '{current_name}' to:")
        self.layout.addWidget(self.label)
        
        self.name_edit = QLineEdit(suggested_name)
        self.layout.addWidget(self.name_edit)
        
        self.buttons = QHBoxLayout()
        self.ok_button = QPushButton("Confirm")
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        self.buttons.addWidget(self.ok_button)
        self.buttons.addWidget(self.cancel_button)
        self.layout.addLayout(self.buttons)
        
        self.setLayout(self.layout)

    def get_new_name(self):
        return self.name_edit.text()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("File Renamer AI")
        self.resize(1000, 700)
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        
        self.select_button = QPushButton("Select File or Directory")
        self.select_button.clicked.connect(self.on_select_clicked)
        self.layout.addWidget(self.select_button)
        
        self.content_area = QHBoxLayout()
        self.layout.addLayout(self.content_area)
        
        self.preview_label = QLabel("Preview will appear here")
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setStyleSheet("border: 1px solid gray;")
        self.preview_label.setMinimumSize(400, 500)
        self.content_area.addWidget(self.preview_label, 2)
        
        self.text_preview = QTextEdit()
        self.text_preview.setPlaceholderText("Selectable text from file will appear here...")
        self.content_area.addWidget(self.text_preview, 1)
        
        self.suggestion_layout = QHBoxLayout()
        self.layout.addLayout(self.suggestion_layout)
        
        self.suggestion_label = QLabel("Suggested Name:")
        self.suggestion_layout.addWidget(self.suggestion_label)
        
        self.suggestion_edit = QLineEdit()
        self.suggestion_layout.addWidget(self.suggestion_edit)
        
        self.rename_button = QPushButton("Rename")
        self.rename_button.clicked.connect(self.on_rename_clicked)
        self.layout.addWidget(self.rename_button)
        
        self.files_to_process = []
        self.current_file_index = -1

    def on_select_clicked(self):
        choice = QMessageBox.question(self, "Select Type", "Do you want to select a Directory?", 
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
                                     QMessageBox.StandardButton.No)
        
        if choice == QMessageBox.StandardButton.Yes:
            dir_path = QFileDialog.getExistingDirectory(self, "Select Directory")
            if dir_path:
                self.files_to_process = [os.path.join(dir_path, f) for f in os.listdir(dir_path) 
                                         if os.path.isfile(os.path.join(dir_path, f)) and not f.startswith(".")]
                if self.files_to_process:
                    self.current_file_index = 0
                    self.load_file(self.files_to_process[0])
        else:
            file_path, _ = QFileDialog.getOpenFileName(self, "Select File")
            if file_path:
                self.files_to_process = [file_path]
                self.current_file_index = 0
                self.load_file(file_path)

    def load_file(self, filepath):
        self.setWindowTitle(f"File Renamer AI - Processing {os.path.basename(filepath)}")
        ext = os.path.splitext(filepath)[1].lower()
        
        # Clear previous previews
        self.preview_label.clear()
        self.text_preview.clear()
        
        if ext == ".pdf":
            self.preview_pdf(filepath)
        elif ext in [".jpg", ".jpeg", ".png"]:
            self.preview_image(filepath)
        else:
            self.preview_label.setText("No preview available for this file type.")
            
        suggested_name = get_suggested_name(filepath)
        self.suggestion_edit.setText(suggested_name)

    def preview_pdf(self, filepath):
        try:
            doc = fitz.open(filepath)
            page = doc[0]
            pix = page.get_pixmap()
            
            # Convert pixmap to QImage
            img = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(img)
            self.preview_label.setPixmap(pixmap.scaled(self.preview_label.size(), 
                                                     Qt.AspectRatioMode.KeepAspectRatio, 
                                                     Qt.TransformationMode.SmoothTransformation))
            
            # Extract text for the text area
            text = page.get_text()
            self.text_preview.setText(text)
            doc.close()
        except Exception as e:
            self.preview_label.setText(f"Error loading PDF: {e}")

    def preview_image(self, filepath):
        try:
            pixmap = QPixmap(filepath)
            self.preview_label.setPixmap(pixmap.scaled(self.preview_label.size(), 
                                                     Qt.AspectRatioMode.KeepAspectRatio, 
                                                     Qt.TransformationMode.SmoothTransformation))
            self.text_preview.setText("Images don't contain selectable text in this version.")
        except Exception as e:
            self.preview_label.setText(f"Error loading image: {e}")

    def on_rename_clicked(self):
        if self.current_file_index < 0 or not self.files_to_process:
            return
        
        old_path = self.files_to_process[self.current_file_index]
        suggested_name = self.suggestion_edit.text()
        
        dialog = RenameConfirmDialog(os.path.basename(old_path), suggested_name, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_name = dialog.get_new_name()
            new_path = os.path.join(os.path.dirname(old_path), new_name)
            
            try:
                os.rename(old_path, new_path)
                QMessageBox.information(self, "Success", f"File renamed to {new_name}")
                self.process_next_file()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not rename file: {e}")

    def process_next_file(self):
        self.current_file_index += 1
        if self.current_file_index < len(self.files_to_process):
            self.load_file(self.files_to_process[self.current_file_index])
        else:
            QMessageBox.information(self, "Finished", "All files processed.")
            self.current_file_index = -1
            self.files_to_process = []
            self.preview_label.setText("Preview will appear here")
            self.text_preview.clear()
            self.suggestion_edit.clear()
            self.setWindowTitle("File Renamer AI")

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
