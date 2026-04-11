# File Renamer AI

File Renamer AI is a desktop application designed to help users rename files and directories based on their content. It uses AI-driven suggestions (currently using internal heuristics and metadata analysis) to identify prominent titles and dates within files to suggest appropriate, standardized filenames.

## Features

- **File & Directory Support**: Select a single file or an entire directory to process files one by one.
- **PDF Analysis**: Scans the first page of PDF files for the most prominent text (titles) and dates.
- **Image Analysis**: Extracts metadata (EXIF) from images to find the original creation date and suggests names based on content.
- **Live Preview**: View the file content (PDF or Image) and selectable text (for PDFs) before renaming.
- **Confirmation Modal**: Review and edit the suggested name before finalizing the rename.

## Prerequisites

- Python 3.8 or higher
- `pip` (Python package installer)

## Installation

1. Clone the repository or download the source code.
2. Navigate to the project directory.
3. Install the required dependencies:

```bash
pip install PyQt6 pymupdf Pillow
```

## How to Run

To start the application, run the `main.py` script:

```bash
python main.py
```

## Usage

1. **Launch the App**: Open the application using the command above.
2. **Select File/Directory**: Click the "Select File or Directory" button.
3. **Choose Type**: A prompt will ask if you want to select a directory or a file.
4. **Preview**: The selected file (or the first file in the directory) will be displayed in the preview area.
5. **Review Suggestion**: The "Suggested Name" field will be automatically populated.
6. **Rename**: Click "Rename". A confirmation dialog will appear where you can make final adjustments.
7. **Next File**: If a directory was selected, the app will automatically load the next file until all are processed.

## Technical Details

- **GUI Framework**: PyQt6
- **PDF Processing**: PyMuPDF (fitz)
- **Image Processing**: Pillow (PIL)
- **Heuristics**: The app uses font size analysis in PDFs to identify titles and regex patterns for date extraction.
