#!/usr/bin/env python3
"""Verify and unpack the AMR reproduction package using standard-library tools."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import shutil
import stat
import zipfile


def digest(path):
    result = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            result.update(block)
    return result.hexdigest()


def safe_name(name):
    path = PurePosixPath(name)
    if path.is_absolute() or '..' in path.parts or '\\' in name or ':' in name:
        raise ValueError('Unsafe package path: ' + name)
    return path


def manifest(path):
    result = {}
    for line in path.read_text(encoding='utf-8').splitlines():
        checksum, name = line.split('  ', 1)
        safe_name(name)
        if name in result:
            raise ValueError('Duplicate manifest entry: ' + name)
        result[name] = checksum
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, help='Destination; default: research_reproduction beside this script')
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    output = (args.output or root / 'research_reproduction').resolve()
    if output == root:
        raise ValueError('Choose a separate output directory.')

    upload = manifest(root / 'FILES_SHA256.txt')
    for name, checksum in upload.items():
        if not (root / name).is_file() or digest(root / name) != checksum:
            raise ValueError('Missing or changed upload file: ' + name)
    print('Upload checksums verified.', flush=True)

    layout = json.loads((root / 'PAYLOADS.json').read_text(encoding='utf-8'))
    expected = manifest(root / 'MANIFEST_SHA256.txt')
    planned = set(layout['documents'])
    if len(planned) != len(layout['documents']):
        raise ValueError('Duplicate document.')
    for name in planned:
        safe_name(name)
        if name not in upload:
            raise ValueError('Unverified document: ' + name)

    # Inspect all member names and the inventory before writing any output.
    for archive in layout['archives']:
        if archive not in upload:
            raise ValueError('Unverified archive: ' + archive)
        with zipfile.ZipFile(root / archive) as source:
            for info in source.infolist():
                safe_name(info.filename)
                if info.is_dir() or stat.S_ISLNK(info.external_attr >> 16):
                    raise ValueError('Unexpected directory or symlink: ' + info.filename)
                if info.filename in planned:
                    raise ValueError('Duplicate archive member: ' + info.filename)
                planned.add(info.filename)
    if planned != set(expected):
        raise ValueError('Payload inventory differs from the package manifest.')

    output.mkdir(parents=True, exist_ok=True)
    for name in planned | {'MANIFEST_SHA256.txt'}:
        destination = output / name
        if destination.resolve() != output.joinpath(*safe_name(name).parts):
            raise ValueError('Output path contains a symlink: ' + name)
        wanted = expected.get(name, upload['MANIFEST_SHA256.txt'])
        if destination.exists() and (not destination.is_file() or digest(destination) != wanted):
            raise ValueError('Existing output differs; choose an empty directory: ' + name)

    for name in layout['documents'] + ['MANIFEST_SHA256.txt']:
        shutil.copyfile(root / name, output / name)
    for archive in layout['archives']:
        print('Unpacking ' + archive, flush=True)
        with zipfile.ZipFile(root / archive) as source:
            for info in source.infolist():
                destination = output / info.filename
                if destination.exists():
                    continue
                destination.parent.mkdir(parents=True, exist_ok=True)
                with source.open(info) as inp, destination.open('xb') as out:
                    shutil.copyfileobj(inp, out)
                if digest(destination) != expected[info.filename]:
                    raise ValueError('Extracted checksum mismatch: ' + info.filename)
    for name, checksum in expected.items():
        if digest(output / name) != checksum:
            raise ValueError('Final checksum mismatch: ' + name)
    print(f'Verified {len(expected):,} files in {output}', flush=True)
    metadata = json.loads((output / 'metadata.json').read_text(encoding='utf-8'))
    print(f"Executions: {metadata['total_reported_executions']:,}; "
          f"identified timing replays: {metadata['accurate_dispatch_batch_timing_replays']}; "
          f"release: {metadata['version']}.")


if __name__ == '__main__':
    main()
