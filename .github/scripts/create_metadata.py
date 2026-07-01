import hashlib
import json
import os
import tomllib


def calculate_sha256(filepath: str):
    sha256_hash = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for byte_block in iter(lambda: f.read(4096), b''):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def main():
    src_dir = "src"
    addon_dir = os.path.join(src_dir, "bl-ext-test")

    toml_path = os.path.join(addon_dir, "blender_manifest.toml")
    with open(toml_path, "rb") as f:
        manifest = tomllib.load(f)

    repo_full_name = os.environ.get("GITHUB_REPOSITORY", "mmt3d/bl-ext-test")
    tag_name = os.environ["TAG_NAME"]
    zip_name = os.environ["ZIP_NAME"]
    zip_path = os.path.join(src_dir, zip_name)

    manifest["archive_url"] = f"https://github.com/{repo_full_name}/releases/download/{tag_name}/{zip_name}"
    manifest["archive_size"] = os.path.getsize(zip_path)
    manifest["archive_hash"] = f"sha256:{calculate_sha256(zip_path)}"
    manifest["extra"] = {"archive_releases": f"https://github.com/{repo_full_name}/releases"}

    with open("metadata.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()