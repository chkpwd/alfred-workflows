import sys
import os

# Add the vendor directory to the path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'vendor'))

import json
import logging
from collections import defaultdict
from datetime import datetime, timedelta

import click
import pyotp
import keyring

USERNAME_IN_TITLE = os.getenv("username_in_title", "false").lower() in ("true", "1", "t", "y", "yes")
USERNAME_IN_SUBTITLE = os.getenv("username_in_subtitle", "false").lower() in ("true", "1", "t", "y", "yes")

# Keychain service and account for storing the secrets
KEYCHAIN_SERVICE = "ente-totp-alfred-workflow"
KEYCHAIN_ACCOUNT = "totp_secrets"

# Use an environment variable to cache the JSON data to reduce keychain calls
CACHE_ENV_VAR = "TOTP_CACHE"


def load_secrets():
    """Load secrets from the environment variable or keychain."""
    # Try to load from the cached environment variable first
    cached_secrets = os.getenv(CACHE_ENV_VAR)

    if cached_secrets:
        logging.warning("Loading secrets from environment variable cache.")
        return json.loads(cached_secrets)

    # If not cached, load from the keychain
    logging.warning("Loading secrets from keychain.")
    secrets_json = keyring.get_password(KEYCHAIN_SERVICE, KEYCHAIN_ACCOUNT)

    if secrets_json is None:
        raise Exception("No secrets found in keychain.")

    return json.loads(secrets_json)

@click.group()
def cli():
    pass


@cli.command("import")
@click.argument("file", type=click.Path(exists=False), required=False)
def import_file(file):
    try:
        logging.warning(f"import_file: {file}")
        secret_dict = defaultdict(list)
        for service_name, username, secret in parse_secrets(file):
            secret_dict[service_name].append((username, secret))

        secrets_json = json.dumps(secret_dict)
        # Store secrets in the keychain
        if secrets_json:
            keyring.set_password(KEYCHAIN_SERVICE, KEYCHAIN_ACCOUNT, secrets_json)

        logging.warning(f"Database created with {sum(len(v) for v in secret_dict.values())} entries.")
        output = {
            "items": [
                {"title": "Import Successful",
                 "subtitle": f"Database created with {sum(len(v) for v in secret_dict.values())} entries."}
            ],
            "variables": {
                CACHE_ENV_VAR: secrets_json  # Set the TOTP_CACHE environment variable for Alfred
            }
        }
        print(json.dumps(output))

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
    """Format the TOTP data based on the output type."""
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
    """Generate the current TOTP for a given secret."""
    try:
        # Load secrets from the cache or keychain
        data = load_secrets()
        items = []

        logging.warning(f"Searching for {secret_id} in {len(data)} services.\n")

        # Split the secret_id by spaces for more granular search
        search_parts = secret_id.lower().split()

        matches = []

        for service_name, service_data in data.items():
            for username, secret in service_data:
                # Lowercase the service_name and username for case-insensitive matching
                service_name_lower = service_name.lower()
                username_lower = username.lower()

                # Define match scores for prioritization
                score = 0
                if all(part in service_name_lower for part in search_parts):
                    score += 3  # Full match in service name
                if all(part in username_lower for part in search_parts):
                    score += 2  # Full match in username
                if any(part in service_name_lower for part in search_parts):
                    score += 1  # Partial match in service name
                if any(part in username_lower for part in search_parts):
                    score += 0.5  # Partial match in username

                if score > 0:
                    # Generate TOTP for the matching service
                    current_totp = pyotp.TOTP(secret).now()
                    next_time = datetime.now() + timedelta(seconds=30)
                    next_totp = pyotp.TOTP(secret).at(next_time)
                    formatted_data = format_data(
                        service_name, username, current_totp, next_totp, output_format
                    )
                    matches.append((score, formatted_data))

        # Sort matches by score in descending order
        matches.sort(reverse=True, key=lambda x: x[0])
        items = [match[1] for match in matches]  # Extract the formatted results

        # Set the output JSON with the items (either matching services or no matches)
        if items:
            output = {
                "items": items,
            }
        else:
            output = {
                "items": [{"title": "No matching services found."}]
            }

        # Always check if the secrets were cached, and include the cache variable
        if os.getenv(CACHE_ENV_VAR) is None:
            secrets_json = json.dumps(data)
            output["variables"] = {
                CACHE_ENV_VAR: secrets_json
            }

        print(json.dumps(output, indent=4))

    except Exception as e:
        logging.warning(f"Error: {str(e)}")
        print(json.dumps({"items": [], "error": str(e)}, indent=4))


if __name__ == "__main__":
    cli()
