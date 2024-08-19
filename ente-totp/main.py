import json
import pathlib
from collections import defaultdict
from urllib.parse import parse_qs, unquote, urlparse

import click
import pyotp

DB_FILE = pathlib.Path.home() /".local/share/ente-totp/db.json"

@click.group()
def cli():
   pass

@cli.command('import')
@click.argument("file", type=click.Path(exists=True))
def import_file(file):
    secret_dict = defaultdict(list) # uses parameterless lambda to create a new list for each key

    for service_name, username, secret in parse_secrets(file):
        secret_dict[service_name].append((username, secret))

    # Create directory if it doesn't exist
    DB_FILE.parent.mkdir(parents=True, exist_ok=True)

    with DB_FILE.open("w") as json_file:
        json.dump(secret_dict, json_file, indent=2)

    print("Database created.")

def parse_secrets(file_path="secrets.txt"):
    secrets_list = []
    
    with open(file_path, "r") as secrets_file:
        for line in secrets_file:
            line = line.strip()
            if line:
                parsed_url = urlparse(line)
                if parsed_url.scheme == "otpauth":
                    path_items = unquote(parsed_url.path).strip('/').split(':', 1)
                    if len(path_items) == 2:
                        service_name, username = path_items[0], path_items[1]
                    else:
                        service_name, username = path_items[0].strip(':'), ""
                    query_params = parse_qs(parsed_url.query)
                    secret = query_params.get("secret", [None])[0]
                    if secret:
                        secrets_list.append((service_name, username, secret))
    
    return secrets_list

def output_data(totp_data, output_format):
    json_data = []
    for service_name, service_data in totp_data:
        if output_format not in ["json", "alfred"]:
            print(f"Service: {service_name}")
        for username, secret in service_data:
            totp = pyotp.TOTP(secret)
            current_code = totp.now()
            
            if output_format == "json":
                json_data.append({
                    "name": username,
                    "totp": current_code
                })
            
            elif output_format == "alfred":
                json_data.append({
                    "title": service_name,
                    "subtitle": username,
                    "arg": current_code,
                    "icon": {
                        "path": "./icon.png"
                    }
                })
            
            else:
                if username:
                    print(f'\t{username}: {current_code}')
                else:
                    print(f'\t{current_code}')

    if output_format in ["json", "alfred"]:
        results = {"items": json_data}
        print(json.dumps(results, indent=4))
    
    elif not totp_data:
        print("No matching service found")
    
@cli.command('get')
@click.argument('secret_id')
@click.option("-o","output_format", type=click.Choice(["json", "alfred", "alien"]), default="alien", help="Data output format")
def generate_totp(secret_id, output_format):
    try:
        with open(DB_FILE, "r") as file:
            data = json.load(file)
        
        totp_data = []
        for service_name, service_data in data.items():
            if secret_id.lower() in service_name.lower():
                totp_data.append((service_name, service_data))

        if totp_data:
            output_data(totp_data, output_format)
            
        else:
            # return an empty array in "items"
            output_data([(secret_id.lower(), [])], output_format)
    
    except Exception as e:
        print(json.dumps({
            "items": [{
                "title": "error",
                "subtitle": str(e),
                "arg": str(e),
                "icon": {
                    "path": "./icon.png"
                }
            }]
        }, indent=4))

if __name__ == "__main__":
    cli()

