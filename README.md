# File Renamer AI Pro

A high-performance file renaming utility for professionals, featuring a modern, high-information-density interface with AI-driven suggestions.

## Key Features

- **Pro-grade Interface**: Darkmode-native, minimal visual noise, and a sophisticated typography hierarchy.
- **Queue Management**: Integrated sidebar displaying all files in the current selection for efficient batch processing.
- **Smart Analysis**: Scans PDF text (using font size heuristics) and Image EXIF metadata to identify relevant titles and dates.
- **Contextual Fallbacks**: Automatically uses the parent directory name if file content is missing or non-descriptive.
- **Live Preview System**: Instant high-fidelity previews for PDFs and images, with selectable text for document analysis.
- **Standardized Output**: Quick-action tools for title-casing and underscore-normalization of filenames.
- **Safety First**: Non-destructive previewing, explicit confirmation dialogs, and automatic collision detection (appending numeric suffixes for unique names).

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
- **Date Extraction**: The app prioritizes dates found within the file content (PDF text or Image EXIF). If no date is found, it falls back to the file's creation date (birth time).
- **Heuristics**: The app uses font size analysis in PDFs to identify titles and regex patterns for date extraction.
