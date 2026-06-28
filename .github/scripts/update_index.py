import tomllib
import json
import os


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
