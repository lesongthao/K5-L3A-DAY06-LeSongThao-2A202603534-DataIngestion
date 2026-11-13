"""Build a submission snapshot from explicit paths; omit credentials and runtime DB."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parent.parent
PATTERNS = (
    "*.md", "requirements*.txt", ".gitignore", ".env.example", ".github/workflows/*.yml", "src/*.py", "scripts/*.py",
    "demo/*.py", "demo/static/*.html", "demo/static/*.css", "demo/static/*.js",
    "data/*.json", "data/*.pdf", "benchmark/*.json", "artifacts/*.csv", "artifacts/audit_confirmation.json",
    "results/benchmark_summary.json", "results/audit_report.json", "results/skipped_pages.json",
    "results/traces_strategy_*.json", "report/individual/*.md", "docs/*.md",
    "assets/*.svg", "assets/demo-*.png", "starter/README.md", "starter/requirements.txt",
    "starter/.env.example", "starter/docker-compose.yml", "starter/init.sql",
    "starter/src/*.py", "starter/scripts/*.py", "starter/data/*.json", "starter/data/*.pdf",
)
SECRET = re.compile(rb"AIza[0-9A-Za-z_-]{35}|gh[pousr]_[A-Za-z0-9]{20,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")


def package(output=None):
    paths = sorted({path for pattern in PATTERNS for path in ROOT.glob(pattern) if path.is_file()})
    contents = []
    for path in paths:
        relative = path.relative_to(ROOT).as_posix()
        if not path.resolve().is_relative_to(ROOT.resolve()) or path.is_symlink():
            raise ValueError(f"Refusing linked/outside file: {relative}")
        body = path.read_bytes()
        if path.suffix not in (".pdf", ".png") and SECRET.search(body):
            raise ValueError(f"Possible credential in {relative}; remove it before packaging")
        contents.append((relative, body))
    output = Path(output) if output else ROOT / "exports/Day06_2A202603534_LeSongThao.zip"
    output.parent.mkdir(parents=True, exist_ok=True)
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    dirty = bool(subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True).strip())
    manifest = {"base_commit": commit, "working_tree_changes_included": dirty,
                "description": "Snapshot of allowlisted workspace files; base_commit is not a commit for uncommitted changes.",
                "excluded": [".env", ".git", "virtual environments", "runtime vector database"],
                "files": {name: hashlib.sha256(body).hexdigest() for name, body in contents}}
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, body in contents:
            archive.writestr(name, body)
        archive.writestr("SNAPSHOT.json", json.dumps(manifest, ensure_ascii=False, indent=2))
    print(f"Submission snapshot: {output} ({len(contents)} files)")
    return output


if __name__ == "__main__":
    package()
