"""Fetch the pinned Flask integration fixture used by the existing test suite."""
from pathlib import Path
import subprocess


COMMIT = "d8eaaba824655046958d1a97f11780de460c3271"
ROOT = Path(__file__).resolve().parent.parent
DESTINATION = ROOT / "data" / "real_repos" / "flask"


def main():
    if DESTINATION.exists():
        raise SystemExit(f"{DESTINATION} already exists; left unchanged.")
    DESTINATION.mkdir(parents=True)
    subprocess.run(["git", "init", "--quiet", str(DESTINATION)], check=True)
    subprocess.run(
        ["git", "fetch", "--quiet", "--depth=2", "https://github.com/pallets/flask.git", COMMIT],
        cwd=DESTINATION, check=True,
    )
    subprocess.run(["git", "checkout", "--quiet", "--detach", COMMIT], cwd=DESTINATION, check=True)
    print(f"Prepared Flask fixture at {COMMIT}.")


if __name__ == "__main__":
    main()
