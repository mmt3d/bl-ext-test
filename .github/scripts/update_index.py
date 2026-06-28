import ast
import hashlib
import json
import os
import tomllib
import zipfile


def extract_bl_info(init_path):
    """__init__.py から bl_info を安全・確実に抽出する"""
    with open(init_path, "r", encoding="utf-8") as f:
        source_code = f.read()

    # 構文木にパース
    tree = ast.parse(source_code)

    # トップレベルの代入文（Assignment）を走査
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                # 変数名が 'bl_info' かチェック
                if isinstance(target, ast.Name) and target.id == "bl_info":
                    # ast.literal_eval で安全にPythonの辞書オブジェクトに変換
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
    addon_dir = "bl-ext-test"
    init_script_path = os.path.join(addon_dir, "__init__.py")
    index_path = "index.json"
    base_toml_path = "blender_manifest_base.toml"

    with open(base_toml_path, "rb") as f:
        manifest = tomllib.load(f)
    addon_id = manifest["id"]

    bl_info = extract_bl_info(init_script_path)
    version = ".".join(map(str, bl_info.get("version")))
    bl_version = ".".join(map(str, bl_info.get("blender")))

    repo_owner = os.environ["GITHUB_REPOSITORY_OWNER"]
    repo_name = os.environ["GITHUB_REPOSITORY"].split("/")[-1]

    with open(index_path, "r", encoding="utf-8") as f:
        index_data = json.load(f)

    exists = any(ext["id"] == addon_id and ext["version"] == version for ext in index_data["data"])
    if exists:
        print(f"バージョン {version} は既に存在するため、json更新をスキップします。")
        return

    # merge
    manifest["version"] = version
    manifest["name"] = bl_info["name"]
    manifest["tagline"] = bl_info["description"]
    manifest["maintainer"] = repo_owner
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
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(addon_dir):
            for file in files:
                file_path = os.path.join(root, file)
                # zip内での相対パス（剥き出し状態）にする
                arcname = os.path.relpath(file_path, addon_dir)
                zf.write(file_path, arcname)

    manifest["archive_url"] = f"https://{repo_owner}.github.io/{repo_name}/zips/{zip_name}"
    manifest["archive_size"] = os.path.getsize(zip_name)
    manifest["archive_hash"] = f"sha256:{calculate_sha256(zip_name)}"

    index_data["data"].insert(0, manifest)

    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(index_data, f, indent=2, ensure_ascii=False)
    print(f"配信用 index.json にバージョン {version} を追加しました。")

    with open(os.environ['GITHUB_OUTPUT'], 'a') as fh:
        print(f"zip_path={zip_name}", file=fh)


if __name__ == "__main__":
    main()
