import ast
import json
import os
import tomllib


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


def main():
    addon_dir = "bl-ext-test"
    init_script_path = os.path.join(addon_dir, "__init__.py")
    base_toml_path = "blender_manifest_base.toml"

    with open(base_toml_path, "rb") as f:
        manifest = tomllib.load(f)
    addon_id = manifest["id"]

    bl_info = extract_bl_info(init_script_path)
    version = ".".join(map(str, bl_info.get("version")))
    bl_version = ".".join(map(str, bl_info.get("blender")))

    zip_name = f"{addon_id}-{version}.zip"
    with open(os.environ['GITHUB_OUTPUT'], 'a') as fh:
        print(f"zip_name={zip_name}", file=fh)
        print(f"version={version}", file=fh)

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
            toml_lines.append(f'[{key}]\n' + '\n'.join(f'{k} = "{v}"' for k, v in value.items()))

    toml_path = os.path.join(addon_dir, "blender_manifest.toml")
    with open(toml_path, "w", encoding="utf-8") as f:
        f.write("\n".join(toml_lines) + "\n")

    print(f"マニフェスト生成完了: {toml_path}")


if __name__ == "__main__":
    main()