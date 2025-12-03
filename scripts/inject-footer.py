#!/usr/bin/env python3
"""
Inject footer content into README.md.

This script reads footer content from footer/footer.html and updates
the README.md footer section using the update-readme.py utility.

Usage:
    python scripts/inject-footer.py
"""

import sys
from pathlib import Path
from update_readme import update_readme_section


def main() -> None:
    """Main entry point for footer injection."""
    script_dir = Path(__file__).resolve().parent
    repo_root = script_dir.parent
    
    footer_path = repo_root / "footer" / "footer.html"
    readme_path = repo_root / "README.md"
    
    if not footer_path.exists():
        print(f"Error: Footer file not found at {footer_path}", file=sys.stderr)
        sys.exit(1)
    
    if not readme_path.exists():
        print(f"Error: README.md not found at {readme_path}", file=sys.stderr)
        sys.exit(1)
    
    try:
        footer_content = footer_path.read_text(encoding="utf-8").strip()
    except IOError as e:
        print(f"Error reading footer file: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Note: This would require a FOOTER marker in README.md
    # For now, the footer is directly embedded in README.md
    print("Footer is embedded directly in README.md")
    print("To update footer: edit footer/footer.html then manually sync to README.md")
    print("Or add <!-- FOOTER:START --> and <!-- FOOTER:END --> markers to README.md")


if __name__ == "__main__":
    main()
