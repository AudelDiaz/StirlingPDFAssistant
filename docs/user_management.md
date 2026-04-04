# User Management & Access Control

To ensure privacy and prevent unauthorized use of system resources, the Stirling PDF Assistant implements a strict access control system.

## Authentication Mechanism

The bot uses a **whitelisting** approach. Every incoming message is intercepted by the `restricted` decorator (`decorators.py`), which checks the user's ID against a list of authorized IDs.

### The Owner
A single `BOT_OWNER_ID` is defined in the environment variables. This user:
- Is always authorized.
- Can add or remove other users via commands.
- Receives access requests from new users.

## Access Request Workflow

When an unauthorized user starts the bot:
1. They see a "Request Access" button.
2. Clicking it prompts them to share their **Contact** (providing their name, user ID, and phone number).
3. This information is forwarded to the **Owner**.
4. The Owner receives an interactive message with "Approve" and "Deny" buttons.
5. If approved, the user's ID is added to the authorized list, and they receive a notification.

## Persistence

The authorized user list is stored in a JSON file (default: `users.json`). The `UserManager` class handles:
- Loading the list on startup.
- Saving changes immediately when a user is added or removed.
- Ensuring the owner cannot be accidentally removed from the list.

## Admin Commands

The following commands are available only to the **Owner**:
- `/add_user <user_id>`: Manually authorize a user.
- `/remove_user <user_id>`: Revoke a user's access.
- `/list_users`: View all authorized user IDs.
