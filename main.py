import sys
import os
import tomli


def load_config(config_path: str):
    if not os.path.isfile(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with open(config_path, "rb") as f:
        return tomli.load(f)


def validate_config(config: dict):
    # Проверка нужных ключей
    required_keys = ["package_name", "repository", "mode", "package_version", "filter_substring"]
    for key in required_keys:
        if key not in config:
            raise ValueError(f"Missing required config key: '{key}'")

    package_name = config["package_name"]
    repository = config["repository"]
    mode = config["mode"]
    package_version = config["package_version"]
    filter_substring = config["filter_substring"]

    # Проверка package_name
    if not isinstance(package_name, str) or not package_name.strip():
        raise ValueError("package_name must be a non-empty string")

    # Проверка repository
    if not isinstance(repository, str) or not repository.strip():
        raise ValueError("repository must be a non-empty string")

    # Проверка mode
    if mode not in ("local", "url"):
        raise ValueError("mode must be either 'local' or 'url'")

    # Проверка package_version
    if not isinstance(package_version, str):
        raise ValueError("package_version must be a string")

    # Проверка filter_substring
    if not isinstance(filter_substring, str):
        raise ValueError("filter_substring must be a string")

    return {
        "package_name": package_name.strip(),
        "repository": repository.strip(),
        "mode": mode,
        "package_version": package_version.strip(),
        "filter_substring": filter_substring.strip(),
    }


def main():
    config_path = "test_repo/config.toml"
    try:
        raw_config = load_config(config_path)
        config = validate_config(raw_config)

        print("Configuration loaded:")
        print(f"package_name = {config['package_name']}")
        print(f"repository = {config['repository']}")
        print(f"mode = {config['mode']}")
        print(f"package_version = {config['package_version']}")
        print(f"filter_substring = {config['filter_substring']}")
        print()


    except (FileNotFoundError, ValueError, OSError) as e:
        print(f"Configuration Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()