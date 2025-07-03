#!/usr/bin/env python3
"""
بوت تحميل الفيديوهات - نسخة بسيطة ومضمونة
"""
import os
import logging
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes
from telegram.error import TelegramError

# إعدادات البوت
BOT_TOKEN = os.getenv("BOT_TOKEN", "7825917266:AAHGvEXje3qQ2LXQ6_T9Sg49BFRlgNQwReE")
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME", "@YOUR_CHANNEL")
ADMIN_USER_ID = int(os.getenv("ADMIN_USER_ID", "606898749"))

# إعداد السجلات
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleBot:
    def __init__(self):
        self.app = Application.builder().token(BOT_TOKEN).build()
        self.setup_handlers()
    
    def setup_handlers(self):
        """إعداد المعالجات"""
        self.app.add_handler(CommandHandler("start", self.start))
        self.app.add_handler(CallbackQueryHandler(self.button_handler))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """أمر البداية"""
        keyboard = [
            [InlineKeyboardButton("📢 اشترك في القناة", url=f"https://t.me/{CHANNEL_USERNAME.replace('@', '')}")],
            [InlineKeyboardButton("✅ تحقق من الاشتراك", callback_data="check")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message = """🎬 مرحباً بك في بوت تحميل الفيديوهات!

📹 يمكنني تحميل الفيديوهات من:
• يوتيوب • فيسبوك • تيك توك • انستجرام

🎵 يمكنني تحويل الفيديوهات إلى صوت

📢 للاستخدام يجب الاشتراك في القناة أولاً!"""
        
        await update.message.reply_text(message, reply_markup=reply_markup)
    
    async def is_subscribed(self, user_id: int, context: ContextTypes.DEFAULT_TYPE):
        """التحقق من الاشتراك"""
        try:
            member = await context.bot.get_chat_member(CHANNEL_USERNAME, user_id)
            return member.status in ['member', 'administrator', 'creator']
        except TelegramError:
            return False
    
    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج الأزرار"""
        query = update.callback_query
        await query.answer()
        
        if query.data == "check":
            user_id = update.effective_user.id
            
            if await self.is_subscribed(user_id, context):
                await query.edit_message_text("✅ ممتاز! الآن أرسل رابط الفيديو الذي تريد تحميله")
            else:
                keyboard = [
                    [InlineKeyboardButton("📢 اشترك في القناة", url=f"https://t.me/{CHANNEL_USERNAME.replace('@', '')}")],
                    [InlineKeyboardButton("✅ تحقق من الاشتراك", callback_data="check")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.edit_message_text(
                    f"❌ لم تشترك في القناة بعد!\n\n📢 يجب الاشتراك في {CHANNEL_USERNAME} للاستخدام",
                    reply_markup=reply_markup
                )
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج الرسائل"""
        user_id = update.effective_user.id
        text = update.message.text
        
        # التحقق من الاشتراك
        if not await self.is_subscribed(user_id, context):
            keyboard = [
                [InlineKeyboardButton("📢 اشترك في القناة", url=f"https://t.me/{CHANNEL_USERNAME.replace('@', '')}")],
                [InlineKeyboardButton("✅ تحقق من الاشتراك", callback_data="check")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                f"❌ لم تشترك في القناة بعد!\n\n📢 يجب الاشتراك في {CHANNEL_USERNAME} للاستخدام",
                reply_markup=reply_markup
            )
            return
        
        # التحقق من صحة الرابط
        if not self.is_url(text):
            await update.message.reply_text("❌ يرجى إرسال رابط صحيح")
            return
        
        # تحميل الفيديو
        await self.download_video(update, context, text)
    
    def is_url(self, text):
        """التحقق من صحة الرابط"""
        return text.startswith(('http://', 'https://'))
    
    async def download_video(self, update: Update, context: ContextTypes.DEFAULT_TYPE, url: str):
        """تحميل الفيديو"""
        try:
            # إرسال رسالة التحميل
            status_message = await update.message.reply_text("⏳ جاري تحميل الفيديو...")
            
            # إعدادات التحميل
            ydl_opts = {
                'format': 'best[height<=720]',
                'outtmpl': 'video.%(ext)s',
                'noplaylist': True,
            }
            
            # تحميل الفيديو
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
            
            # إرسال الفيديو
            await status_message.edit_text("📤 جاري إرسال الفيديو...")
            
            with open(filename, 'rb') as video_file:
                await context.bot.send_video(
                    chat_id=update.effective_chat.id,
                    video=video_file,
                    caption=f"🎬 {info.get('title', 'فيديو')}",
                    reply_to_message_id=update.message.message_id
                )
            
            # حذف الملف
            os.remove(filename)
            await status_message.delete()
            
        except Exception as e:
            logger.error(f"خطأ في التحميل: {e}")
            await update.message.reply_text("❌ حدث خطأ في التحميل. تأكد من صحة الرابط")
    
    def run(self):
        """تشغيل البوت"""
        logger.info("بدء تشغيل البوت...")
        self.app.run_polling()

if __name__ == "__main__":
    bot = SimpleBot()
    bot.run()