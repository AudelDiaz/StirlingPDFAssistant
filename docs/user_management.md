# User Management and Access Control

The bot uses a whitelist to control who can send commands. Unauthorized users are prompted to request access from the owner.

## How It Works

Every incoming message goes through the `restricted` decorator in `decorators.py`. It checks the user's Telegram ID against a list of authorized IDs stored in a JSON file.

### The Owner

`BOT_OWNER_ID` is set in the environment. The owner:

- Is always authorized.
- Can add and remove users via commands.
- Receives access requests from new users.

### Access Request Flow

1. An unauthorized user sends `/start`.
2. They see a button to share their contact info.
3. The request (name, user ID, phone number) is forwarded to the owner.
4. The owner sees an inline message with Approve and Deny buttons.
5. If approved, the user's ID is added to the whitelist and they get a confirmation.

## Persistence

The authorized user list is stored in `users.json` (configurable via `USERS_FILE`). The `UserManager` class:

- Loads the list on startup.
- Saves changes immediately when users are added or removed.
- Prevents the owner from being removed.

## Admin Commands

Only available to the owner:

- `/add_user <id>` — manually authorize a user.
- `/remove_user <id>` — revoke a user's access.
- `/list_users` — show all authorized user IDs.
