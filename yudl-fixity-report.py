import requests
import csv
import click
import datetime
import re


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


def extract_datetime(performed):
    """Extract the datetime value from the performed field."""
    match = re.search(r'datetime="([^"]+)"', performed)
    return match.group(1) if match else performed.strip()


@click.command()
@click.option(
    "--credentials",
    type=click.Path(exists=True),
    required=True,
    help="Path to credentials file.",
)
@click.option(
    "--endpoint", type=str, required=True, help="URL for fixity report endpoint."
)
def fetch_fixity_reports(credentials, endpoint):
    """Fetch fixity reports from YUDL and write results to a CSV file."""

    password = get_credentials(credentials)

    today = datetime.datetime.now().strftime("%Y%m%d")
    output_file = f"yudl-fixity-results-{today}.csv"

    with open(output_file, mode="a", newline="", buffering=1) as csvfile:
        writer = csv.writer(csvfile)

        if csvfile.tell() == 0:
            writer.writerow(
                ["Filename", "Fixity State", "Media ID", "File ID", "Performed"]
            )
        csvfile.flush()

        page = 0
        while True:
            url = f"{endpoint}?page={page}"
            click.echo(f"Fetching page {page}.")
            response = requests.get(url, auth=("admin", password))

            if response.status_code != 200:
                click.echo(f"Error fetching data from {url}: {response.status_code}")
                break

            data = response.json()

            if not data:
                click.echo("No more results. Stopping.")
                break

            stop_pagination = False
            for record in data:
                file_1 = record.get("file_1", "").strip()
                fid = record.get("fid", "").strip()

                if not file_1 or not fid:
                    stop_pagination = True
                    break

                state = record.get("state", "").strip()
                mid = record.get("mid", "").strip()
                performed_raw = record.get("performed", "").strip()
                performed = extract_datetime(performed_raw)

                writer.writerow([file_1, state, mid, fid, performed])
                csvfile.flush()

            if stop_pagination:
                click.echo("Empty file_1 or fid detected. Stopping.")
                break

            page += 1

    click.echo(f"Fixity report saved to {output_file}.")


if __name__ == "__main__":
    fetch_fixity_reports()
