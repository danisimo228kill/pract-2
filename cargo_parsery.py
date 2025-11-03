import urllib.request
import urllib.error
from typing import Dict, List


def get_cargo_toml_urls(repo_url: str, version: str) -> List[str]:

    if not repo_url.startswith("https://github.com/"):
        raise ValueError("Поддерживается только GitHub (начинается с https://github.com/)")
    raw = repo_url.replace("github.com", "raw.githubusercontent.com")
    urls = [
        f"{raw}/{version}/Cargo.toml",
        f"{raw}/v{version}/Cargo.toml"
    ]
    return urls


def fetch_cargo_toml(urls: List[str]) -> str:

    for url in urls:
        try:
            with urllib.request.urlopen(url) as resp:
                return resp.read().decode("utf-8")
        except urllib.error.HTTPError as e:
            if e.code == 404:
                continue
            else:
                raise RuntimeError(f"HTTP {e.code} при загрузке: {url}")
        except Exception as e:
            raise RuntimeError(f"Ошибка сети: {e}")
    raise RuntimeError(f"Cargo.toml не найден по адресам:\n  " + "\n  ".join(urls))


def parse_dependencies_from_cargo_toml(content: str, filter_sub: str = "") -> Dict[str, str]:

    lines = content.splitlines()
    in_deps = False
    deps = {}

    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        if line == "[dependencies]":
            in_deps = True
            continue

        if in_deps and line.startswith("["):
            break

        if in_deps and "=" in line:
            try:
                name_part, val_part = line.split("=", 1)
                name = name_part.strip()
                if filter_sub and filter_sub.lower() not in name.lower():
                    continue

                val_part = val_part.strip()


                if val_part.startswith(("'", '"')) and not val_part.startswith(("{", "[")):
                    version = val_part.strip("'\"")
                    deps[name] = version

                elif val_part.startswith("{"):
                    if "version" in val_part:

                        parts = val_part[1:-1].split(",")
                        for part in parts:
                            if "version" in part:
                                ver = part.split("=")[1].strip().strip("'\"")
                                deps[name] = ver
                                break

            except Exception:
                continue

    return deps