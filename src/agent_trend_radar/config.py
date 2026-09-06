import yaml

DEFAULT_TARGETS_PATH = "config/targets.yaml"


def load_targets(path: str = DEFAULT_TARGETS_PATH) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data["targets"]
