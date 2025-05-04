import subprocess


def main():
    subprocess.run(["poetry", "run", "solara", "run", "virusx.app"])


if __name__ == "__main__":
    main()
