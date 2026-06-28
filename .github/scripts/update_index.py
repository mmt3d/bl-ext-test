import tomllib
import json
import os
import hashlib


def calculate_sha256(filepath):
    """ファイルからSHA256ハッシュ値を計算するヘルパー関数"""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def main():
    manifest_path = "bl-ext-test/blender_manifest.toml"
    index_path = "index.json"

    with open(manifest_path, "rb") as f:
        manifest = tomllib.load(f)

    addon_id = manifest["id"]
    version = manifest["version"]
    zip_name = f"{addon_id}-{version}.zip"

    repo_owner = os.environ["GITHUB_REPOSITORY_OWNER"]
    repo_name = os.environ["GITHUB_REPOSITORY"].split("/")[-1]
    download_url = f"https://{repo_owner}.github.io/{repo_name}/zips/{zip_name}"

    with open(index_path, "r", encoding="utf-8") as f:
        index_data = json.load(f)

    exists = any(ext["id"] == addon_id and ext["version"] == version for ext in index_data["data"])
    
    if not exists:
        new_entry = {}
        for key, value in manifest.items():
            if key != "permissions": 
                new_entry[key] = value

        new_entry["archive_url"] = download_url

        import zipfile
        addon_dir = "bl-ext-test"
        with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zf:
            for root, dirs, files in os.walk(addon_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    # zip内での相対パス（剥き出し状態）にする
                    arcname = os.path.relpath(file_path, addon_dir)
                    zf.write(file_path, arcname)
        new_entry["archive_size"] = os.path.getsize(zip_name)
        new_entry["archive_hash"] = f"sha256:{calculate_sha256(zip_name)}"

        index_data["data"].insert(0, new_entry)

        with open(index_path, "w", encoding="utf-8") as f:
            json.dump(index_data, f, indent=2, ensure_ascii=False)
        print(f"配信用 index.json にバージョン {version} を追加しました。")
    else:
        print(f"バージョン {version} は既に存在するため、json更新をスキップします。")

    with open(os.environ['GITHUB_OUTPUT'], 'a') as fh:
        print(f"zip_path={zip_name}", file=fh)


if __name__ == "__main__":
    main()
