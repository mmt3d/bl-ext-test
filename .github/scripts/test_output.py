import os


def main():
    zip_name = "test-ver.zip"
    with open(os.environ['GITHUB_OUTPUT'], 'a') as fh:
        print(f"zip_name={zip_name}", file=fh)

    toml_path = 'test-ver.toml'
    print(f"マニフェスト生成完了: {toml_path}")


if __name__ == "__main__":
    main()