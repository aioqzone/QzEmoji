import argparse
from pathlib import Path

from qzemoji.hash import hash_stream, prepare_png
from qzemoji.sql import EmojiTable, HashTable
from sqlmodel import create_engine

RAW_ROOT = Path('data/raw')
EMOJI_ROOT = Path('data/emoji')
DB_ROOT = Path('data')
YML_EXT = ['.yml', '.yaml']


def clean():
    skip = RAW_ROOT, EMOJI_ROOT
    for i in DB_ROOT.iterdir():
        if i.is_dir():
            if i not in skip: i.rmdir()
        else:
            i.unlink()


def create_table(name: str):
    db_path = (DB_ROOT / name).with_suffix('.db')
    hash_path = db_path.with_suffix('.hash.db')
    db_conn = create_engine('sqlite:///' + db_path.as_posix())
    hash_conn = create_engine('sqlite:///' + hash_path.as_posix())
    return EmojiTable(db_conn), HashTable(hash_conn)


def dump_items(name: str = 'emoji'):
    emo, htb = create_table(name)
    for k, v in hash_stream():
        if not v.text:
            print(f"{k} null value. Skipped.")
            continue
        emo[k] = v.text
        assert (v.rgb) not in htb
        htb.add(v)
    emo.sess.commit()
    htb.sess.commit()


def check_dirs():
    for i in [DB_ROOT, RAW_ROOT]:
        if not i.exists(): i.mkdir(parents=True, exist_ok=True)


if __name__ == '__main__':
    psr = argparse.ArgumentParser()
    psr.add_argument('-o', '--outname', default='emoji')
    psr.add_argument('-v', '--verbose')
    arg = psr.parse_args()

    if arg.verbose:
        import qzemoji.hash.download
        qzemoji.hash.download.verbose = True

    check_dirs()
    clean()
    prepare_png()
    dump_items(arg.outname)
