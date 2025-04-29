import subprocess


def main():
    subprocess.run(["poetry", "run", "solara", "run", "disease_spread.app"])


if __name__ == "__main__":
    main()
