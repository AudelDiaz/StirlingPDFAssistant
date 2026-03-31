import logging
from functools import wraps
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from stirlingpdf_assistant.utils.user_manager import UserManager

logger = logging.getLogger(__name__)

def restricted(user_manager: UserManager):
    """Decorator to restrict access to authorized users only.
    Provides a 'Request Access' button to unauthorized users.
    """
    def decorator(func):
        @wraps(func)
        async def wrapped(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
            user_id = update.effective_user.id
            if not user_manager.is_authorized(user_id):
                logger.warning(f"Unauthorized access attempt by user {user_id} (@{update.effective_user.username})")
                
                keyboard = [[InlineKeyboardButton("📩 Request Access", callback_data=f"req_acc:{user_id}")]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                msg = "⛔ Access Denied. You are not authorized to use this bot."
                if update.message:
                    await update.message.reply_text(msg, reply_markup=reply_markup)
                elif update.callback_query:
                    await update.callback_query.answer(msg, show_alert=True)
                return
            return await func(update, context, *args, **kwargs)
        return wrapped
    return decorator

def owner_only(owner_id: int):
    """Decorator to restrict access to the bot owner only."""
    def decorator(func):
        @wraps(func)
        async def wrapped(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
            user_id = update.effective_user.id
            if user_id != owner_id:
                if update.message:
                    await update.message.reply_text("🚫 This command is reserved for the bot owner.")
                elif update.callback_query:
                    await update.callback_query.answer("🚫 Unauthorized access.", show_alert=True)
                return
            return await func(update, context, *args, **kwargs)
        return wrapped
    return decorator
