# Custom Telegram Bot API server image with UID 1000
#
# The official aiogram/telegram-bot-api image runs as UID 101.
# StirlingPDFAssistant runs as UID 1000.  When a shared volume is
# used for file transfers, UID mismatch causes Permission denied errors.
#
# This image changes the telegram-bot-api user/group from UID/GID 101
# to 1000 so that files written to the shared volume are readable by
# the bot container.
#
# Why UID 1000?
# - It's the default non-root UID on most Linux systems (Ubuntu, Debian,
#   Raspberry Pi OS, Docker Desktop on macOS/Windows).
# - It matches the appuser UID in the StirlingPDFAssistant container.
# - Avoiding UID 0 (root) reduces security risk.
#
# Usage in docker-compose.yml:
#   build: ./docker/telegram-bot-api
#   # instead of: image: aiogram/telegram-bot-api:latest

FROM aiogram/telegram-bot-api:10.1

# Change telegram-bot-api from UID/GID 101 → 1000 to match the bot
# container's appuser, so files in the shared volume are readable.
# Uses sed to edit /etc/passwd and /etc/group in-place, replacing
# all occurrences of ":101:" on the telegram-bot-api line with ":1000:".
RUN sed -i '/^telegram-bot-api:/s/:101:/:1000:/g' /etc/passwd /etc/group \
    && chown -R 1000:1000 \
        /var/lib/telegram-bot-api \
        /tmp/telegram-bot-api
