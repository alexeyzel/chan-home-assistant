"""Prepare a clean example node that fetches all firmware through a Git ref."""

import sys
from pathlib import Path


def main():
    ref, destination = sys.argv[1:]
    root = Path(__file__).resolve().parent.parent
    target = Path(destination)
    target.mkdir(parents=True, exist_ok=True)
    template = (root / "firmware/chan.example.yaml").read_text(encoding="utf-8")
    (target / "chan.yaml").write_text(template.replace("@v0.1.1", f"@{ref}"), encoding="utf-8")
    (target / "secrets.yaml").write_bytes((root / "firmware/secrets.example.yaml").read_bytes())
    print(target / "chan.yaml")


if __name__ == "__main__":
    main()
