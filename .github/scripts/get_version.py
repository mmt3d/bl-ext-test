import ast
import os


init_path = 'bl-ext-test/__init__.py'
with open(init_path, 'r', encoding='utf-8') as f:
    tree = ast.parse(f.read())
for node in tree.body:
    if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'bl_info' for t in node.targets):
        bl_info = ast.literal_eval(node.value)
        version = '.'.join(map(str, bl_info.get('version', (1, 0, 0))))
        with open(os.environ['GITHUB_OUTPUT'], 'a') as fh:
            print(f'version={version}', file=fh)
        break
