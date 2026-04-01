import logging
import asyncio
from typing import List, Dict, Tuple
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import ContextTypes
from stirlingpdf_assistant.api.client import StirlingPDFClient
from stirlingpdf_assistant.api.tools import (
    CompressPDFTool, OCRPDFTool, AddPasswordTool, MergePDFsTool, 
    ImagesToPDFTool, PdfToWordTool, ScannerEffectTool, 
    SplitPDFTool, AutoRedactTool, URLToPDFTool
)
import re
from stirlingpdf_assistant.utils.user_manager import UserManager
from stirlingpdf_assistant.utils.i18n import get_text

logger = logging.getLogger(__name__)

class BotHandlers:
    def __init__(self, 
                 stirling_client: StirlingPDFClient, 
                 user_manager: UserManager, 
                 owner_id: int,
                 max_concurrent_tasks: int = 2,
                 max_file_size_mb: int = 20):
        self.stirling_client = stirling_client
        self.user_manager = user_manager
        self.owner_id = owner_id
        
        # Load persistent setting or fallback to provided value (from .env)
        self.max_file_size_mb = self.user_manager.get_setting("max_file_size_mb", max_file_size_mb)
        
        # Concurrency Safeguard
        self.semaphore = asyncio.Semaphore(max_concurrent_tasks)
        
        # Pre-instantiate tools
        self.compress_tool = CompressPDFTool()
        self.ocr_tool = OCRPDFTool()
        self.password_tool = AddPasswordTool()
        self.merge_tool = MergePDFsTool()
        self.images_to_pdf_tool = ImagesToPDFTool()
        self.to_word_tool = PdfToWordTool()
        self.scanner_tool = ScannerEffectTool()
        self.split_tool = SplitPDFTool()
        self.redact_tool = AutoRedactTool()
        self.url_tool = URLToPDFTool()

    def _t(self, update: Update, key: str, **kwargs) -> str:
        """Helper to get translated text based on user language."""
        lang = update.effective_user.language_code if update.effective_user else "en"
        return get_text(lang, key, **kwargs)

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        greeting = self._t(update, "start_greeting", name=update.effective_user.first_name)
        await update.message.reply_text(greeting)

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        help_text = (
            f"{self._t(update, 'help_title')}\n\n"
            f"{self._t(update, 'help_usage')}\n\n"
            f"{self._t(update, 'help_core')}\n\n"
            f"{self._t(update, 'help_advanced')}\n\n"
        )
        
        # Only show system limits to the owner
        if update.effective_user.id == self.owner_id:
            help_text += f"{self._t(update, 'help_system', max_size=self.max_file_size_mb)}\n\n"
            
        help_text += self._t(update, 'help_admin')
        await update.message.reply_text(help_text, parse_mode='Markdown')

    # --- Admin Handlers ---
    
    async def list_users_cmd(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        users = self.user_manager.allowed_ids
        users_list = "\n".join([f"- `{uid}`" + (" (Owner)" if uid == self.owner_id else "") for uid in users])
        title = self._t(update, "auth_list_title")
        await update.message.reply_text(f"{title}\n{users_list}", parse_mode='Markdown')

    async def add_user_cmd(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not context.args: return
        try:
            new_id = int(context.args[0])
            if self.user_manager.add_user(new_id): 
                await update.message.reply_text(self._t(update, "auth_added", user_id=new_id))
        except: pass

    async def remove_user_cmd(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not context.args: return
        try:
            target_id = int(context.args[0])
            if self.user_manager.remove_user(target_id): 
                await update.message.reply_text(self._t(update, "auth_removed", user_id=target_id))
        except: pass

    async def set_limit_cmd(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not context.args:
            await update.message.reply_text(self._t(update, "admin_limit_usage"), parse_mode='Markdown')
            return
        try:
            new_limit = int(context.args[0])
            if new_limit < 1 or new_limit > 500:
                await update.message.reply_text(self._t(update, "admin_limit_range"))
                return
            
            self.max_file_size_mb = new_limit
            self.user_manager.set_setting("max_file_size_mb", new_limit)
            await update.message.reply_text(self._t(update, "admin_limit_success", new_limit=new_limit), parse_mode='Markdown')
        except:
            await update.message.reply_text(self._t(update, "admin_limit_invalid"))

    # --- Access Request ---

    async def request_access_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.callback_query.answer()
        keyboard = [[KeyboardButton(self._t(update, "req_access_button"), request_contact=True)]]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=self._t(update, "req_access_prompt"), reply_markup=reply_markup)

    async def handle_contact(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        c = update.message.contact
        # Monitor/Owner message might be better in the bot's default/owner language or Dual
        title = self._t(update, "req_access_title")
        msg = f"{title}\n👤 {c.first_name}\n🆔 `{c.user_id}`\n📱 {c.phone_number}"
        
        keyboard = [[
            InlineKeyboardButton(self._t(update, "req_approve"), callback_data=f"appr_acc:{c.user_id}"), 
            InlineKeyboardButton(self._t(update, "req_deny"), callback_data=f"deny_acc:{c.user_id}")
        ]]
        await context.bot.send_message(chat_id=self.owner_id, text=msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
        await update.message.reply_text(self._t(update, "req_access_sent"), reply_markup=ReplyKeyboardRemove())

    async def approve_access_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        target_id = int(query.data.split(":")[1])
        if self.user_manager.add_user(target_id):
            await query.edit_message_text(self._t(update, "req_approved_log", user_id=target_id))
            
            # Use English/Spanish based on some heuristic or just standard
            # Ideally we'd know the TARGET user's language, but since we don't store it, 
            # we can guess or use a dual-language welcome. For now we use standard i18n
            welcome_msg = self._t(update, "welcome_approved") 
            try: 
                await context.bot.send_message(chat_id=target_id, text=welcome_msg, parse_mode='Markdown')
            except: 
                pass

    async def deny_access_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.callback_query.answer("Denied.")
        tid = int(update.callback_query.data.split(":")[1])
        await update.callback_query.edit_message_text(self._t(update, "req_denied_log", user_id=tid))

    # --- Hybrid Merge Mode ---

    async def merge_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Initializes a merge session."""
        context.chat_data['merge_active'] = True
        context.chat_data['merge_queue'] = [] # List of (filename, file_content, mime_type)
        
        keyboard = [[
            InlineKeyboardButton(self._t(update, "merge_btn_finish"), callback_data='merge_finish'),
            InlineKeyboardButton(self._t(update, "merge_btn_cancel"), callback_data='merge_cancel')
        ]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"{self._t(update, 'merge_start_title')}\n\n{self._t(update, 'merge_start_desc')}",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    async def merge_finish_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        queue = context.chat_data.get('merge_queue', [])
        
        if not queue:
            await query.answer(self._t(update, "merge_empty"), show_alert=True)
            return

        await query.answer()
        await query.edit_message_text(text=self._t(update, "merge_processing", count=len(queue)))
        
        async with self.semaphore:
            try:
                final_pdf_list = []
                for i, (fname, content, mime) in enumerate(queue):
                    if len(queue) > 2:
                        await query.edit_message_text(text=self._t(update, "merge_step", current=i+1, total=len(queue)))
                    
                    if mime.startswith('image/'):
                        pdf_page = await self.stirling_client.execute(
                            self.images_to_pdf_tool, 
                            file_contents=[content], 
                            filenames=[fname]
                        )
                        final_pdf_list.append(pdf_page)
                    else:
                        final_pdf_list.append(content)

                await query.edit_message_text(text=self._t(update, "merge_finalizing"))
                merged_result = await self.stirling_client.execute(self.merge_tool, file_contents=final_pdf_list)
                
                await query.edit_message_text(text=self._t(update, "merge_complete"))
                await context.bot.send_document(
                    chat_id=update.effective_chat.id, 
                    document=merged_result, 
                    filename="merged_document.pdf"
                )
                
                context.chat_data['merge_active'] = False
                context.chat_data['merge_queue'] = []
                
            except Exception as e:
                logger.error(f"Merge error: {e}")
                await context.bot.send_message(chat_id=update.effective_chat.id, text=self._t(update, "err_merge", error=str(e)))

    async def merge_cancel_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        context.chat_data['merge_active'] = False
        context.chat_data['merge_queue'] = []
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(self._t(update, "merge_cancelled"))

    # --- Universal Document/Photo Handlers ---

    async def handle_document(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        doc = update.message.document
        
        file_size_mb = doc.file_size / (1024 * 1024)
        if file_size_mb > self.max_file_size_mb:
            await update.message.reply_text(self._t(update, "msg_file_large", size=file_size_mb, max_size=self.max_file_size_mb))
            return

        if context.chat_data.get('merge_active'):
            tg_file = await context.bot.get_file(doc.file_id)
            content = bytes(await tg_file.download_as_bytearray())
            context.chat_data['merge_queue'].append((doc.file_name or "file.pdf", content, doc.mime_type))
            count = len(context.chat_data['merge_queue'])
            await update.message.reply_text(self._t(update, "msg_added_queue", count=count))
            return

        if doc.mime_type != 'application/pdf':
            await update.message.reply_text(self._t(update, "msg_send_pdf_hint"))
            return

        context.chat_data['current_file_id'] = doc.file_id
        context.chat_data['current_file_name'] = doc.file_name or "document.pdf"
        
        keyboard = [
            [InlineKeyboardButton(self._t(update, "btn_compress"), callback_data='action_compress'),
             InlineKeyboardButton(self._t(update, "btn_ocr"), callback_data='action_ocr')],
            [InlineKeyboardButton(self._t(update, "btn_password"), callback_data='action_password'),
             InlineKeyboardButton(self._t(update, "btn_to_word"), callback_data='action_to_word')],
            [InlineKeyboardButton(self._t(update, "btn_scanner"), callback_data='action_scanner'),
             InlineKeyboardButton(self._t(update, "btn_split"), callback_data='action_split')],
            [InlineKeyboardButton(self._t(update, "btn_redact"), callback_data='action_redact')]
        ]
        await update.message.reply_text(self._t(update, "msg_received_file", name=doc.file_name), reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

    async def handle_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        photo = update.message.photo[-1]
        
        if context.chat_data.get('merge_active'):
            tg_file = await context.bot.get_file(photo.file_id)
            content = bytes(await tg_file.download_as_bytearray())
            context.chat_data['merge_queue'].append(("image.jpg", content, "image/jpeg"))
            count = len(context.chat_data['merge_queue'])
            await update.message.reply_text(self._t(update, "msg_img_added_queue", count=count))
            return
        
        keyboard = [[InlineKeyboardButton(self._t(update, "btn_img_to_pdf"), callback_data='action_img_to_pdf')]]
        context.chat_data['current_file_id'] = photo.file_id
        context.chat_data['current_file_name'] = "converted.jpg"
        await update.message.reply_text(self._t(update, "msg_received_img"), reply_markup=InlineKeyboardMarkup(keyboard))

    async def handle_callback_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        action = query.data

        if action.startswith(('appr_acc', 'deny_acc', 'req_acc')): return
        if action == 'merge_finish': return await self.merge_finish_callback(update, context)
        if action == 'merge_cancel': return await self.merge_cancel_callback(update, context)

        await query.answer()
        fid = context.chat_data.get('current_file_id')
        fname = context.chat_data.get('current_file_name')

        if not fid:
            await query.edit_message_text(self._t(update, "err_session_expired"))
            return

        if action == 'action_password':
            context.chat_data['awaiting_password'] = True
            await query.edit_message_text(self._t(update, "action_password_prompt"))
            return
            
        if action == 'action_split':
            context.chat_data['awaiting_split'] = True
            await query.edit_message_text(self._t(update, "prompt_split_pages"))
            return

        if action == 'action_redact':
            context.chat_data['awaiting_redact'] = True
            await query.edit_message_text(self._t(update, "prompt_redact_text"))
            return

        await query.edit_message_text(text=self._t(update, "action_processing"))
        async with self.semaphore:
            try:
                tg_file = await context.bot.get_file(fid)
                content = bytes(await tg_file.download_as_bytearray())
                
                if action == 'action_compress':
                    res = await self.stirling_client.execute(self.compress_tool, file_content=content, filename=fname)
                    out = f"compressed_{fname}"
                elif action == 'action_ocr':
                    res = await self.stirling_client.execute(self.ocr_tool, file_content=content, filename=fname)
                    out = f"ocr_{fname}"
                elif action == 'action_img_to_pdf':
                    res = await self.stirling_client.execute(self.images_to_pdf_tool, file_contents=[content], filenames=[fname])
                    out = fname.replace(".jpg", ".pdf").replace(".png", ".pdf").replace("converted", "document")
                    if not out.endswith(".pdf"): out += ".pdf"
                elif action == 'action_to_word':
                    res = await self.stirling_client.execute(self.to_word_tool, file_content=content, filename=fname)
                    out = fname.rsplit('.', 1)[0] + ".docx"
                elif action == 'action_scanner':
                    await query.edit_message_text(text=self._t(update, "action_scanning"))
                    res = await self.stirling_client.execute(self.scanner_tool, file_content=content, filename=fname)
                    out = f"scanned_{fname}"
                else: return

                await query.edit_message_text(self._t(update, "action_complete"))
                await context.bot.send_document(chat_id=update.effective_chat.id, document=res, filename=out)
            except Exception as e:
                await context.bot.send_message(chat_id=update.effective_chat.id, text=self._t(update, "err_generic", error=str(e)))

    async def handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = update.message.text
        chat_data = context.chat_data
        
        # 1. Check for URL input (Auto-convert to PDF)
        url_match = re.search(r'(https?://\S+)', text)
        if url_match and not any([chat_data.get('awaiting_password'), chat_data.get('awaiting_split'), chat_data.get('awaiting_redact')]):
            url = url_match.group(1)
            status = await update.message.reply_text(self._t(update, "action_converting_url"))
            async with self.semaphore:
                try:
                    res = await self.stirling_client.execute(self.url_tool, url=url)
                    await status.delete()
                    await context.bot.send_document(chat_id=update.effective_chat.id, document=res, filename="webpage.pdf")
                except Exception as e:
                    await status.edit_text(self._t(update, "err_generic", error=str(e)))
            return

        # 2. State-based Input Handling
        if chat_data.get('awaiting_password'):
            await self._process_tool_with_input(update, context, self.password_tool, "awaiting_password", "action_encrypting", "protected_", password=text)
        elif chat_data.get('awaiting_split'):
            await self._process_tool_with_input(update, context, self.split_tool, "awaiting_split", "action_splitting", "split_", page_numbers=text)
        elif chat_data.get('awaiting_redact'):
            await self._process_tool_with_input(update, context, self.redact_tool, "awaiting_redact", "action_redacting", "redacted_", keywords=text)

    async def _process_tool_with_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE, tool, state_key: str, status_key: str, prefix: str, **kwargs):
        """Generic helper for tools requiring text input."""
        context.chat_data[state_key] = False
        fid = context.chat_data.get('current_file_id')
        fname = context.chat_data.get('current_file_name')
        
        if not fid:
            await update.message.reply_text(self._t(update, "err_session_expired"))
            return

        status = await update.message.reply_text(self._t(update, "action_processing"))
        await status.edit_text(self._t(update, status_key))
        
        async with self.semaphore:
            try:
                tg_file = await context.bot.get_file(fid)
                content = bytes(await tg_file.download_as_bytearray())
                res = await self.stirling_client.execute(tool, file_content=content, filename=fname, **kwargs)
                await status.edit_text(self._t(update, "action_complete"))
                await context.bot.send_document(chat_id=update.effective_chat.id, document=res, filename=f"{prefix}{fname}")
            except Exception as e:
                await status.edit_text(self._t(update, "err_generic", error=str(e)))
