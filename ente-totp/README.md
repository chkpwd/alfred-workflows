# An Alfred Workflow that uses your Ente Exports

Ente Auth CLI does [not support](https://github.com/ente-io/ente/discussions/716) exporting TOTP codes. To use this project, please export from the Ente app and then
and then import them into the workflow's database by choosing the export file using the "Configure Workflow" button 
in the workflow setup and then import using the 'ente import' Alfred command. 

The file can be deleted once imported.

> [!NOTE]
> In the future, the workflow will take care of the import.
> In addtion, once support for exporting codes via CLI is supported, we will use that instead.

## Setup

1. Install workflow from releases
2. Follow instructions below to create the database

## Instructions

1. Open Alfred
2. Go to workflows
3. Click the Ente 2FA workflow and click the Configure Workflow button
4. Click the file button next to the Ente Export File and browse to the Ente Auth plain text export of your two factor codes
5. Run the alfred command 'ente import'