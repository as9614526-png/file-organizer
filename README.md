# Smart File Organizer (Python & React)

<p align="left">
  <img src="https://img.shields.io/badge/Python-3.8+-3776AB?style=flat&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/React-18+-61DAFB?style=flat&logo=react&logoColor=black" alt="React" />
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License" />
  <img src="https://img.shields.io/badge/Tests-10%2F10%20Passing-brightgreen" alt="Tests" />
  <img src="https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey" alt="Platform" />
</p>

A full-stack, production-grade file automation tool that categorizes messy directories into clean folders (`Images`, `Documents`, `Videos`, `Audio`, `Other files`). Features an **atomic rollback undo system**, **recursive scanning**, and a **modern React 18 + CSS dashboard**.

---

## 🌟 Key Features

- **Package Architecture (`main/`)**: Single Responsibility modular design (`file_organizer`, `organizer`, `file_ops`, `undo_manager`, `logger`, `config`).
- **Modern React Web Dashboard**: Interactive UI with real-time category chips, live terminal console, and file previews.
- **Native Folder Browser**: Click **"Browse"** in the web interface to open your OS's native folder selection dialog.
- **Undo / Revert Capability (`--undo`)**: Atomic transaction history (`organizer_audit.json`) allows rolling back any session to its exact original directory layout.
- **Categorized Routing**: Automatically organizes `Images`, `Documents`, `Videos`, `Audio`, and `Other files`.
- **Dry-Run Simulation**: Safely preview file movements before modifying any disk state.
- **Recursive Scanning (`-r`)**: Traverses nested subdirectories while preventing infinite loops or cycle traversal.
- **External Configuration (`config.json`)**: Allows non-programmers to define custom extensions and categories without touching source code.
- **Zero-Dependency CLI**: Core CLI runs 100% on Python's built-in standard library.
- **Robust Error Handling**: Handles Windows/OneDrive permissions, duplicate file collisions (`file_1.txt`), and system file exclusions.

---

## 📁 Default File Categories

| Category | Extensions |
| :--- | :--- |
| **Images** | `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.svg`, `.webp`, `.tiff`, `.ico` |
| **Documents** | `.pdf`, `.doc`, `.docx`, `.txt`, `.rtf`, `.odt`, `.xls`, `.xlsx`, `.ppt`, `.pptx`, `.csv` |
| **Videos** | `.mp4`, `.mkv`, `.flv`, `.avi`, `.mov`, `.wmv`, `.webm`, `.m4v` |
| **Audio** | `.mp3`, `.wav`, `.aac`, `.flac`, `.ogg`, `.m4a`, `.wma` |
| **Other files** | Any unrecognized extension or files without extensions (e.g., `.zip`, `.exe`) |

---

## 🧩 Project Structure

```text
├── main/                   # Core Python package folder
│   ├── __init__.py         # Package entry and API exports
│   ├── __main__.py         # Enables 'python -m main' execution
│   ├── file_organizer.py   # CLI interface and main execution
│   ├── organizer.py        # High-level folder organization service
│   ├── undo_manager.py     # Transactional audit logging & session rollback
│   ├── file_ops.py         # Reusable low-level file and directory utilities
│   ├── logger.py           # Dual console and file logger (organizer.log)
│   └── config.py           # Configuration loader and default rules
├── frontend/               # React + CSS dashboard (Vite + Lucide Icons)
│   ├── src/
│   │   ├── components/     # CategoryCard.jsx, etc.
│   │   ├── App.jsx         # Main dashboard layout and state
│   │   ├── App.css         # Modern dark glassmorphic styling
│   │   └── main.jsx
│   ├── dist/               # Pre-compiled production React assets
│   └── package.json
├── server.py               # Flask REST API backend + static React server
├── file_organizer.py       # Root forwarder launcher
├── config.json             # Customizable JSON file categories & ignored files
├── test_organizer.py       # Automated unit test suite (10 tests)
├── create_demo_files.py    # Test data generator for demonstrations
├── requirements.txt        # Optional Python dependencies (Flask for Web UI)
├── pyproject.toml          # Package installation config (pip install -e .)
└── LICENSE                 # MIT Open Source License
```

---

## 🚀 Quick Start

### 1. Clone & Install
```bash
git clone https://github.com/YOUR_USERNAME/python-file-organizer.git
cd python-file-organizer
pip install -r requirements.txt
```

### 2. Launch the React Web Dashboard
```bash
python file_organizer.py --ui
# or
python server.py
```
*Automatically opens `http://127.0.0.1:5000` in your default web browser.*

### 3. Or Use via Command Line (CLI)
```bash
# Standard interactive prompt
python file_organizer.py

# Organize a folder directly
python -m main "path/to/folder"

# Recursive subfolder scanning
python -m main "path/to/folder" -r

# Dry-run simulation mode (safe preview)
python -m main "path/to/folder" --dry-run

# Undo / Revert previous organization session
python -m main "path/to/folder" --undo
```

### 4. Optional: Install as a System CLI Command
```bash
pip install -e .
file-organizer "path/to/folder"
```

---

## 🧪 Testing & Quality Assurance

Run the automated test suite covering categorization, recursion, duplicate collision resolution, and rollback:
```bash
python -m unittest test_organizer.py -v
```
All 10 unit tests run in isolated sandboxes using Python's `tempfile` module.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
