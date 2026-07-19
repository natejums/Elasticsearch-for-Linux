# Elasticsearch-for-Linux

A single 35-line Python script that walks a folder, indexes every file it finds into a local Elasticsearch index, then runs one full-text search over their contents.

Published as-is from February 2023. **It will not run against a current `elasticsearch` install** — see [Known issues](#known-issues) before you try.

## What it does

`ElasticFileSearch.py` performs one non-repeating index-then-search pass:

1. Prompts for a folder path and walks it recursively with `os.walk`.
2. Reads **every** file it encounters as text and indexes it into a local index named `files`, storing two fields, `path` and `content`. There is no extension allowlist, no MIME sniffing, and no skip logic of any kind.
3. Prompts for a search string and runs a `match` query against `content`.
4. Prints the `path` of each hit, one per line.

That is the entire program: two functions, `index_files(es, root_folder)` and `search_files(es, query)`, plus a `__main__` block.

Despite the repository name, nothing in the code is Linux-specific. It uses `os.walk` and `os.path.join` and behaves identically on macOS and Windows.

## Requirements

- **Python 3.** No minimum version is pinned anywhere in the repo.
- **A running Elasticsearch server** on the same machine, reachable at the client default `localhost:9200`. The script does not start one for you.
- **`elasticsearch-py` 7.x**, pinned below 8 — see below.

## Install

There is no `requirements.txt`, `pyproject.toml`, or `setup.py` here, so there is nothing to install the project itself from. Install the client directly and pin it:

```
pip install "elasticsearch<8"
```

## Usage

```
python3 ElasticFileSearch.py
```

No arguments or flags — there is no `argparse` and no `sys.argv` use. It asks two questions:

```
Enter the root folder path: /home/you/notes
Enter the search query: quarterly report
```

## Known issues

Real, reproducible defects:

- **It does not run on a modern client.** A plain `pip install elasticsearch` gets 8.x or newer, where the no-argument `Elasticsearch()` constructor is no longer valid (hosts must be given explicitly) and `doc_type=` is gone from `index()`. `body=` was deprecated across 8.x and dropped in 9.0. Any one of those fails at startup. Pin to `elasticsearch<8`. Note that `doc_type=` was *already* deprecated in the 7.x client — mapping types were removed from Elasticsearch 7 servers — so it was legacy usage even when this was written.
- **One binary file kills the whole run.** Files are opened with `open(file_path, 'r')` — no encoding, no `errors=` handler, and no `try`/`except` anywhere in the file. The first file whose bytes are not valid text raises `UnicodeDecodeError` and aborts indexing. `os.walk` does not skip dotfiles, so pointing this at any directory containing a `.git` folder crashes it immediately.
- **Re-running duplicates everything.** No document ID is passed to `es.index()`, so Elasticsearch generates a fresh one per call. Every run re-indexes the whole tree as new documents and the index grows without bound. There is no dedup or cleanup path.
- **No error handling at all.** A refused connection, an unreadable file, or a nonexistent folder each surface as a raw traceback.
- **Results are capped at 10.** `es.search()` passes no `size`, so it returns the Elasticsearch default, with no pagination and no warning that results were truncated.
- **Indexing and searching cannot be run separately.** They are welded into one pass: no way to search an existing index without re-indexing first, and no way to index without being dropped into a search prompt.
- **Nothing is configurable.** The index name `files`, the doc type `file`, and the implicit `localhost:9200` host are hardcoded. The index name appears on two lines, so renaming it means editing both.
- **No authentication or TLS support.** There is no `api_key`, `basic_auth`, or `ca_certs`. Elasticsearch 8 enables TLS and auth by default, so this would not connect to a stock modern server even with the client version fixed.
- **The folder path is not validated** and gets no `expanduser()`, so answering `~/Documents` silently walks nothing and indexes nothing. Use an absolute path.
- **Whole files are read into memory.** `f.read()` ships each file as one document with no size cap, so a large log can exhaust memory or exceed Elasticsearch's default 100 MB request limit.
- **Search may run before the index is ready.** Nothing refreshes the index after writing and the default refresh interval is about a second. This works only because a human takes longer than that to answer the second prompt; piped input may search a stale index.
- **Only files are indexed.** `dirs` is unpacked from `os.walk` and never used again, so directories are traversed but never become searchable documents.
- No shebang, no tests, no CI, no type hints, no `.gitignore`.

## Status

Unmaintained. Kept for reference rather than use.

## License

MIT — see [LICENSE](LICENSE).
