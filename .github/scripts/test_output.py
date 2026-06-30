import os


def main():
    zip_name = "test-ver.zip"
    with open(os.environ['GITHUB_OUTPUT'], 'a') as fh:
        print(f"zip_name={zip_name}", file=fh)


if __name__ == "__main__":
    main()