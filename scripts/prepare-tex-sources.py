"""Clone TeX-only Markdown corpora without downloading LFS images.

Run from any directory using the deployment Python interpreter.
Existing checkouts are retained and checked for the expected remote and prefix.
"""
import json
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]

def main():
    manifest = json.loads((ROOT / "plugins/tex-cpp/plugin.json").read_text())
    env = dict(os.environ, GIT_LFS_SKIP_SMUDGE="1")
    for source in manifest["sources"].values():
        target = ROOT / "engine" / source["path"]
        if target.exists():
            if not (target / ".git").exists():
                raise SystemExit(f"Existing directory is not a checkout: {target}")
            origin = subprocess.check_output(["git", "-C", str(target), "remote", "get-url", "origin"], text=True).strip()
            if origin != source["url"]:
                raise SystemExit(f"Refusing checkout with different origin: {target}")
            print(f"Keeping existing checkout: {target}")
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            subprocess.run(["git", "clone", "--depth", "1", "--branch", source["branch"], source["url"], str(target)], env=env, check=True)
        if not (target / source["prefix"]).is_dir():
            raise SystemExit(f"Missing content prefix: {target / source['prefix']}")
    print("TeX documentation and API reference sources are ready.")

if __name__ == "__main__":
    main()
