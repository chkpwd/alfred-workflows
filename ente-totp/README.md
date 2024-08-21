# An Alfred Workflow that uses your Ente Exports

Ente Auth does [not support](https://github.com/ente-io/ente/discussions/716) exporting TOTP codes. To use this project, please export from the Ente app and then manually import them into the workflow's database using the `import` parameter.

> [!NOTE] **Note**: In the future, the workflow will take care of the import.

## Setup

1. Install workflow from releases
2. Follow instructions below to create the database

## Instructions

1. Open Alfred
2. Go to workflows
3. Right click the Ente 2FA workflow and press Open In Finder.
4. Export in plain text your Ente 2FA codes
5. Rename that file to secrets.txt and put it in the folder that got opened previously

![image](https://github.com/user-attachments/assets/0964cb6c-e453-4be9-a8a8-2891001f2762)

It should look something like this

6. Open a terminal
7. Navigate to the folder that got contains the `main.py` file
8. Run `python main.py import secrets.txt`
9. Run `ente` in Alfred and let the database populate

