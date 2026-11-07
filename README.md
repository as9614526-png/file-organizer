# File Organizer Automation Tool (Python & React)

A full-stack file organization automation suite combining a **modular Python package (`main/`)** with a **modern React + CSS visual dashboard**.

---

## 🌟 Key Features

- **Package Architecture (`main/`)**: Core logic is packaged into a dedicated `main/` module (`file_organizer`, `organizer`, `file_ops`, `undo_manager`, `logger`, `config`).
- **Modern React Web Dashboard**: Interactive UI with real-time stats, category chips, live terminal console, and file previews.
- **Native Folder Browser**: Click **"Browse"** in the web interface to open your OS's native folder selection dialog.
- **Undo / Revert Capability (`--undo`)**: Atomic transaction history (`organizer_audit.json`) allows rolling back any session.
- **Categorized Routing**: Automatically organizes `Images`, `Documents`, `Videos`, `Audio`, and `Other files`.
- **Dry-Run Simulation**: Preview file movements before modifying any disk state.
- **Recursive Scanning (`-r`)**: Traverses nested subdirectories while preventing infinite loops.
- **External Configuration (`config.json`)**: Allows adding custom extensions and categories without touching source code.
- **Robust Error Handling**: Handles Windows/OneDrive permissions, file collisions, and system file exclusions.

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
python task/
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
└── create_demo_files.py    # Test data generator for demonstrations
```

---

## 🎨 How to Launch the React UI

You can launch the complete React UI directly with Python:
```powershell
python file_organizer.py --ui
# or
python -m main --ui
# or
python server.py
```
This automatically starts the backend server on `http://127.0.0.1:5000` and opens the dashboard in your default web browser.

---

## 💻 How to Use via Command Line (CLI)

You can run the organizer using any of these commands:

```powershell
# Run via package
python -m main "path/to/folder"

# Run via root script
python file_organizer.py "path/to/folder"

# Recursive scanning (nested subdirectories)
python -m main "path/to/folder" -r

# Dry-run simulation mode
python -m main "path/to/folder" --dry-run

# Undo / Revert previous organization session
python -m main "path/to/folder" --undo
```

---

## 🧪 Testing & Demonstration

Run the automated unit test suite (10 tests):
```powershell
python -m unittest test_organizer.py -v
```
All 10 unit tests run in isolated temporary directories.
