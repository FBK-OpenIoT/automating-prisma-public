"""Check tracked files and reachable history without printing secret values."""
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
BLOCKED = re.compile(r"(?:\.(?:pdf|docx?|tex|pkl|pickle|faiss|pem|key)$|(?:^|/)(?:vectorstore[^/]*|full_text_pdf[^/]*|CLAUDE_full_text_pdf|\.cache)/|(?:^|/)\.env(?:\..*)?$)", re.I)
SECRETS = [rb"AIza[0-9A-Za-z_-]{35}", rb"sk-ant-[A-Za-z0-9_-]{20,}",
           rb"(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,})",
           rb"(?:AKIA|ASIA)[A-Z0-9]{16}", rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"]


def git(*args, **kwargs):
    return subprocess.check_output(["git", *args], cwd=ROOT, **kwargs)


def forbidden(path):
    return path != ".env.example" and bool(BLOCKED.search(path))


def main():
    problems = []
    paths = git("ls-files", "-z").decode().split("\0")
    for name in filter(None, paths):
        if forbidden(name):
            problems.append(f"Excluded artifact is tracked: {name}")
        path = ROOT / name
        if path.is_file() and any(re.search(pattern, path.read_bytes()) for pattern in SECRETS):
            problems.append(f"Possible credential in working file: {name}")
    objects = git("rev-list", "--objects", "--all").decode().splitlines()
    oids = [line.split(" ", 1)[0] for line in objects]
    metadata = git("cat-file", "--batch-check=%(objectname) %(objecttype)",
                   input=("\n".join(oids) + "\n").encode()).decode().splitlines()
    blobs = {line.split()[0] for line in metadata if line.endswith(" blob")}
    for line in objects:
        oid, _, name = line.partition(" ")
        if oid not in blobs:
            continue
        if forbidden(name):
            problems.append(f"Excluded artifact in reachable history: {name} ({oid[:12]})")
        data = git("cat-file", "blob", oid)
        if any(re.search(pattern, data) for pattern in SECRETS):
            problems.append(f"Possible credential in history: {name} ({oid[:12]})")
    if problems:
        print("\n".join(problems))
        return 1
    print(f"Release scan passed: {len(list(filter(None, paths)))} tracked files, {len(blobs)} reachable blobs.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
