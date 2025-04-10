import sys
import toml


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in ("patch", "minor", "major"):
        print("Usage: python bump_version.py [patch|minor|major]")
        sys.exit(1)

    bump_type = sys.argv[1]

    pyproject_path = "pyproject.toml"
    data = toml.load(pyproject_path)

    try:
        version_str = data["project"]["version"]
    except KeyError:
        print("Version string not found in pyproject.toml")
        sys.exit(1)

    major, minor, patch = map(int, version_str.split("."))

    if bump_type == "patch":
        patch += 1
    elif bump_type == "minor":
        minor += 1
        patch = 0
    elif bump_type == "major":
        major += 1
        minor = 0
        patch = 0

    new_version = f"{major}.{minor}.{patch}"
    data["project"]["version"] = new_version

    with open(pyproject_path, "w", encoding="utf-8") as f:
        toml.dump(data, f)

    print(new_version)


if __name__ == "__main__":
    main()
