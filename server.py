"""
File Organizer API Backend
==========================
Flask REST API server connecting the modular Python file organizer engine
to the React + CSS frontend.
"""

from pathlib import Path
import os
import sys
import logging
import webbrowser
from flask import Flask, request, jsonify, send_from_directory

# Engine imports from main package
from main import (
    load_config,
    AUDIT_LOG_FILENAME,
    find_files_to_organize,
    get_category_for_extension,
    organize_folder,
    undo_last_operation
)
from create_demo_files import create_demo_environment

DIST_DIR = Path(__file__).resolve().parent / "frontend" / "dist"

app = Flask(
    __name__,
    static_folder=str(DIST_DIR / "assets") if (DIST_DIR / "assets").exists() else None,
    static_url_path="/assets"
)

# Basic logging
logging.basicConfig(level=logging.INFO)
server_logger = logging.getLogger("server")


@app.after_request
def add_cors_headers(response):
    """Enable CORS so the React frontend on any port can access this API."""
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
    return response


@app.route("/api/config", methods=["GET"])
def get_config():
    """Returns current active categories and default rules."""
    categories, default_cat, ignored = load_config()
    return jsonify({
        "categories": categories,
        "default_category": default_cat,
        "ignored_files": sorted(list(ignored))
    })


@app.route("/api/scan", methods=["POST"])
def scan_directory():
    """
    Scans a folder and returns statistics & file list before organizing.
    Allows React UI to preview what will be organized.
    """
    data = request.get_json(silent=True) or {}
    folder_str = data.get("folder", "").strip() or "."
    recursive = bool(data.get("recursive", False))

    source_dir = Path(folder_str).resolve()
    if not source_dir.exists():
        return jsonify({"error": f"Folder does not exist: {source_dir}"}), 404
    if not source_dir.is_dir():
        return jsonify({"error": f"Path is not a directory: {source_dir}"}), 400

    categories_map, default_cat, ignored_files = load_config()
    category_names = set(categories_map.keys()) | {default_cat}

    files = find_files_to_organize(
        source_dir=source_dir,
        recursive=recursive,
        category_names=category_names,
        ignored_files=ignored_files
    )

    items = []
    category_counts = {cat: 0 for cat in list(categories_map.keys()) + [default_cat]}

    for f in files:
        cat = get_category_for_extension(f.suffix, categories_map, default_cat)
        category_counts[cat] = category_counts.get(cat, 0) + 1
        try:
            size_bytes = f.stat().st_size
        except OSError:
            size_bytes = 0

        items.append({
            "name": f.name,
            "category": cat,
            "extension": f.suffix.lower(),
            "size": size_bytes,
            "rel_path": str(f.relative_to(source_dir))
        })

    has_audit = (source_dir / AUDIT_LOG_FILENAME).exists()

    return jsonify({
        "folder": str(source_dir),
        "total_files": len(items),
        "category_counts": category_counts,
        "files": items[:200],  # Limit preview list to first 200 items for performance
        "has_audit_log": has_audit
    })


@app.route("/api/organize", methods=["POST"])
def run_organize():
    """Executes organization on the requested directory."""
    data = request.get_json(silent=True) or {}
    folder_str = data.get("folder", "").strip() or "."
    recursive = bool(data.get("recursive", False))
    dry_run = bool(data.get("dry_run", False))

    summary = organize_folder(folder_str, dry_run=dry_run, recursive=recursive)
    return jsonify(summary)


@app.route("/api/undo", methods=["POST"])
def run_undo():
    """Reverts the previous organization session."""
    data = request.get_json(silent=True) or {}
    folder_str = data.get("folder", "").strip() or "."
    dry_run = bool(data.get("dry_run", False))

    summary = undo_last_operation(folder_str, dry_run=dry_run)
    return jsonify(summary)


@app.route("/api/demo", methods=["POST"])
def generate_demo():
    """Generates the demo_messy_folder for live testing."""
    data = request.get_json(silent=True) or {}
    folder_name = data.get("folder", "demo_messy_folder")
    created_path = create_demo_environment(folder_name)
    return jsonify({
        "success": True,
        "folder": str(created_path),
        "folder_name": folder_name
    })


@app.route("/api/browse", methods=["POST"])
def browse_folder():
    """
    Opens a native system directory picker dialog and returns the selected path.
    """
    try:
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        selected_path = filedialog.askdirectory(title="Select Folder to Organize")
        root.destroy()
        if selected_path:
            return jsonify({"selected": str(Path(selected_path).resolve())})
        return jsonify({"selected": None})
    except Exception as err:
        return jsonify({"error": str(err)}), 500


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_react_app(path):
    """Serves the compiled React SPA from frontend/dist."""
    if DIST_DIR.exists():
        target = DIST_DIR / path
        if path and target.exists() and target.is_file():
            return send_from_directory(str(DIST_DIR), path)
        return send_from_directory(str(DIST_DIR), "index.html")
    return (
        "<h2>React frontend build not found.</h2>"
        "<p>Run <code>npm run build --prefix frontend</code> or <code>npm run dev --prefix frontend</code></p>"
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    url = f"http://127.0.0.1:{port}"
    print(f"\n==================================================")
    print(f"🚀 File Organizer React UI running on {url}")
    print(f"   Opening browser automatically...")
    print(f"==================================================\n")
    try:
        webbrowser.open(url)
    except Exception:
        pass
    app.run(host="127.0.0.1", port=port, debug=False)
