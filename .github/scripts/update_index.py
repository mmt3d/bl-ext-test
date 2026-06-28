import ast
import hashlib
import json
import os
import tomllib
import zipfile


def extract_bl_info(init_path):
    """__init__.py から bl_info を抽出する"""
    with open(init_path, "r", encoding="utf-8") as f:
        source_code = f.read()
    tree = ast.parse(source_code)
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "bl_info":
                    try:
                        return ast.literal_eval(node.value)
                    except (ValueError, SyntaxError) as e:
                        raise ValueError(f"bl_info の構造が静的に解析できません: {e}")
    raise ValueError("__init__.py 内にトップレベルの bl_info 定義が見つかりませんでした。")


def calculate_sha256(filepath: str) -> str:
    """ファイルからSHA256ハッシュ値を計算するヘルパー関数"""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def main():
    src_dir = "src"
    dist_dir = "dist"
    dist_repo_name = "blender-extensions"
    dist_repo_owner = "mmt3d"
    addon_dir = os.path.join(src_dir, "bl-ext-test")
    init_script_path = os.path.join(addon_dir, "__init__.py")
    base_toml_path = os.path.join(src_dir, "blender_manifest_base.toml")
    dist_index_path = os.path.join(dist_dir, "index.json")
    dist_zips_dir = os.path.join(dist_dir, "zips")
    os.makedirs(dist_zips_dir, exist_ok=True)

    with open(base_toml_path, "rb") as f:
        manifest = tomllib.load(f)
    addon_id = manifest["id"]

    bl_info = extract_bl_info(init_script_path)
    version = ".".join(map(str, bl_info.get("version")))
    bl_version = ".".join(map(str, bl_info.get("blender")))

    with open(dist_index_path, "r", encoding="utf-8") as f:
        index_data = json.load(f)

    exists = any(ext["id"] == addon_id and ext["version"] == version for ext in index_data["data"])
    if exists:
        print(f"バージョン {version} は既に存在するため、json更新をスキップします。")
        return

    # merge
    manifest["version"] = version
    manifest["name"] = bl_info["name"]
    manifest["tagline"] = bl_info["description"]
    manifest["maintainer"] = os.environ["GITHUB_REPOSITORY_OWNER"]
    manifest["blender_version_min"] = bl_version

    toml_lines = []
    for key, value in manifest.items():
        if isinstance(value, (str, int, float)):
            toml_lines.append(f'{key} = "{value}"' if isinstance(value, str) else f'{key} = {value}')
        elif isinstance(value, list):
            toml_lines.append(f'{key} = {json.dumps(value)}')
        elif isinstance(value, dict):
            # 簡易的な1階層のテーブル対応（もし将来的に拡張用）
            toml_lines.append(f'[{key}]\n' + '\n'.join(f'{k} = "{v}"' for k, v in value.items()))

    toml_path = os.path.join(addon_dir, "blender_manifest.toml")
    with open(toml_path, "w", encoding="utf-8") as f:
        f.write("\n".join(toml_lines) + "\n")

    zip_name = f"{addon_id}-{version}.zip"
    dist_zip_path = os.path.join(dist_zips_dir, zip_name)
    with zipfile.ZipFile(dist_zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(addon_dir):
            for file in files:
                file_path = os.path.join(root, file)
                # zip内での相対パス（剥き出し状態）にする
                arcname = os.path.relpath(file_path, addon_dir)
                zf.write(file_path, arcname)
    if os.path.exists(toml_path):
        os.remove(toml_path)

    manifest["archive_url"] = f"https://{dist_repo_owner}.github.io/{dist_repo_name}/zips/{zip_name}"
    manifest["archive_size"] = os.path.getsize(dist_zip_path)
    manifest["archive_hash"] = f"sha256:{calculate_sha256(dist_zip_path)}"

    index_data["data"].append(manifest)

    with open(dist_index_path, "w", encoding="utf-8") as f:
        json.dump(index_data, f, indent=2, ensure_ascii=False)
    print(f"配信用 index.json にバージョン {version} を追加しました。")

    with open(os.environ['GITHUB_OUTPUT'], 'a') as fh:
        print(f"zip_path={dist_zip_path}", file=fh)


if __name__ == "__main__":
    main()
