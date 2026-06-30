import ast
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


def main():
    src_dir = "src"
    dist_dir = "dist"
    addon_dir = os.path.join(src_dir, "bl-ext-test")
    init_script_path = os.path.join(addon_dir, "__init__.py")
    base_toml_path = os.path.join(src_dir, "blender_manifest_base.toml")
    dist_zips_dir = os.path.join(dist_dir, "zips")
    os.makedirs(dist_zips_dir, exist_ok=True)

    with open(base_toml_path, "rb") as f:
        manifest = tomllib.load(f)
    addon_id = manifest["id"]

    bl_info = extract_bl_info(init_script_path)
    version = ".".join(map(str, bl_info.get("version")))
    bl_version = ".".join(map(str, bl_info.get("blender")))
    zip_name = "test-ver.zip"
    with open(os.environ['GITHUB_OUTPUT'], 'a') as fh:
        print(f"zip_name={zip_name}", file=fh)

    toml_path = 'test-ver.toml'
    print(f"マニフェスト生成完了: {toml_path}")


if __name__ == "__main__":
    main()