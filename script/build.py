import argparse
import sqlite3
from pathlib import Path

import yaml
from qzemoji.emojitable import EmojiTable



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


def clean():
    for i in DB_ROOT.iterdir():
        if i.is_dir():
            if i != RAW_ROOT: i.rmdir()
        else:
            i.unlink()


def create_table(name: str):
    db_path = (DB_ROOT / name).with_suffix('.db')
    conn = sqlite3.connect(str(db_path))
    return conn, EmojiTable('emoji', conn.cursor())


def dump_items(name: str = 'emoji'):
    conn, tbl = create_table(name)
    for k, v in collect_items():
        if not v: 
            print(f"{k} null value. Skipped.")
            continue
        tbl[k] = v
    conn.commit()
    tbl.cursor.close()
    conn.close()


def check_dirs():
    for i in [DB_ROOT, RAW_ROOT]:
        if not i.exists(): i.mkdir(parents=True, exist_ok=True)


if __name__ == '__main__':
    psr = argparse.ArgumentParser()
    psr.add_argument('-o', '--outname', default='emoji')
    arg = psr.parse_args()

    check_dirs()
    clean()
    dump_items(arg.outname)
