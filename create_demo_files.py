"""
Demo File Generator
===================
Creates a sample 'demo_messy_folder' populated with dummy files of various
extensions (images, documents, audio, video, and other files) so you can test
and demonstrate the file organizer tool right away.
"""

from pathlib import Path
import sys


DEMO_FILES = [
    # Images
    "beach_sunset.jpg",
    "avatar_photo.png",
    "vector_logo.svg",
    "reaction_animation.gif",

    # Documents
    "final_project_report.pdf",
    "meeting_notes.docx",
    "budget_2026.xlsx",
    "todo_list.txt",
    "grades_dataset.csv",

    # Videos
    "lecture_recording.mp4",
    "vacation_clip.mkv",
    "presentation_demo.mov",

    # Audio
    "favorite_song.mp3",
    "interview_voice_memo.wav",
    "soundtrack.flac",

    # Other files (unknown, archives, code, executables, or no extension)
    "backup_archive.zip",
    "setup_installer.exe",
    "mystery_file"
]


def create_demo_environment(target_dir_name: str = "demo_messy_folder") -> Path:
    """
    Creates a folder populated with demo files for testing.

    :param target_dir_name: Name of the demo directory
    :return: Path object of the created folder
    """
    demo_dir = Path(target_dir_name).resolve()
    demo_dir.mkdir(parents=True, exist_ok=True)

    print(f"Creating demo test files in: {demo_dir}")
    for filename in DEMO_FILES:
        file_path = demo_dir / filename
        file_path.write_text(f"Dummy sample content for {filename}\n", encoding="utf-8")
        print(f"  + Created: {filename}")

    print("\n[SUCCESS] Demo files created successfully!")
    print(f"To organize this folder, run:\n    python file_organizer.py \"{demo_dir.name}\"")
    print(f"Or test in dry-run mode:\n    python file_organizer.py \"{demo_dir.name}\" --dry-run\n")
    return demo_dir


if __name__ == "__main__":
    folder_name = sys.argv[1] if len(sys.argv) > 1 else "demo_messy_folder"
    create_demo_environment(folder_name)

