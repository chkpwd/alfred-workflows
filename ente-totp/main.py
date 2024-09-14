import json
import logging
import pathlib
import os
from collections import defaultdict
from datetime import datetime, timedelta

import click
import pyotp

DB_FILE = pathlib.Path.home() / ".local/share/ente-totp/db.json"
USERNAME_IN_TITLE = os.getenv("username_in_title", "false").lower() in ("true", "1", "t", "y", "yes")
USERNAME_IN_SUBTITLE = os.getenv("username_in_subtitle", "false").lower() in ("true", "1", "t", "y", "yes")


@click.group()
def cli():
    pass


@cli.command("import")
@click.argument("file", type=click.Path(exists=False), required=False)
def import_file(file):
    try:
        logging.warning(f"import_file: {file}")
        secret_dict = defaultdict(list)  # less strict than regular dict
        for service_name, username, secret in parse_secrets(file):
            secret_dict[service_name].append((username, secret))
        DB_FILE.parent.mkdir(parents=True, exist_ok=True)
        with DB_FILE.open("w") as json_file:
            json.dump(secret_dict, json_file, indent=2)

        logging.warning(f"Database created with {sum(len(v) for v in secret_dict.values())} entries.")

        print(json.dumps({"items": [{"title": "Import Successful",
                                     "subtitle": f"Database created with {sum(len(v) for v in secret_dict.values())} entries."}]}))
    except FileNotFoundError:
        error_message = f"File not found: {file}"
        logging.error(error_message)
        print(json.dumps({"items": [{"title": "Import Failed", "subtitle": error_message}]}))
    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        logging.error(error_message)
        print(json.dumps({"items": [{"title": "Import Failed", "subtitle": error_message}]}))


def parse_secrets(file_path="secrets.txt"):
    secrets_list = []

    with open(file_path, "r") as secrets_file:
        for line in secrets_file:
            line = line.strip()
            if line:
                line = line.replace("=sha1", "=SHA1")
                if "codeDisplay" in line:
                    line = line.split("codeDisplay")[0][:-1]

                parsed_uri = pyotp.parse_uri(line)
                if parsed_uri:
                    service_name = parsed_uri.issuer or parsed_uri.name
                    username = parsed_uri.name
                    secret = parsed_uri.secret
                    if secret:
                        secrets_list.append((service_name, username, secret))
                    else:
                        print(f"Unable to parse secret in: {line}")
                else:
                    print(f"Unable to parse the line: {line}")
    return secrets_list


def format_data(service_name, username, current_totp, next_totp, output_type):
    """Format the data based on the output type."""
    subset = f"Current TOTP: {current_totp} | Next TOTP: {next_totp}" + (
        f" - {username}" if username and USERNAME_IN_SUBTITLE else "")
    service_name = f"{service_name} - {username}" if username and USERNAME_IN_TITLE else service_name

    if output_type == "alfred":
        return {
            "title": service_name,
            "subtitle": subset,
            "arg": current_totp,
            "icon": {"path": "./icon.png"},
        }

    elif output_type == "json":
        return {
            "service_name": service_name,
            "current_totp": current_totp,
            "next_totp": next_totp,
            "service_data": subset,
        }

    return None


@cli.command("get")
@click.argument("secret_id")
@click.option(
    "-o",
    "output_format",
    type=click.Choice(["json", "alfred"]),
    default="json",
    help="Data output format",
)
def generate_totp(secret_id, output_format):
    try:
        with open(DB_FILE, "r") as file:
            data = json.load(file)
        items = []  # Collect all items in this list
        logging.warning(f"Searching for {secret_id} in {len(data)} services.\n")
        for service_name, service_data in data.items():
            if secret_id.lower() in service_name.lower():
                for username, secret in service_data:
                    current_totp = pyotp.TOTP(secret).now()
                    next_time = datetime.now() + timedelta(seconds=30)
                    next_totp = pyotp.TOTP(secret).at(next_time)
                    formatted_data = format_data(
                        service_name, username, current_totp, next_totp, output_format
                    )
                    if formatted_data:
                        items.append(formatted_data)

        if items:
            print(json.dumps({"items": items}, indent=4))
        else:
            print("No matching services found.")

    except Exception as e:
        logging.warning(f"Error: {str(e)}")
        print(json.dumps({"items": [], "error": str(e)}, indent=4))


if __name__ == "__main__":
    cli()
