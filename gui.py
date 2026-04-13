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
    QFrame,
    QSplitter,
)
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt
import fitz  # PyMuPDF
from analyser import get_suggested_name, get_file_date, get_unique_path

# --- STYLING ---
DARK_THEME = """
QMainWindow, QDialog {
    background-color: #0F111A;
}

QWidget {
    background-color: transparent;
    color: #E0E0E0;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}

QFrame#Sidebar {
    background-color: #171923;
    border-right: 1px solid #2D3748;
}

QFrame#ControlCard {
    background-color: #1A202C;
    border: 1px solid #2D3748;
    border-radius: 12px;
}

QFrame#PreviewArea {
    background-color: #0F111A;
    border: 1px solid #2D3748;
    border-radius: 8px;
}

QListWidget {
    background-color: transparent;
    border: none;
    outline: none;
    padding: 10px;
}

QListWidget::item {
    padding: 12px;
    border-radius: 6px;
    margin-bottom: 4px;
    color: #A0AEC0;
}

QListWidget::item:selected {
    background-color: #2D3748;
    color: #BB86FC;
    font-weight: bold;
}

QListWidget::item:hover {
    background-color: #2A2D37;
}

QLineEdit {
    background-color: #2D3748;
    border: 1px solid #4A5568;
    border-radius: 6px;
    padding: 8px 12px;
    color: #F7FAFC;
    font-size: 14px;
}

QLineEdit:focus {
    border: 1px solid #BB86FC;
}

QTextEdit {
    background-color: #171923;
    border: 1px solid #2D3748;
    border-radius: 8px;
    padding: 10px;
    color: #CBD5E0;
    font-family: 'JetBrains Mono', 'Consolas', monospace;
}

QLabel#HeaderTitle {
    font-size: 24px;
    font-weight: 800;
    color: #F7FAFC;
}

QLabel#SectionLabel {
    font-size: 12px;
    font-weight: 700;
    color: #718096;
    text-transform: uppercase;
    letter-spacing: 1px;
}

QLabel#DateLabel {
    font-size: 13px;
    color: #A0AEC0;
}

QPushButton {
    padding: 10px 20px;
    border-radius: 6px;
    font-weight: 600;
    font-size: 14px;
}

QPushButton#PrimaryAction {
    background-color: #BB86FC;
    color: #000000;
}

QPushButton#PrimaryAction:hover {
    background-color: #D6BCFA;
}

QPushButton#PrimaryAction:pressed {
    background-color: #9F7AEA;
}

QPushButton#SecondaryAction {
    background-color: #2D3748;
    color: #E2E8F0;
    border: 1px solid #4A5568;
}

QPushButton#SecondaryAction:hover {
    background-color: #4A5568;
}

QPushButton#SelectAction {
    background-color: #1A202C;
    border: 2px dashed #4A5568;
    color: #A0AEC0;
}

QPushButton#SelectAction:hover {
    border-color: #BB86FC;
    color: #BB86FC;
}

QPushButton#CancelAction {
    background-color: transparent;
    color: #FC8181;
    border: 1px solid #FC8181;
}

QPushButton#CancelAction:hover {
    background-color: #FFF5F5;
    color: #E53E3E;
}

QPushButton#ToolAction {
    background-color: transparent;
    border: 1px solid #4A5568;
    color: #CBD5E0;
    padding: 6px 12px;
    font-size: 12px;
}

QPushButton#ToolAction:hover {
    border-color: #BB86FC;
    color: #BB86FC;
}

QMessageBox {
    background-color: #1A202C;
}

QMessageBox QLabel {
    color: #E2E8F0;
    font-size: 14px;
}

QMessageBox QPushButton {
    background-color: #2D3748;
    color: #E2E8F0;
    border: 1px solid #4A5568;
    min-width: 80px;
    padding: 6px 12px;
}

QMessageBox QPushButton:hover {
    background-color: #4A5568;
}
"""


class RenameConfirmDialog(QDialog):
    def __init__(self, current_name, suggested_name, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Confirm Rename")
        self.setFixedWidth(450)
        self.setStyleSheet(DARK_THEME)
        
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(30, 30, 30, 30)
        self.layout.setSpacing(20)

        self.header = QLabel("Confirm Name Change")
        self.header.setObjectName("HeaderTitle")
        self.layout.addWidget(self.header)

        self.sub_info = QVBoxLayout()
        self.label = QLabel("Current Filename")
        self.label.setObjectName("SectionLabel")
        self.current_label = QLabel(current_name)
        self.current_label.setStyleSheet("color: #718096; margin-bottom: 10px;")
        self.current_label.setWordWrap(True)
        self.sub_info.addWidget(self.label)
        self.sub_info.addWidget(self.current_label)
        self.layout.addLayout(self.sub_info)

        self.edit_info = QVBoxLayout()
        self.edit_label = QLabel("New Filename")
        self.edit_label.setObjectName("SectionLabel")
        self.name_edit = QLineEdit(suggested_name)
        self.edit_info.addWidget(self.edit_label)
        self.edit_info.addWidget(self.name_edit)
        self.layout.addLayout(self.edit_info)

        self.buttons = QHBoxLayout()
        self.buttons.setSpacing(12)
        self.cancel_button = QPushButton("Back")
        self.cancel_button.setObjectName("SecondaryAction")
        self.cancel_button.clicked.connect(self.reject)
        
        self.ok_button = QPushButton("Confirm Rename")
        self.ok_button.setObjectName("PrimaryAction")
        self.ok_button.clicked.connect(self.accept)
        
        self.buttons.addStretch()
        self.buttons.addWidget(self.cancel_button)
        self.buttons.addWidget(self.ok_button)
        self.layout.addLayout(self.buttons)

        self.setLayout(self.layout)

    def get_new_name(self):
        return self.name_edit.text()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("File Renamer AI")
        self.resize(1200, 800)
        self.setStyleSheet(DARK_THEME)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # --- Sidebar ---
        self.sidebar = QFrame()
        self.sidebar.setObjectName("Sidebar")
        self.sidebar.setFixedWidth(300)
        self.sidebar_layout = QVBoxLayout(self.sidebar)
        self.sidebar_layout.setContentsMargins(20, 30, 20, 30)
        self.sidebar_layout.setSpacing(20)

        self.logo_label = QLabel("RENAMER")
        self.logo_label.setObjectName("HeaderTitle")
        self.logo_label.setStyleSheet("letter-spacing: 4px; font-size: 20px; color: #BB86FC;")
        self.sidebar_layout.addWidget(self.logo_label)

        self.select_button = QPushButton("Import Files")
        self.select_button.setObjectName("SelectAction")
        self.select_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.select_button.clicked.connect(self.on_select_clicked)
        self.sidebar_layout.addWidget(self.select_button)

        self.list_label = QLabel("Queue")
        self.list_label.setObjectName("SectionLabel")
        self.sidebar_layout.addWidget(self.list_label)

        self.file_list = QListWidget()
        self.sidebar_layout.addWidget(self.file_list)
        
        self.sidebar_layout.addStretch()
        
        self.main_layout.addWidget(self.sidebar)

        # --- Content Area ---
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(40, 40, 40, 40)
        self.content_layout.setSpacing(30)

        # Preview Section
        self.preview_container = QSplitter(Qt.Orientation.Horizontal)
        
        self.preview_frame = QFrame()
        self.preview_frame.setObjectName("PreviewArea")
        self.preview_frame_layout = QVBoxLayout(self.preview_frame)
        self.preview_label = QLabel("No file selected")
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_frame_layout.addWidget(self.preview_label)
        self.preview_container.addWidget(self.preview_frame)

        self.text_preview = QTextEdit()
        self.text_preview.setPlaceholderText("Selectable text will appear here...")
        self.text_preview.setReadOnly(True)
        self.preview_container.addWidget(self.text_preview)
        
        self.preview_container.setStretchFactor(0, 2)
        self.preview_container.setStretchFactor(1, 1)
        self.content_layout.addWidget(self.preview_container, 3)

        # Control Card
        self.control_card = QFrame()
        self.control_card.setObjectName("ControlCard")
        self.control_card_layout = QVBoxLayout(self.control_card)
        self.control_card_layout.setContentsMargins(30, 30, 30, 30)
        self.control_card_layout.setSpacing(20)

        # Row 1: Date and Suggestion Label
        self.meta_row = QHBoxLayout()
        self.date_label = QLabel("DATE: N/A")
        self.date_label.setObjectName("DateLabel")
        self.meta_row.addWidget(self.date_label)
        self.meta_row.addStretch()
        self.control_card_layout.addLayout(self.meta_row)

        # Row 2: Suggested Name Input
        self.name_row = QVBoxLayout()
        self.sugg_label = QLabel("Suggested Filename")
        self.sugg_label.setObjectName("SectionLabel")
        self.suggestion_edit = QLineEdit()
        self.name_row.addWidget(self.sugg_label)
        self.name_row.addWidget(self.suggestion_edit)
        self.control_card_layout.addLayout(self.name_row)

        # Row 3: Tools and Main Actions
        self.actions_row = QHBoxLayout()
        
        self.tools_layout = QHBoxLayout()
        self.titlecase_button = QPushButton("Titlecase")
        self.titlecase_button.setObjectName("ToolAction")
        self.titlecase_button.clicked.connect(self.on_titlecase_clicked)
        self.underscore_button = QPushButton("Underscore")
        self.underscore_button.setObjectName("ToolAction")
        self.underscore_button.clicked.connect(self.on_underscore_clicked)
        self.tools_layout.addWidget(self.titlecase_button)
        self.tools_layout.addWidget(self.underscore_button)
        self.actions_row.addLayout(self.tools_layout)
        
        self.actions_row.addStretch()
        
        self.cancel_button = QPushButton("Skip")
        self.cancel_button.setObjectName("CancelAction")
        self.cancel_button.clicked.connect(self.on_cancel_clicked)
        self.actions_row.addWidget(self.cancel_button)

        self.rename_button = QPushButton("Apply Rename")
        self.rename_button.setObjectName("PrimaryAction")
        self.rename_button.setMinimumWidth(160)
        self.rename_button.clicked.connect(self.on_rename_clicked)
        self.actions_row.addWidget(self.rename_button)
        
        self.control_card_layout.addLayout(self.actions_row)
        
        self.content_layout.addWidget(self.control_card)
        
        self.main_layout.addWidget(self.content_widget)

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
            target_path = os.path.join(os.path.dirname(old_path), new_name)

            # Check if it's the same file (e.g. case-change only on macOS)
            is_same = False
            try:
                if os.path.exists(target_path):
                    is_same = os.path.samefile(old_path, target_path)
            except OSError:
                pass

            # Ensure uniqueness if renaming to a DIFFERENT file that already exists
            if os.path.exists(target_path) and not is_same:
                target_path = get_unique_path(target_path)
                new_name = os.path.basename(target_path)

            try:
                os.rename(old_path, target_path)
                QMessageBox.information(self, "Success", f"File renamed to {new_name}")
                # Update list item and current files to process
                item = self.file_list.item(self.current_file_index)
                if item:
                    item.setText(new_name)
                self.files_to_process[self.current_file_index] = target_path

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
