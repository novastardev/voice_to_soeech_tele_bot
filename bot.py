import io
import logging
import io
import logging
import os, threading
from http.server import HTTPServer, BaseHTTPRequestHandler

def run():
    HTTPServer(("0.0.0.0", int(os.environ.get("PORT", 8080))), BaseHTTPRequestHandler).serve_forever()

threading.Thread(target=run, daemon=True).start()
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

from config import (
    TELEGRAM_BOT_TOKEN,
    ALLOWED_CHAT_IDS,
    BOT_OWNER_HANDLE,
)

from database import (
    init_db,
    add_user,
    get_voice,
    set_voice,
    save_to_library,
    get_library,
    get_library_item,
    delete_from_library,
)

from tts import (
    get_voices,
    generate_speech,
)


# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)


# ============================================================
# ACCESS CONTROL
# ============================================================

def is_chat_allowed(user_id):
    """Check if user's chat ID is in the whitelist."""
    return user_id in ALLOWED_CHAT_IDS


# ============================================================
# USER STATE
# ============================================================

# Users who clicked Text to Speech and are expected
# to send text.
waiting_for_text = set()

# Store pending audio data for saving to library
# Format: {user_id: {"text": str, "voice": str, "message_id": int}}
pending_saves = {}


# ============================================================
# /START
# ============================================================

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    try:
        user_id = update.effective_user.id

        # Check if user is allowed
        if not is_chat_allowed(user_id):
            await update.message.reply_text(
                f"❌ Access Denied\n\n"
                f"Please ask {BOT_OWNER_HANDLE} to grant you access to this bot."
            )
            logger.warning(
                "Unauthorized access attempt from user %s",
                user_id,
            )
            return

        add_user(user_id)

        keyboard = [
            [
                InlineKeyboardButton(
                    "🎙️ Text to Speech",
                    callback_data="tts",
                )
            ],
            [
                InlineKeyboardButton(
                    "⚙️ Settings",
                    callback_data="settings",
                )
            ],
            [
                InlineKeyboardButton(
                    "📚 My Library",
                    callback_data="library_view",
                )
            ],
        ]

        await update.message.reply_text(
            "🔊 *Text to Speech Bot*\n\n"
            "Convert your text into natural speech with multiple voices.\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "*Built by Novastar* 👨‍💻\n\n"
            "A passionate IT developer creating awesome tools.\n"
            "Currently focused on building intelligent Telegram bots and innovative solutions.\n\n"
            "*Get in touch:*\n"
            "• Telegram: @novastar\n"
            "• Portfolio: novastar-dev.vercel.app\n\n"
            "Feel free to reach out for collaborations, questions, or just to say hi! 😁\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown",
        )

    except Exception:
        logger.exception("START ERROR")

        await update.message.reply_text(
            "❌ Something went wrong."
        )


# ============================================================
# /SETTINGS
# ============================================================

async def settings(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    try:
        user_id = update.effective_user.id

        add_user(user_id)

        keyboard = [
            [
                InlineKeyboardButton(
                    "🔊 Voice",
                    callback_data="settings_voice",
                )
            ],
        ]

        await update.message.reply_text(
            "⚙️ *Settings*",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown",
        )

    except Exception:
        logger.exception("SETTINGS ERROR")

        await update.message.reply_text(
            "❌ Unable to open settings."
        )


# ============================================================
# /LIBRARY
# ============================================================

async def library(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    try:
        user_id = update.effective_user.id

        add_user(user_id)

        library_items = get_library(
            user_id,
            limit=10,
        )

        if not library_items:
            await update.message.reply_text(
                "📚 *Your Library*\n\n"
                "No saved audios yet.\n\n"
                "Generate some text-to-speech and save them to your library!",
                parse_mode="Markdown",
            )
            return

        keyboard = []

        for item in library_items:
            item_id = item[0]
            text = item[1]
            voice = item[2]
            created_at = item[4]

            # Truncate text for button display
            short_text = (
                text[:30] + "..."
                if len(text) > 30
                else text
            )

            button_text = (
                f"📄 {short_text}"
            )

            keyboard.append(
                [
                    InlineKeyboardButton(
                        button_text,
                        callback_data=f"lib:{item_id}",
                    )
                ]
            )

        await update.message.reply_text(
            "📚 *Your Library*\n\n"
            "Click any to view details",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown",
        )

    except Exception:
        logger.exception("LIBRARY ERROR")

        await update.message.reply_text(
            "❌ Unable to open library."
        )


# ============================================================
# CALLBACK HANDLER
# ============================================================

async def button_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    query = update.callback_query

    try:

        user_id = query.from_user.id
        data = query.data

        logger.info(
            "CALLBACK RECEIVED: data=%s user=%s",
            data,
            user_id,
        )

        # Check if user is allowed
        if not is_chat_allowed(user_id):
            await query.answer(
                f"Access denied. Ask {BOT_OWNER_HANDLE}",
                show_alert=True,
            )
            logger.warning(
                "Unauthorized button press from user %s",
                user_id,
            )
            return

        # Stop Telegram's loading spinner.
        await query.answer()

        add_user(user_id)

        # ----------------------------------------------------
        # TEXT TO SPEECH
        # ----------------------------------------------------

        if data == "tts":

            waiting_for_text.add(user_id)

            await query.message.reply_text(
                "📝 *Send the text you want to convert to speech.*",
                parse_mode="Markdown",
            )

            return

        # ----------------------------------------------------
        # SETTINGS
        # ----------------------------------------------------

        if data == "settings":

            keyboard = [
                [
                    InlineKeyboardButton(
                        "🔊 Voice",
                        callback_data="settings_voice",
                    )
                ],
            ]

            await query.edit_message_text(
                "⚙️ *Settings*",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown",
            )

            return

        # ----------------------------------------------------
        # LIBRARY VIEW (from start menu)
        # ----------------------------------------------------

        if data == "library_view":

            await library_callback(
                query,
                user_id,
            )

            return

        # ----------------------------------------------------
        # VOICE SETTINGS
        # ----------------------------------------------------

        if data == "settings_voice":

            await show_voices(
                query,
                user_id,
            )

            return

        # ----------------------------------------------------
        # BACK TO SETTINGS
        # ----------------------------------------------------

        if data == "settings_back":

            keyboard = [
                [
                    InlineKeyboardButton(
                        "🔊 Voice",
                        callback_data="settings_voice",
                    )
                ],
            ]

            await query.edit_message_text(
                "⚙️ *Settings*",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown",
            )

            return

        # ----------------------------------------------------
        # VOICE SELECTION
        # ----------------------------------------------------

        if data.startswith("voice:"):

            voice_id = data.split(
                ":",
                1,
            )[1]

            set_voice(
                user_id,
                voice_id,
            )

            await query.answer(
                f"Selected: {voice_id}",
                show_alert=False,
            )

            # Refresh the list so the new voice
            # gets the checkmark.
            await show_voices(
                query,
                user_id,
            )

            return

        # ----------------------------------------------------
        # SAVE TO LIBRARY
        # ----------------------------------------------------

        if data.startswith("save_library:"):

            target_user_id = int(
                data.split(
                    ":",
                    1,
                )[1]
            )

            # Only allow saving own audios
            if user_id != target_user_id:
                await query.answer(
                    "❌ You can only save your own audios.",
                    show_alert=True,
                )
                return

            if user_id not in pending_saves:
                await query.answer(
                    "❌ Audio data not found. Please generate a new audio.",
                    show_alert=True,
                )
                return

            save_data = pending_saves[user_id]

            try:

                library_id = save_to_library(
                    user_id=user_id,
                    text=save_data["text"],
                    voice=save_data["voice"],
                    file_path=f"msg_{save_data['message_id']}",
                )

                await query.answer(
                    f"✅ Saved to library! (ID: {library_id})",
                    show_alert=False,
                )

                # Remove from pending
                del pending_saves[user_id]

                logger.info(
                    "SAVED TO LIBRARY: user=%s library_id=%s",
                    user_id,
                    library_id,
                )

            except Exception:

                logger.exception(
                    "SAVE TO LIBRARY ERROR"
                )

                await query.answer(
                    "❌ Failed to save to library.",
                    show_alert=True,
                )

            return

        # ----------------------------------------------------
        # LIBRARY ITEM DETAILS
        # ----------------------------------------------------

        if data.startswith("lib:"):

            item_id = int(
                data.split(
                    ":",
                    1,
                )[1]
            )

            try:

                item = get_library_item(
                    user_id,
                    item_id,
                )

                if not item:
                    await query.answer(
                        "❌ Item not found.",
                        show_alert=True,
                    )
                    return

                item_id = item[0]
                text = item[1]
                voice = item[2]
                created_at = item[4]

                keyboard = [
                    [
                        InlineKeyboardButton(
                            "🗑️ Delete",
                            callback_data=f"del_lib:{item_id}",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "⬅️ Back",
                            callback_data="library_back",
                        )
                    ],
                ]

                message_text = (
                    f"📄 *Saved Audio*\n\n"
                    f"*Text:*\n`{text}`\n\n"
                    f"*Voice:* {voice}\n"
                    f"*Saved:* {created_at}\n"
                )

                await query.edit_message_text(
                    message_text,
                    reply_markup=InlineKeyboardMarkup(keyboard),
                    parse_mode="Markdown",
                )

            except Exception:

                logger.exception(
                    "LIBRARY ITEM ERROR"
                )

                await query.answer(
                    "❌ Failed to load item.",
                    show_alert=True,
                )

            return

        # ----------------------------------------------------
        # DELETE FROM LIBRARY
        # ----------------------------------------------------

        if data.startswith("del_lib:"):

            item_id = int(
                data.split(
                    ":",
                    1,
                )[1]
            )

            try:

                delete_from_library(
                    user_id,
                    item_id,
                )

                await query.answer(
                    "🗑️ Deleted from library",
                    show_alert=False,
                )

                await library_callback(
                    query,
                    user_id,
                )

                logger.info(
                    "DELETED FROM LIBRARY: user=%s item_id=%s",
                    user_id,
                    item_id,
                )

            except Exception:

                logger.exception(
                    "DELETE LIBRARY ERROR"
                )

                await query.answer(
                    "❌ Failed to delete.",
                    show_alert=True,
                )

            return

        # ----------------------------------------------------
        # LIBRARY BACK
        # ----------------------------------------------------

        if data == "library_back":

            try:

                await library_callback(
                    query,
                    user_id,
                )

            except Exception:

                logger.exception(
                    "LIBRARY BACK ERROR"
                )

            return

    except Exception:

        logger.exception(
            "BUTTON ERROR"
        )

        try:

            await query.message.reply_text(
                "❌ Something went wrong while processing that button."
            )

        except Exception:
            pass


# ============================================================
# VOICE LIST
# ============================================================

async def show_voices(
    query,
    user_id,
):

    try:

        logger.info(
            "Loading voices for user %s",
            user_id,
        )

        voices = get_voices()

        selected_voice = get_voice(
            user_id
        )

        if not voices:

            await query.edit_message_text(
                "❌ No voices are currently available."
            )

            return

        keyboard = []

        for voice in voices:

            voice_id = voice.get("id")

            if not voice_id:
                continue

            voice_name = (
                voice.get("name")
                or voice_id
            )

            short_name = str(
                voice_name
            ).strip()

            if voice_id == selected_voice:

                button_text = (
                    f"✅ {short_name}"
                )

            else:

                button_text = short_name

            keyboard.append(
                [
                    InlineKeyboardButton(
                        button_text,
                        callback_data=f"voice:{voice_id}",
                    )
                ]
            )

        keyboard.append(
            [
                InlineKeyboardButton(
                    "⬅️ Back",
                    callback_data="settings_back",
                )
            ]
        )

        await query.edit_message_text(
            "🔊 *Select Voice*\n\n"
            "Only one voice can be selected.",
            reply_markup=InlineKeyboardMarkup(
                keyboard
            ),
            parse_mode="Markdown",
        )

    except Exception:

        logger.exception(
            "VOICE LIST ERROR"
        )

        try:

            await query.message.reply_text(
                "❌ Failed to load the voice list."
            )

        except Exception:
            pass


# ============================================================
# LIBRARY DISPLAY
# ============================================================

async def library_callback(
    query,
    user_id,
):

    try:

        logger.info(
            "Loading library for user %s",
            user_id,
        )

        library_items = get_library(
            user_id,
            limit=10,
        )

        if not library_items:

            await query.edit_message_text(
                "📚 *Your Library*\n\n"
                "No saved audios yet.\n\n"
                "Generate some text-to-speech and save them to your library!"
            )

            return

        keyboard = []

        for item in library_items:

            item_id = item[0]
            text = item[1]

            # Truncate text for button display
            short_text = (
                text[:30] + "..."
                if len(text) > 30
                else text
            )

            button_text = (
                f"📄 {short_text}"
            )

            keyboard.append(
                [
                    InlineKeyboardButton(
                        button_text,
                        callback_data=f"lib:{item_id}",
                    )
                ]
            )

        await query.edit_message_text(
            "📚 *Your Library*\n\n"
            "Click any to view details",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown",
        )

    except Exception:

        logger.exception(
            "LIBRARY DISPLAY ERROR"
        )

        try:

            await query.message.reply_text(
                "❌ Failed to load library."
            )

        except Exception:
            pass


# ============================================================
# TEXT MESSAGE HANDLER
# ============================================================

async def handle_text(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    user_id = update.effective_user.id

    # Check if user is allowed
    if not is_chat_allowed(user_id):
        await update.message.reply_text(
            f"❌ Access Denied\n\n"
            f"Please ask {BOT_OWNER_HANDLE} to grant you access to this bot."
        )
        logger.warning(
            "Unauthorized text message from user %s",
            user_id,
        )
        return

    # Ignore normal messages unless the user
    # requested TTS.
    if user_id not in waiting_for_text:
        return

    waiting_for_text.discard(
        user_id
    )

    text = update.message.text.strip()

    if not text:

        await update.message.reply_text(
            "❌ Please send some text."
        )

        return

    # Maximum text length.
    if len(text) > 5000:

        await update.message.reply_text(
            "❌ Your text is too long.\n\n"
            "Please keep it under 5,000 characters."
        )

        return

    processing_message = await update.message.reply_text(
        "⏳ Processing your text..."
    )

    voice = get_voice(
        user_id
    )

    logger.info(
        "TTS REQUEST: user=%s voice=%s length=%s",
        user_id,
        voice,
        len(text),
    )

    try:

        audio_data = generate_speech(
            text=text,
            voice=voice,
        )

        audio_file = io.BytesIO(
            audio_data
        )

        audio_file.name = "speech.mp3"

        # Send audio with save button
        keyboard = [
            [
                InlineKeyboardButton(
                    "💾 Save to Library",
                    callback_data=f"save_library:{user_id}",
                )
            ],
        ]

        audio_message = await update.message.reply_audio(
            audio=audio_file,
            caption=f"🔊 Voice: {voice}",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

        # Store data for potential save
        pending_saves[user_id] = {
            "text": text,
            "voice": voice,
            "message_id": audio_message.message_id,
        }

        try:

            await processing_message.delete()

        except Exception:
            pass

    except Exception:

        logger.exception(
            "TTS GENERATION ERROR"
        )

        try:

            await processing_message.edit_text(
                "❌ Failed to generate the speech.\n\n"
                "Please try again."
            )

        except Exception:
            pass


# ============================================================
# /CANCEL
# ============================================================

async def cancel(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    user_id = update.effective_user.id

    waiting_for_text.discard(
        user_id
    )

    await update.message.reply_text(
        "❌ Text-to-speech request cancelled."
    )


# ============================================================
# ERROR HANDLER
# ============================================================

async def error_handler(
    update: object,
    context: ContextTypes.DEFAULT_TYPE,
):

    logger.error(
        "UNHANDLED ERROR: %s",
        context.error,
        exc_info=context.error,
    )


# ============================================================
# MAIN
# ============================================================

def main():

    # Create database/tables.
    init_db()

    # Create Telegram application.
    app = (
        Application
        .builder()
        .token(TELEGRAM_BOT_TOKEN)
        .build()
    )

    # --------------------------------------------------------
    # COMMANDS
    # --------------------------------------------------------

    app.add_handler(
        CommandHandler(
            "start",
            start,
        )
    )

    app.add_handler(
        CommandHandler(
            "settings",
            settings,
        )
    )

    app.add_handler(
        CommandHandler(
            "cancel",
            cancel,
        )
    )

    app.add_handler(
        CommandHandler(
            "library",
            library,
        )
    )

    # --------------------------------------------------------
    # CALLBACKS
    # --------------------------------------------------------

    # Catch ALL callback queries.
    app.add_handler(
        CallbackQueryHandler(
            button_handler
        )
    )

    # --------------------------------------------------------
    # TEXT
    # --------------------------------------------------------

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_text,
        )
    )

    # --------------------------------------------------------
    # ERROR HANDLER
    # --------------------------------------------------------

    app.add_error_handler(
        error_handler
    )

    # --------------------------------------------------------
    # START BOT
    # --------------------------------------------------------

    print("--------------------------------")
    print("🔊 TTS Telegram Bot")
    print("--------------------------------")
    print("Bot is running...")
    print("Waiting for updates...")
    print("--------------------------------")

    # IMPORTANT:
    # Telegram must deliver both normal messages
    # AND inline-button callback queries.
    app.run_polling(
        allowed_updates=[
            "message",
            "callback_query",
        ],
        drop_pending_updates=True,
    )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()