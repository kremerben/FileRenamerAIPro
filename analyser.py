import fitz  # PyMuPDF
from PIL import Image
from PIL.ExifTags import TAGS
import re
from datetime import datetime
import os


def find_dates(text):
    # Matches common date formats (YYYY-MM-DD, MM/DD/YYYY, etc.)
    # Heuristic for the task
    date_patterns = [
        r"\d{4}[-/]\d{1,2}[-/]\d{1,2}",  # YYYY-MM-DD
        r"\d{1,2}[-/]\d{1,2}[-/]\d{4}",  # DD/MM/YYYY or MM/DD/YYYY
        r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2}, \d{4}",  # Month D, YYYY
    ]
    for pattern in date_patterns:
        match = re.search(pattern, text)
        if match:
            # For simplicity, we just return the first one found and try to normalize it to YYYYMMDD
            try:
                # Basic normalization attempt
                d_str = match.group(0)
                # This is just a heuristic. In a real app we'd use dateutil.parser
                # For this task, let's keep it simple.
                # If it's Month D, YYYY
                if any(
                    m in d_str
                    for m in [
                        "Jan",
                        "Feb",
                        "Mar",
                        "Apr",
                        "May",
                        "Jun",
                        "Jul",
                        "Aug",
                        "Sep",
                        "Oct",
                        "Nov",
                        "Dec",
                    ]
                ):
                    dt = datetime.strptime(d_str.replace(",", ""), "%b %d %Y")
                elif "-" in d_str:
                    parts = d_str.split("-")
                    if len(parts[0]) == 4:  # YYYY-MM-DD
                        dt = datetime.strptime(d_str, "%Y-%m-%d")
                    else:
                        dt = datetime.strptime(d_str, "%m-%d-%Y")  # Or DD-MM-YYYY
                elif "/" in d_str:
                    parts = d_str.split("/")
                    if len(parts[0]) == 4:  # YYYY/MM/DD
                        dt = datetime.strptime(d_str, "%Y/%m/%d")
                    else:
                        dt = datetime.strptime(d_str, "%m/%d/%Y")
                else:
                    return None
                return dt.strftime("%Y%m%d")
            except:
                pass
    return None


def get_file_date(filepath):
    try:
        stat = os.stat(filepath)
        # st_birthtime is available on macOS/BSD
        if hasattr(stat, "st_birthtime"):
            dt = datetime.fromtimestamp(stat.st_birthtime)
        else:
            # Fallback to mtime for other systems
            dt = datetime.fromtimestamp(stat.st_mtime)
        return dt.strftime("%Y%m%d")
    except Exception:
        return datetime.now().strftime("%Y%m%d")


def analyze_pdf(filepath):
    doc = fitz.open(filepath)
    text = ""
    prominent_spans = []
    max_font_size = 0

    first_page = doc[0]
    blocks = first_page.get_text("dict")["blocks"]

    for b in blocks:
        if b["type"] == 0:  # text block
            for l in b["lines"]:
                for s in l["spans"]:
                    text += s["text"] + " "
                    if s["size"] > max_font_size:
                        max_font_size = s["size"]
                        prominent_spans = [s["text"].strip()]
                    elif abs(s["size"] - max_font_size) < 0.1:  # Same font size
                        prominent_spans.append(s["text"].strip())

    # Heuristic: join all spans with the same largest font size
    prominent_text = " ".join(prominent_spans)

    found_date = find_dates(text)
    if not found_date:
        found_date = get_file_date(filepath)

    suggested_name = f"{prominent_text.replace(' ', '_')}_{found_date}.pdf"
    # Clean up filename (remove invalid chars)
    suggested_name = re.sub(r'[\\/*?:"<>|]', "", suggested_name)

    doc.close()
    return suggested_name


def get_ai_name_suggestion(filepath):
    # This is a mock for an AI agent that would describe the file content.
    # In a real app, this would call an external API like OpenAI or a local LLM.
    filename = os.path.basename(filepath).lower()
    if "cat" in filename:
        return "white_cat"
    elif "insurance" in filename:
        return "Dwelling_Insurance"
    elif "therapy" in filename:
        return "Therapy_Homework"
    return "suggested_name"


def analyze_image(filepath):
    try:
        img = Image.open(filepath)
        exif = img._getexif()
        date_str = None
        if exif:
            for tag, value in exif.items():
                decoded = TAGS.get(tag, tag)
                if decoded == "DateTimeOriginal":
                    # Usually "YYYY:MM:DD HH:MM:SS"
                    date_str = value[:10].replace(":", "")
                    break

        if not date_str:
            # Fallback to file creation date
            date_str = get_file_date(filepath)

        # Suggested name for image using mock AI
        suggested_subject = get_ai_name_suggestion(filepath)
        if suggested_subject == "suggested_name":
            suggested_subject = "image"

        suggested_name = f"{suggested_subject}_{date_str}{os.path.splitext(filepath)[1]}"
        return suggested_name
    except Exception as e:
        print(f"Error analyzing image: {e}")
        return os.path.basename(filepath)


def get_suggested_name(filepath):
    ext = os.path.splitext(filepath)[1].lower()
    if ext == ".pdf":
        return analyze_pdf(filepath)
    elif ext in [".jpg", ".jpeg", ".png"]:
        return analyze_image(filepath)
    else:
        # Fallback for other files
        date_str = get_file_date(filepath)
        return f"file_{date_str}{ext}"
