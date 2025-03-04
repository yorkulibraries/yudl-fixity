# YUDL Fixity

Utiliites to assist in periodic fixity verification for York University Digital Library.

## Utilities

```
Usage: fetch-fids.py [OPTIONS]

  Fetch file ids (fids) from YUDL and write them to files.

Options:
  --credentials PATH  Path to the credentials file.  [required]
  --base-url TEXT     Base URL for the fid api endpoints (e.g.,
                      https://digital.library.yorku.ca).  [required]
  --endpoints TEXT    Comma-separated list of the fid api endpoints or 'all'.
                      [required]
  --help              Show this message and exit.
```

```
Usage: fixity-list.py [OPTIONS] PREVIOUS RECENT OUTPUT

  Create a new fid list with unique lines a previous and recent list, sorted
  in descending order.

  Lines that exist only in the most recent fid list but not in the previous
  fid list are excluded from the output.

Options:
  --help  Show this message and exit.
```

```
Usage: yudl-fixity-report.py [OPTIONS]

  Fetch fixity reports from YUDL and write results to a CSV file.

Options:
  --credentials PATH  Path to credentials file.  [required]
  --endpoint TEXT     URL for fixity report endpoint.  [required]
  --help              Show this message and exit.
```

## License

[Unlicense](https://unlicense.org/)
