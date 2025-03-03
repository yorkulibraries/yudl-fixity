import os
import click
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime


def get_credentials(credentials_path):
    """Retrieve credentials from a file."""
    try:
        with open(credentials_path, "r") as f:
            for line in f.readlines():
                if line.startswith("password"):
                    return line.split(" ")[-1].strip()
    except FileNotFoundError:
        click.echo(f"Error: credentials file not found at {credentials_path}", err=True)
        exit(1)
    except Exception as e:
        click.echo(f"Error reading credentials file: {e}", err=True)
        exit(1)
    return None


def get_current_date():
    """Return the current date in YYYYMMDD format."""
    return datetime.now().strftime("%Y%m%d")


def fetch_fids(endpoint, credentials_path):
    """Fetch fids from an endpoint and handle pagination."""
    page = 0
    password = get_credentials(credentials_path)

    while True:
        url = f"{endpoint}?page={page}"
        click.echo(f"Fetching page {page} from {url}")
        response = requests.get(url, auth=HTTPBasicAuth("admin", password))

        if response.status_code != 200:
            click.echo(
                f"Error fetching data from {url}. Status code: {response.status_code}"
            )
            break

        if not response.text.strip():
            click.echo(f"Empty response received from {url}, stopping.")
            break

        try:
            data = response.json()
        except ValueError:
            click.echo(f"Invalid JSON response from {url}, stopping.", err=True)
            break

        if not data:
            click.echo(f"No data received from {url}, stopping.")
            break

        fids = [item["fid"] for item in data if "fid" in item]

        if not fids or all(fid == "" for fid in fids):
            click.echo(f"All fids empty on page {page}, stopping.")
            break

        if "" in fids:
            fids = fids[: fids.index("")]
            yield fids
            break
        else:
            yield fids

        page += 1


def write_fids_to_file(file_name, fids):
    """Write fids to a file."""
    with open(file_name, "a") as f:
        for fid in fids:
            f.write(f"{fid}\n")


@click.command()
@click.option(
    "--credentials",
    type=click.Path(exists=True),
    required=True,
    help="Path to the credentials file.",
)
@click.option(
    "--base-url",
    type=str,
    required=True,
    help="Base URL for the fid api endpoints (e.g., https://digital.library.yorku.ca).",
)
@click.option(
    "--endpoints",
    type=str,
    required=True,
    help="Comma-separated list of the fid api endpoints or 'all'.",
)
def main(credentials, base_url, endpoints):
    """Fetch file ids (fids) from YUDL and write them to files."""
    base_url = base_url.rstrip("/")
    available_endpoints = ["audio", "documents", "files", "images", "videos"]

    selected_endpoints = (
        available_endpoints if endpoints == "all" else endpoints.split(",")
    )

    for key in selected_endpoints:
        if key not in available_endpoints:
            click.echo(f"Skipping unknown endpoint: {key}", err=True)
            continue

        endpoint_url = f"{base_url}/{key}"
        click.echo(f"Processing endpoint: {key}")

        current_date = get_current_date()
        file_name = f"yudl-fids-{key}-{current_date}.txt"

        empty_response = True
        for fids in fetch_fids(endpoint_url, credentials):
            write_fids_to_file(file_name, fids)
            empty_response = False

        if empty_response:
            click.echo(f"No valid fids found for {key}, skipping file creation.")


if __name__ == "__main__":
    main()
