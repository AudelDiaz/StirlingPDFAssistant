import os
import logging
import asyncio
from dotenv import load_dotenv
from telegram import Update, BotCommand, BotCommandScopeChat
from telegram.ext import (
    ApplicationBuilder, 
    CommandHandler, 
    MessageHandler, 
    CallbackQueryHandler, 
    filters
)

from stirlingpdf_assistant.api.client import StirlingPDFClient
from stirlingpdf_assistant.utils.user_manager import UserManager
from stirlingpdf_assistant.bot.handlers import BotHandlers
from stirlingpdf_assistant.bot.decorators import restricted, owner_only
from stirlingpdf_assistant.utils.i18n import TRANSLATIONS

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def post_init(application):
    """Set bot commands for multiple languages."""
    # English commands (Default)
    en_commands = [
        BotCommand("start", "Start the bot"),
        BotCommand("merge", "Enter Merge Mode (Combine files)"),
        BotCommand("help", "Show feature guide")
    ]
    await application.bot.set_my_commands(en_commands)
    
    # Spanish commands
    es_commands = [
        BotCommand("start", "Iniciar el bot"),
        BotCommand("merge", "Modo Unión (Combinar archivos)"),
        BotCommand("help", "Ver guía de funciones")
    ]
    await application.bot.set_my_commands(es_commands, language_code='es')
    
    # --- Owner-Specific Commands (Private Admin Menu) ---
    owner_id = int(os.getenv("BOT_OWNER_ID", "0"))
    if owner_id:
        admin_commands = [
            BotCommand("start", "Start the bot"),
            BotCommand("merge", "Enter Merge Mode"),
            BotCommand("help", "Show feature guide"),
            BotCommand("list_users", "📋 [Admin] Show authorized IDs"),
            BotCommand("add_user", "👤 [Admin] Authorize a user ID"),
            BotCommand("remove_user", "❌ [Admin] Revoke access ID"),
            BotCommand("set_limit", "📈 [Admin] Set Max File Size (MB)")
        ]
        try:
            await application.bot.set_my_commands(
                admin_commands, 
                scope=BotCommandScopeChat(chat_id=owner_id)
            )
            logger.info(f"Private Admin Menu set for owner ID: {owner_id}")
        except Exception as e:
            logger.warning(f"Could not set admin commands: {e}")
            
    logger.info("Bot commands set for English and Spanish.")

def main():
    # Load configuration
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    stirling_url = os.getenv("STIRLING_PDF_URL", "http://127.0.0.1:8080")
    stirling_key = os.getenv("STIRLING_PDF_API_KEY")
    owner_id = int(os.getenv("BOT_OWNER_ID", "0"))
    users_file = os.getenv("USERS_FILE", "users.json")
    
    # Load Safeguards
    max_tasks = int(os.getenv("MAX_CONCURRENT_TASKS", "2"))
    max_size_mb = int(os.getenv("MAX_FILE_SIZE_MB", "20"))

    if not token:
        logger.error("TELEGRAM_BOT_TOKEN not found in environment.")
        return

    # Initialize components
    stirling_client = StirlingPDFClient(stirling_url, stirling_key)
    user_manager = UserManager(users_file, owner_id)
    
    # Initialize handlers
    h = BotHandlers(
        stirling_client=stirling_client, 
        user_manager=user_manager, 
        owner_id=owner_id,
        max_concurrent_tasks=max_tasks,
        max_file_size_mb=max_size_mb
    )

    # Build application
    application = ApplicationBuilder().token(token).post_init(post_init).build()

    # --- Register Handlers ---

    # Access Request & Approval
    application.add_handler(CallbackQueryHandler(h.request_access_callback, pattern="^req_acc:"))
    application.add_handler(CallbackQueryHandler(h.approve_access_callback, pattern="^appr_acc:"))
    application.add_handler(CallbackQueryHandler(h.deny_access_callback, pattern="^deny_acc:"))
    application.add_handler(MessageHandler(filters.CONTACT, h.handle_contact))

    # Commands
    application.add_handler(CommandHandler("start", restricted(user_manager)(h.start)))
    application.add_handler(CommandHandler("help", restricted(user_manager)(h.help_command)))
    application.add_handler(CommandHandler("merge", restricted(user_manager)(h.merge_command)))
    
    # Admin commands (Owner Only)
    application.add_handler(CommandHandler("add_user", owner_only(owner_id)(h.add_user_cmd)))
    application.add_handler(CommandHandler("remove_user", owner_only(owner_id)(h.remove_user_cmd)))
    application.add_handler(CommandHandler("list_users", owner_only(owner_id)(h.list_users_cmd)))
    application.add_handler(CommandHandler("set_limit", owner_only(owner_id)(h.set_limit_cmd)))
    
    # Document, Photo, and interaction handlers
    application.add_handler(MessageHandler(filters.Document.ALL, restricted(user_manager)(h.handle_document)))
    application.add_handler(MessageHandler(filters.PHOTO, restricted(user_manager)(h.handle_photo)))
    application.add_handler(CallbackQueryHandler(restricted(user_manager)(h.handle_callback_query)))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), restricted(user_manager)(h.handle_text)))

    logger.info(f"Stirling PDF Assistant starting (Tasks: {max_tasks}, Max Size: {max_size_mb}MB)...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
