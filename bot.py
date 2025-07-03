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
        self.app.add_handler(CommandHandler("test", self.test_command))
        self.app.add_handler(CommandHandler("bypass", self.bypass_command))
        self.app.add_handler(CommandHandler("testdownload", self.test_download_command))
        self.app.add_handler(CallbackQueryHandler(self.button_handler))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """أمر البداية"""
        # إذا كان معرف القناة لم يتم تغييره
        if CHANNEL_USERNAME == "@YOUR_CHANNEL":
            message = """🎬 مرحباً بك في بوت تحميل الفيديوهات!

📹 يمكنني تحميل الفيديوهات من:
• يوتيوب • فيسبوك • تيك توك • انستجرام

🎵 يمكنني تحويل الفيديوهات إلى صوت

✅ البوت يعمل في وضع التجربة - أرسل رابط الفيديو مباشرة!

⚠️ ملاحظة للمطور: يجب تغيير معرف القناة في إعدادات البوت."""
            
            await update.message.reply_text(message)
        else:
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
    
    async def test_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """أمر اختبار للمشرف"""
        user_id = update.effective_user.id
        
        if user_id != ADMIN_USER_ID:
            await update.message.reply_text("❌ هذا الأمر للمشرف فقط")
            return
        
        # اختبار التحقق من الاشتراك
        subscription_status = "⏳ جاري الفحص..."
        try:
            if CHANNEL_USERNAME == "@YOUR_CHANNEL":
                subscription_status = "✅ وضع التجربة - لا يوجد تحقق من الاشتراك"
            else:
                is_sub = await self.is_subscribed(user_id, context)
                subscription_status = f"{'✅ مشترك' if is_sub else '❌ غير مشترك'}"
                
                # اختبار إضافي للبوت في القناة
                try:
                    bot_member = await context.bot.get_chat_member(CHANNEL_USERNAME, context.bot.id)
                    bot_status = f"🤖 البوت في القناة: ✅ {bot_member.status}"
                    if bot_member.status not in ['administrator']:
                        bot_status += " ⚠️ (يجب أن يكون مشرف)"
                except Exception as e:
                    bot_status = f"🤖 البوت في القناة: ❌ خطأ - {e}"
        except Exception as e:
            subscription_status = f"❌ خطأ في الفحص: {e}"
            bot_status = "❌ لا يمكن فحص حالة البوت"
        
        message = f"""🧪 اختبار البوت:

👤 معرف المستخدم: {user_id}
🔧 معرف القناة: {CHANNEL_USERNAME}
👑 معرف المشرف: {ADMIN_USER_ID}

📊 حالة الاشتراك: {subscription_status}
{bot_status if 'bot_status' in locals() else ''}

💡 إذا كان البوت لا يعمل، تأكد من:
1. البوت مشرف في القناة {CHANNEL_USERNAME}
2. البوت له صلاحية "قراءة الأعضاء"
3. القناة عامة وليست خاصة
4. معرف القناة صحيح"""
        
        await update.message.reply_text(message)
    
    async def bypass_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """أمر تجاوز مشكلة الاشتراك للمشرف"""
        user_id = update.effective_user.id
        
        if user_id != ADMIN_USER_ID:
            await update.message.reply_text("❌ هذا الأمر للمشرف فقط")
            return
        
        message = f"""🔧 إصلاح مشكلة الاشتراك:

📋 **المشكلة**: البوت يقول "لم تشترك في القناة" رغم الاشتراك

🛠️ **الحلول الفورية**:

**الحل الأول** (الأسرع):
في Railway، غير المتغير إلى:
```
CHANNEL_USERNAME=@YOUR_CHANNEL
```
سيعمل البوت بدون اشتراك إجباري.

**الحل الثاني** (لإصلاح القناة):
1. تأكد أن البوت مشرف في @{CHANNEL_USERNAME.replace('@', '')}
2. أعط البوت صلاحية "قراءة الأعضاء"
3. تأكد أن القناة عامة
4. أعد تشغيل البوت في Railway

**الحل الثالث** (للطوارئ):
أرسل أي رابط فيديو هنا وسأحمله لك مباشرة بدون تحقق من الاشتراك."""
        
        await update.message.reply_text(message)
    
    async def test_download_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """اختبار التحميل مع رابط تجريبي"""
        user_id = update.effective_user.id
        
        if user_id != ADMIN_USER_ID:
            await update.message.reply_text("❌ هذا الأمر للمشرف فقط")
            return
        
        # رابط تجريبي قصير
        test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        
        await update.message.reply_text("🧪 جاري اختبار التحميل بفيديو تجريبي...")
        await self.download_video(update, context, test_url)
    
    async def is_subscribed(self, user_id: int, context: ContextTypes.DEFAULT_TYPE):
        """التحقق من الاشتراك"""
        try:
            # إذا كان معرف القناة لم يتم تغييره، اسمح بالوصول
            if CHANNEL_USERNAME == "@YOUR_CHANNEL":
                return True
            
            # إذا كان المستخدم هو المشرف، اسمح بالوصول
            if user_id == ADMIN_USER_ID:
                return True
            
            member = await context.bot.get_chat_member(CHANNEL_USERNAME, user_id)
            status = member.status
            logger.info(f"حالة المستخدم {user_id} في القناة {CHANNEL_USERNAME}: {status}")
            
            return status in ['member', 'administrator', 'creator']
            
        except TelegramError as e:
            error_message = str(e).lower()
            logger.error(f"خطأ في التحقق من الاشتراك للمستخدم {user_id} في القناة {CHANNEL_USERNAME}: {e}")
            
            # أخطاء شائعة ومعالجتها
            if "chat not found" in error_message:
                logger.error("القناة غير موجودة أو معرف القناة خاطئ")
                return True  # اسمح بالوصول إذا كانت القناة غير موجودة
            elif "bot is not a member" in error_message or "forbidden" in error_message:
                logger.error("البوت ليس عضو في القناة أو لا يملك الصلاحيات")
                return True  # اسمح بالوصول إذا كان البوت غير مشرف
            elif "user not found" in error_message:
                logger.error("المستخدم غير موجود")
                return False
            else:
                logger.error(f"خطأ غير معروف: {e}")
                return True  # في حالة أي خطأ آخر، اسمح بالوصول
    
    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالج الأزرار"""
        query = update.callback_query
        await query.answer()
        
        if query.data == "check":
            user_id = update.effective_user.id
            
            # إذا كان معرف القناة لم يتم تغييره
            if CHANNEL_USERNAME == "@YOUR_CHANNEL":
                await query.edit_message_text(
                    "⚠️ مرحباً! البوت يعمل في وضع التجربة.\n\n"
                    "✅ يمكنك استخدام البوت الآن وإرسال رابط الفيديو.\n\n"
                    "📝 ملاحظة: يجب على المطور تغيير معرف القناة في إعدادات البوت."
                )
                return
            
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
        
        # للمشرف: تجاهل التحقق من الاشتراك واعرض رسالة خاصة
        if user_id == ADMIN_USER_ID and CHANNEL_USERNAME != "@YOUR_CHANNEL":
            await update.message.reply_text(
                f"👑 مرحباً أيها المشرف!\n\n"
                f"💡 إذا كان البوت يقول للمستخدمين أنهم غير مشتركين في {CHANNEL_USERNAME}، "
                f"استخدم الأمر /bypass لمعرفة الحلول.\n\n"
                f"🎬 الآن سأحمل لك الفيديو..."
            )
        # التحقق من الاشتراك للمستخدمين العاديين (إلا إذا كان معرف القناة لم يتم تغييره)
        elif CHANNEL_USERNAME != "@YOUR_CHANNEL" and not await self.is_subscribed(user_id, context):
            keyboard = [
                [InlineKeyboardButton("📢 اشترك في القناة", url=f"https://t.me/{CHANNEL_USERNAME.replace('@', '')}")],
                [InlineKeyboardButton("✅ تحقق من الاشتراك", callback_data="check")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                f"❌ لم تشترك في القناة بعد!\n\n📢 يجب الاشتراك في {CHANNEL_USERNAME} للاستخدام\n\n"
                f"💡 إذا كنت مشترك ولا يزال البوت يعرض هذه الرسالة، تواصل مع المطور.",
                reply_markup=reply_markup
            )
            return
        
        # التحقق من صحة الرابط
        if not self.is_url(text):
            if text.startswith(('http://', 'https://')):
                await update.message.reply_text(
                    "❌ هذا الموقع غير مدعوم.\n\n"
                    "📹 المواقع المدعومة:\n"
                    "• YouTube\n• Facebook\n• Instagram\n• TikTok\n• Twitter\n• Vimeo"
                )
            else:
                await update.message.reply_text("❌ يرجى إرسال رابط صحيح يبدأ بـ http أو https")
            return
        
        # تحميل الفيديو
        await self.download_video(update, context, text)
    
    def is_url(self, text):
        """التحقق من صحة الرابط"""
        if not text.startswith(('http://', 'https://')):
            return False
        
        # قائمة المواقع المدعومة
        supported_sites = [
            'youtube.com', 'youtu.be', 'youtube.co.uk',
            'facebook.com', 'fb.watch', 'fb.com',
            'instagram.com', 'instagr.am',
            'tiktok.com', 'vm.tiktok.com',
            'twitter.com', 'x.com', 't.co',
            'vimeo.com', 'dailymotion.com',
            'twitch.tv', 'streamable.com'
        ]
        
        return any(site in text.lower() for site in supported_sites)
    
    async def download_video(self, update: Update, context: ContextTypes.DEFAULT_TYPE, url: str):
        """تحميل الفيديو"""
        status_message = None
        filename = None
        
        try:
            # إرسال رسالة التحميل
            status_message = await update.message.reply_text("⏳ جاري تحليل الرابط...")
            
            # إعدادات التحميل المحسنة
            ydl_opts = {
                'format': 'best[height<=480]/best[height<=720]/best[filesize<=50M]/best',
                'outtmpl': f'downloads/%(title).60s.%(ext)s',  # حد أقصى 60 حرف للعنوان
                'noplaylist': True,
                'no_warnings': True,
                'extractaudio': False,
                'ignoreerrors': False,
                'retries': 3,
                'fragment_retries': 3,
                'http_chunk_size': 10485760,  # 10MB chunks
                'socket_timeout': 30,
                'prefer_ffmpeg': True,
                'keepvideo': False,
                'writesubtitles': False,
                'writeautomaticsub': False,
                'subtitleslangs': [],
                'postprocessors': [{
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': 'mp4',
                }],
            }
            
            # إنشاء مجلد التحميل
            os.makedirs('downloads', exist_ok=True)
            
            logger.info(f"بدء تحميل الفيديو من: {url}")
            
            # تحميل الفيديو
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # استخراج المعلومات أولاً
                await status_message.edit_text("📊 جاري استخراج معلومات الفيديو...")
                info = ydl.extract_info(url, download=False)
                
                # التحقق من حجم الفيديو
                if info.get('filesize') and info['filesize'] > 50 * 1024 * 1024:  # 50MB
                    await status_message.edit_text("⚠️ الفيديو كبير جداً. جاري تحميل نسخة مضغوطة...")
                    ydl_opts['format'] = 'worst[height<=360]/worst'
                
                # تحميل الفيديو
                await status_message.edit_text("⬇️ جاري تحميل الفيديو...")
                ydl.download([url])
                
                # العثور على الملف المحمل
                filename = ydl.prepare_filename(info)
                
                # البحث عن الملف في المجلد إذا لم يوجد
                if not os.path.exists(filename):
                    downloads_dir = 'downloads'
                    if os.path.exists(downloads_dir):
                        files = os.listdir(downloads_dir)
                        if files:
                            filename = os.path.join(downloads_dir, files[0])
                
                if not os.path.exists(filename):
                    raise FileNotFoundError("لم يتم العثور على الملف المحمل")
            
            # التحقق من حجم الملف
            file_size = os.path.getsize(filename)
            if file_size > 50 * 1024 * 1024:  # 50MB
                await status_message.edit_text("❌ الفيديو كبير جداً للإرسال (أكثر من 50MB)")
                return
            
            # إرسال الفيديو
            await status_message.edit_text("📤 جاري إرسال الفيديو...")
            
            with open(filename, 'rb') as video_file:
                await context.bot.send_video(
                    chat_id=update.effective_chat.id,
                    video=video_file,
                    caption=f"🎬 {info.get('title', 'فيديو')}\n💾 الحجم: {file_size / (1024*1024):.1f} MB",
                    reply_to_message_id=update.message.message_id,
                    supports_streaming=True
                )
            
            await status_message.edit_text("✅ تم إرسال الفيديو بنجاح!")
            
        except yt_dlp.utils.DownloadError as e:
            error_msg = str(e)
            logger.error(f"خطأ في التحميل: {error_msg}")
            
            if status_message:
                if "not available" in error_msg.lower():
                    await status_message.edit_text("❌ الفيديو غير متاح أو محذوف")
                elif "private" in error_msg.lower():
                    await status_message.edit_text("❌ الفيديو خاص ولا يمكن تحميله")
                elif "geo" in error_msg.lower():
                    await status_message.edit_text("❌ الفيديو محجوب جغرافياً")
                else:
                    await status_message.edit_text(f"❌ خطأ في التحميل: رابط غير صالح أو فيديو محمي")
            
        except FileNotFoundError:
            logger.error("لم يتم العثور على الملف المحمل")
            if status_message:
                await status_message.edit_text("❌ فشل في تحميل الفيديو. جرب رابط آخر")
            
        except Exception as e:
            logger.error(f"خطأ غير متوقع في التحميل: {e}")
            if status_message:
                await status_message.edit_text(f"❌ خطأ في التحميل: {str(e)[:100]}...")
            
        finally:
            # تنظيف الملفات
            try:
                if filename and os.path.exists(filename):
                    os.remove(filename)
                    logger.info(f"تم حذف الملف: {filename}")
                
                # تنظيف مجلد التحميل
                if os.path.exists('downloads'):
                    for file in os.listdir('downloads'):
                        file_path = os.path.join('downloads', file)
                        if os.path.isfile(file_path):
                            os.remove(file_path)
                            
            except Exception as cleanup_error:
                logger.error(f"خطأ في تنظيف الملفات: {cleanup_error}")
    
    def run(self):
        """تشغيل البوت"""
        logger.info("بدء تشغيل البوت...")
        self.app.run_polling()

if __name__ == "__main__":
    bot = SimpleBot()
    bot.run()
