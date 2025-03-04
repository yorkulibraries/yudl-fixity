import click


@click.command()
@click.argument("previous", type=click.Path(exists=True))
@click.argument("recent", type=click.Path(exists=True))
@click.argument("output", type=click.Path())
def process_files(previous, recent, output):
    """Create a new fid list with unique lines a previous and recent list, sorted in descending order.

    Lines that exist only in the most recent fid list but not in the previous
    fid list are excluded from the output.
    """
    with open(previous, "r") as fa, open(recent, "r") as fb:
        lines_previous = {line.strip() for line in fa}
        lines_recent = {line.strip() for line in fb}

    result_lines = lines_previous.union(lines_recent).intersection(lines_previous)

    sorted_lines = sorted(result_lines, reverse=True)

    with open(output, "w") as fc:
        fc.write("\n".join(sorted_lines) + "\n")

    click.echo(f"Processed {previous} and {recent}. Output written to {output}.")


if __name__ == "__main__":
    process_files()
