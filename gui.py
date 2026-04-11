import sys
import os
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QFileDialog,
    QLabel,
    QLineEdit,
    QMessageBox,
    QTextEdit,
    QDialog,
    QListWidget,
)
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt
import fitz  # PyMuPDF
from analyser import get_suggested_name, get_file_date


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
        self.resize(1100, 700)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.select_button = QPushButton("Select File or Directory")
        self.select_button.clicked.connect(self.on_select_clicked)
        self.layout.addWidget(self.select_button)

        self.content_area = QHBoxLayout()
        self.layout.addLayout(self.content_area)

        # File list for directory selection
        self.file_list = QListWidget()
        self.file_list.setMaximumWidth(250)
        self.content_area.addWidget(self.file_list)

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

        self.date_label = QLabel("File Date: N/A")
        self.suggestion_layout.addWidget(self.date_label)

        self.suggestion_label = QLabel("Suggested Name:")
        self.suggestion_layout.addWidget(self.suggestion_label)

        self.suggestion_edit = QLineEdit()
        self.suggestion_layout.addWidget(self.suggestion_edit)

        # Filename manipulation buttons
        self.filename_tools_layout = QHBoxLayout()
        self.titlecase_button = QPushButton("Titlecase filename")
        self.titlecase_button.clicked.connect(self.on_titlecase_clicked)
        self.underscore_button = QPushButton("Underscore filename")
        self.underscore_button.clicked.connect(self.on_underscore_clicked)
        self.filename_tools_layout.addWidget(self.titlecase_button)
        self.filename_tools_layout.addWidget(self.underscore_button)
        self.layout.addLayout(self.filename_tools_layout)

        self.actions_layout = QHBoxLayout()
        self.rename_button = QPushButton("Rename")
        self.rename_button.clicked.connect(self.on_rename_clicked)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.on_cancel_clicked)
        self.actions_layout.addWidget(self.rename_button)
        self.actions_layout.addWidget(self.cancel_button)
        self.layout.addLayout(self.actions_layout)

        self.files_to_process = []
        self.current_file_index = -1

    def on_select_clicked(self):
        choice = QMessageBox.question(
            self,
            "Select Type",
            "Do you want to select a Directory?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        self.file_list.clear()

        if choice == QMessageBox.StandardButton.Yes:
            dir_path = QFileDialog.getExistingDirectory(self, "Select Directory")
            if dir_path:
                self.files_to_process = sorted([
                    os.path.join(dir_path, f)
                    for f in os.listdir(dir_path)
                    if os.path.isfile(os.path.join(dir_path, f)) and not f.startswith(".")
                ])
                if self.files_to_process:
                    for f in self.files_to_process:
                        self.file_list.addItem(os.path.basename(f))
                    self.current_file_index = 0
                    self.load_file(self.files_to_process[0])
        else:
            file_path, _ = QFileDialog.getOpenFileName(self, "Select File")
            if file_path:
                self.files_to_process = [file_path]
                self.file_list.addItem(os.path.basename(file_path))
                self.current_file_index = 0
                self.load_file(file_path)

    def load_file(self, filepath):
        self.setWindowTitle(f"File Renamer AI - Processing {os.path.basename(filepath)}")
        # Highlight in list
        if self.current_file_index >= 0:
            self.file_list.setCurrentRow(self.current_file_index)

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
        self.date_label.setText(f"File Date: {get_file_date(filepath)}")

    def preview_pdf(self, filepath):
        try:
            doc = fitz.open(filepath)
            page = doc[0]
            pix = page.get_pixmap()

            # Convert pixmap to QImage
            img = QImage(
                pix.samples, pix.width, pix.height, pix.stride, QImage.Format.Format_RGB888
            )
            pixmap = QPixmap.fromImage(img)
            self.preview_label.setPixmap(
                pixmap.scaled(
                    self.preview_label.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )

            # Extract text for the text area
            text = page.get_text()
            self.text_preview.setText(text)
            doc.close()
        except Exception as e:
            self.preview_label.setText(f"Error loading PDF: {e}")

    def preview_image(self, filepath):
        try:
            pixmap = QPixmap(filepath)
            self.preview_label.setPixmap(
                pixmap.scaled(
                    self.preview_label.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )
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
                # Update list item and current files to process
                item = self.file_list.item(self.current_file_index)
                if item:
                    item.setText(new_name)
                self.files_to_process[self.current_file_index] = new_path

                self.process_next_file()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not rename file: {e}")

    def on_cancel_clicked(self):
        if self.current_file_index >= 0:
            self.process_next_file()

    def on_titlecase_clicked(self):
        filename = self.suggestion_edit.text()
        if not filename:
            return
        name, ext = os.path.splitext(filename)
        # Handle underscores explicitly if needed, but .title() handles them
        # "dwelling_insurance".title() -> "Dwelling_Insurance"
        # However, it also titlecases things like "pdf" -> "Pdf"
        # and it might lower other chars.
        # Let's use a more careful approach if needed, or just .title() on name part.
        new_name = name.title() + ext
        self.suggestion_edit.setText(new_name)

    def on_underscore_clicked(self):
        filename = self.suggestion_edit.text()
        if not filename:
            return
        new_name = filename.replace(" ", "_")
        self.suggestion_edit.setText(new_name)

    def process_next_file(self):
        self.current_file_index += 1
        if self.current_file_index < len(self.files_to_process):
            self.load_file(self.files_to_process[self.current_file_index])
        else:
            QMessageBox.information(self, "Finished", "All files processed.")
            self.current_file_index = -1
            self.files_to_process = []
            self.file_list.clear()
            self.preview_label.setText("Preview will appear here")
            self.text_preview.clear()
            self.suggestion_edit.clear()
            self.date_label.setText("File Date: N/A")
            self.setWindowTitle("File Renamer AI")


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
