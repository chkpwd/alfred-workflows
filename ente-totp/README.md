# An Alfred Workflow that uses your Ente Exports

The Ente Auth CLI does not support exporting TOTP codes. To use this project, please export TOTP codes from the Ente app and then import them into the workflow's database by selecting the export file using the "Configure Workflow" button in the workflow setup. You can import the file using the `ente import` Alfred command. Once imported, you can delete the file.

> [!NOTE]
> In the future, the workflow will take care of the import.
> In addtion, once support for exporting codes via CLI is supported, we will use that instead.

## Setup

1. Install workflow from releases
2. Follow instructions below to create the database

## Instructions

1. Open Alfred
2. Go to Workflows.
3. Click the "Enter 2FA" workflow and click the Configure Workflow button.
4. Next, click the file button next to "Ente Export File" and browse to your Ente Auth plain text export of two-factor codes.
5. Finally, run the Alfred command `ente import`.

## Local Development

### Install dependencies
./build-deps.sh

### Build alfred workflow file
./build.sh

### Update requirements
pip install pip-tools
pip-compile requirements.in