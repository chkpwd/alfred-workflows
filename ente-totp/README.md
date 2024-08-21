# An Alfred Workflow that uses your Ente Exports

It's not using a cli so you have to export from the ente app and then manually import them into the workflow's database

## Setup

1. Install workflow from releases
2. Follow instructions below to create the database

## Instructions

1. Open Alfred
2. Go to workflows
3. Right click the Ente 2FA workflow and press Open In Finder.
4. Export in plain text your Ente 2FA codes
5. rename that file to secrets.txt and put it in the folder that got opened previously

![image](https://github.com/user-attachments/assets/0964cb6c-e453-4be9-a8a8-2891001f2762)

It should look something like this
  
6. Open a terminal
7. Run `python main.py import secrets.txt`
8. Run `.ente` in Alfred and let the database populate