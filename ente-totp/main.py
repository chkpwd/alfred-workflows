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
    """Import secrets from the given file and create a database."""
    secret_dict = defaultdict(list) # uses parameterless lambda to create a new list for each key

    for service_name, username, secret in parse_secrets(file):
        secret_dict[service_name].append((username, secret))

    # Create directory if it doesn't exist
    DB_FILE.parent.mkdir(parents=True, exist_ok=True)

    with DB_FILE.open("w") as json_file:
        json.dump(secret_dict, json_file, indent=2)

    print("Database created.")

def parse_secrets(file_path="secrets.txt"):
    """Parse the secrets from the given file."""
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

def format_data(service_name, service_data, output_type):
    """Format the data based on the output type."""
    json_data = []
    for username, secret in service_data:
        totp = pyotp.TOTP(secret)
        current_code = totp.now()
        
        if output_type == 'json':
            json_data.append({
                "name": username,
                "totp": current_code
            })
        
        elif output_type == 'alfred':
            json_data.append({
                "title": service_name,
                "subtitle": current_code,
                "arg": current_code,
                "icon": {
                    "path": "./icon.png"
                }
            })
        
        elif output_type == 'print':
            print(f'\t{username}: {current_code}')

    if output_type in ['json', 'alfred']:
        results = {"items": json_data}
        return json.dumps(results, indent=4)
    
    return None

@cli.command('get')
@click.argument('secret_id')
@click.option("-j","json_output", is_flag=True)
@click.option("-a","alfred_output", is_flag=True)
def generate_totp(secret_id, json_output, alfred_output):
    """Generate TOTP for the given secret_id."""
    try:
        with open(DB_FILE, "r") as file:
            data = json.load(file)
        
        totp_data = None
        for service_name, service_data in data.items():
            if secret_id.lower() == service_name.lower():
                totp_data = service_name, service_data
                break

        if totp_data:
            service_name, service_data = totp_data
            
            # Determine the output type
            if json_output:
                output_type = 'json'
            elif alfred_output:
                output_type = 'alfred'
            else:
                output_type = 'print'
            
            output = format_data(service_name, service_data, output_type)
            
            if output:
                print(output)

        else:
            # return an empty array in "items"
            print(json.dumps({"items": []}, indent=4))
    
    except Exception as e:
        print(json.dumps({"items": [], "error": str(e)}, indent=4))


if __name__ == "__main__":
    cli()

