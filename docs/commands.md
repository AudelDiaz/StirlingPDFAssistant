# Bot Commands & Features

The Stirling PDF Assistant provides several commands and interactive features for managing your documents.

## Public Commands

These commands are available to all authorized users.

-   **/start**: Displays a welcome message and initializes the bot interaction.
-   **/help**: Shows a comprehensive guide of all features and system limits.
-   **/merge**: Enters **Merge Mode**.
    -   In this mode, any PDFs or images you send are queued.
    -   You can click "Finish Merge" to combine all queued files into a single PDF.
    -   Images sent during this mode are automatically converted to PDF pages.

## Document Handling

When you send a **PDF** to the bot (outside of Merge Mode), it responds with an interactive menu:

-   **Compress**: Reduces the file size (useful for email attachments).
-   **OCR**: Makes the PDF searchable (Optical Character Recognition).
-   **Add Password**: Prompts you for a password and encrypts the document.
-   **To Word**: Converts the PDF into an editable `.docx` file.
-   **Scanner Effect**: Makes the digital PDF look like a physical scan.

## Photo Handling

When you send a **Photo** to the bot:
-   It offers an "Image to PDF" action.
-   Converting a single photo results in a one-page PDF.

## Admin Commands (Owner Only)

-   **/list_users**: Shows all authorized user IDs.
-   **/add_user <id>**: Adds a user to the whitelist.
-   **/remove_user <id>**: Removes a user from the whitelist.

## System Limits

To ensure stability, the following limits are enforced (configurable via `.env`):
-   **Max File Size**: Default 20MB.
-   **Concurrent Tasks**: Default 2 tasks. If multiple users are processing files, others will wait until a slot is free.
