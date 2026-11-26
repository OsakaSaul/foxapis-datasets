#!/usr/bin/env python3
"""Push the files in dist/ to Kaggle and Hugging Face. A service without its token is skipped, not failed.

Tokens come only from environment variables (repository secrets): KAGGLE_USERNAME + KAGGLE_KEY, and HF_TOKEN.
Nothing here prints or stores a token. HF_NAMESPACE (default: foxapis) is the Hugging Face account name.
"""
import json
import os
import pathlib
import shutil
import subprocess
import tempfile

from build import DIST, META


def kaggle(name):
    user = os.environ["KAGGLE_USERNAME"]
    m = META[name]
    slug = f"{user}/{m['kaggle_slug']}"
    with tempfile.TemporaryDirectory() as folder:
        folder = pathlib.Path(folder)
        for f in (DIST / name).iterdir():
            if f.suffix in (".csv", ".parquet"):
                shutil.copy(f, folder / f.name)
        (folder / "dataset-metadata.json").write_text(json.dumps({
            "title": m["title"][:50], "id": slug, "subtitle": m["subtitle"][:80],
            "description": (DIST / name / "card-for-kaggle.txt").read_text(encoding="utf-8"),
            "licenses": [{"name": "CC-BY-4.0"}], "keywords": m["tags"]}), encoding="utf-8")
        exists = subprocess.run(["kaggle", "datasets", "status", slug], capture_output=True, text=True).returncode == 0
        command = (["kaggle", "datasets", "version", "-p", str(folder), "-m", "Weekly refresh"] if exists
                   else ["kaggle", "datasets", "create", "-p", str(folder), "--public"])
        subprocess.run(command, check=True)
    print(f"Kaggle: {'new version of' if exists else 'created'} {slug}")


def hugging_face(name):
    from huggingface_hub import HfApi
    api = HfApi(token=os.environ["HF_TOKEN"])
    repo = f"{os.environ.get('HF_NAMESPACE') or 'foxapis'}/{name}"
    api.create_repo(repo, repo_type="dataset", exist_ok=True)
    api.upload_folder(repo_id=repo, repo_type="dataset", folder_path=str(DIST / name),
                      ignore_patterns=["card-for-kaggle.txt"], commit_message="Weekly refresh")
    print(f"Hugging Face: updated {repo}")


if __name__ == "__main__":
    targets = []
    if os.environ.get("KAGGLE_USERNAME") and os.environ.get("KAGGLE_KEY"):
        targets.append(kaggle)
    else:
        print("Kaggle: no token yet, skipped")
    if os.environ.get("HF_TOKEN"):
        targets.append(hugging_face)
    else:
        print("Hugging Face: no token yet, skipped")
    failed = []
    for target in targets:
        for name in META:
            try:
                target(name)
            except Exception as error:  # one dataset failing must not stop the others
                failed.append(f"{target.__name__} {name}: {type(error).__name__}")
    if failed:
        raise SystemExit("Failed: " + "; ".join(failed))
