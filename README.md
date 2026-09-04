# Image Color Extract

A fast, lightweight web application built with Flask, Bootstrap 5, and Pillow that extracts the dominant color palette from any uploaded image and groups tonal shades by standard CSS3 color identities.

---

## Features

- **In-Memory Processing:** Processes uploads entirely in memory via `io.BytesIO` without persisting temporary files to disk.
- **Adaptive Octree Quantization:** Fast, low-latency color extraction using Pillow's native quantization algorithms.
- **Intelligent Shade Grouping:** Aggregates neighboring shades into their parent CSS3 color names with expandable dropdowns displaying individual RGB/HEX variations.
- **Percentage Breakdown:** Calculates relative pixel distributions for both individual color variants and overall parent tones.
- **Security Protections:** Validates MIME types, guards against path traversal, and enforces upper/lower bounds on extraction parameters.

---

## Tech Stack

- **Backend:** Python 3, Flask, Pillow, NumPy, Webcolors
- **Frontend:** Jinja2, HTML5, Bootstrap 5
- **Deployment:** Vercel Serverless Functions

---

## Getting Started

### Prerequisites
- Python 3.10+
- `pip` package manager

### Local Installation

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/](https://github.com/)KINGDAUDA/img-color-extract.git
   cd img-color-extract
   
2. **Set up a virtual environment**

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
4. **Run development server**
   ```bash
   python main.py