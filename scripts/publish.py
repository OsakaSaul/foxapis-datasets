#!/usr/bin/env python3
"""Push the files in dist/ to Kaggle and Hugging Face. A service without its token is skipped, not failed.

Tokens come only from environment variables (repository secrets): KAGGLE_KEY (with a current KGAT_ token no
KAGGLE_USERNAME is needed; a legacy 32-character key needs it), and HF_TOKEN.
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
        done = subprocess.run(command, capture_output=True, text=True)
        said = (done.stdout or "") + (done.stderr or "")
        print(said.strip())
        # The client can refuse an upload and still exit 0, so only its own success sentence counts.
        if done.returncode != 0 or "is being created" not in said:
            raise RuntimeError("Kaggle did not accept the upload")
    print(f"Kaggle: {'new version of' if exists else 'created'} https://www.kaggle.com/datasets/{slug}")


def kaggle_sign_in():
    """Fill KAGGLE_USERNAME. A current Kaggle token (KGAT_...) needs no username secret: Kaggle says whose it is."""
    if os.environ.get("KAGGLE_USERNAME") or not os.environ.get("KAGGLE_KEY", "").startswith("KGAT_"):
        return
    os.environ["KAGGLE_API_TOKEN"] = os.environ["KAGGLE_KEY"]
    try:
        from kaggle.api.kaggle_api_extended import KaggleApi
        api = KaggleApi()
        api.authenticate()
        user = api.get_config_value("username")
    except (Exception, SystemExit) as error:  # the client calls exit() when it cannot sign in
        print(f"Kaggle: the token was not accepted ({type(error).__name__})")
        return
    if user:
        os.environ["KAGGLE_USERNAME"] = user


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
    failed = []
    kaggle_sign_in()
    if os.environ.get("KAGGLE_USERNAME") and os.environ.get("KAGGLE_KEY"):
        targets.append(kaggle)
    elif os.environ.get("KAGGLE_KEY"):
        failed.append("kaggle sign-in")   # a token that does not work must turn the run red, not be skipped
    else:
        print("Kaggle: no token yet, skipped")
    if os.environ.get("HF_TOKEN"):
        targets.append(hugging_face)
    else:
        print("Hugging Face: no token yet, skipped")
    for target in targets:
        for name in META:
            try:
                target(name)
            except Exception as error:  # one dataset failing must not stop the others
                failed.append(f"{target.__name__} {name}: {type(error).__name__}")
    if failed:
        raise SystemExit("Failed: " + "; ".join(failed))
