from pathlib import Path

import yaml

RAW_ROOT = Path('data/raw')
DB_ROOT = Path('data')
YML_EXT = ['.yml', '.yaml']


def collect_files():
    for i in RAW_ROOT.iterdir():
        if i.suffix in YML_EXT:
            yield i


def collect_items():
    for f in collect_files():
        with open(f, encoding='utf8') as f:
            d: dict = yaml.safe_load(f) or {}
            assert isinstance(d, dict)
            yield from d.items()
