# main.py
import sys
import os

try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib
    except ImportError:
        print(" Установите 'tomli': pip install tomli", file=sys.stderr)
        sys.exit(1)

from cargo_parsery import get_cargo_toml_urls, fetch_cargo_toml, parse_dependencies_from_cargo_toml


def load_config(path: str):
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Файл конфигурации не найден: {path}")

    with open(path, "rb") as f:
        cfg = tomllib.load(f)

    required = ["package_name", "repository_url", "mode", "version", "filter_substring"]
    for key in required:
        if key not in cfg:
            raise ValueError(f"Отсутствует обязательный параметр: '{key}'")

    if cfg["mode"] not in ("git", "local"):
        raise ValueError("Режим должен быть 'git' или 'local'")


    for k in cfg:
        if isinstance(cfg[k], str):
            cfg[k] = cfg[k].strip()

    return cfg


def main():
    cfg = load_config("config.toml")

    print(" Загруженные параметры:")
    labels = {
        "package_name": "Имя пакета",
        "repository_url": "URL репозитория",
        "mode": "Режим работы",
        "version": "Версия пакета",
        "filter_substring": "Фильтр по подстроке"
    }
    for key, label in labels.items():
        print(f"{label}: {cfg[key]!r}")
    print()

    if cfg["mode"] != "git":
        print("  Режим 'local' не поддерживается.")
        return

    print(" Генерация возможных ссылок на Cargo.toml...")
    urls = get_cargo_toml_urls(cfg["repository_url"], cfg["version"])
    for u in urls:
        print(f"  • {u}")
    print()

    print(" Загрузка Cargo.toml...")
    content = fetch_cargo_toml(urls)
    print(" Успешно загружен!")
    print()

    print(" Поиск прямых зависимостей...")
    deps = parse_dependencies_from_cargo_toml(content, cfg["filter_substring"])

    if deps:
        print("Найдены прямые зависимости:")
        for name in sorted(deps):
            print(f"  • {name} — версия {deps[name]}")
    else:
        note = f" (фильтр: «{cfg['filter_substring']}»)" if cfg['filter_substring'] else ""
        print(f"  Зависимости не найдены{note}.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f" Ошибка: {e}", file=sys.stderr)
        sys.exit(1)