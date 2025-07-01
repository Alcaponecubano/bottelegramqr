import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)
import qrcode
from io import BytesIO
import binascii
import urllib.parse

# Configuración básica
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = "TU_TOKEN_AQUÍ"  # Reemplaza con tu token real

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Maneja el comando /start."""
    user = update.effective_user
    await update.message.reply_text(
        f"👋 ¡Hola {user.first_name}!\n\n"
        "📝 Envíame cualquier texto y te lo puedo convertir en:\n"
        "🔳 Código QR\n"
        "🅷 Código Hexadecimal\n"
        "𝟘𝟙 Código Binario\n\n"
        "¡Prueba enviando palabras como 'perro' o cualquier texto!"
    )

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Muestra opciones de conversión cuando recibe texto."""
    user_text = update.message.text
    
    # Codificamos el texto para el callback_data
    encoded_text = urllib.parse.quote_plus(user_text)
    
    keyboard = [
        [
            InlineKeyboardButton("🔳 QR", callback_data=f"qr|{encoded_text}"),
            InlineKeyboardButton("🅷 Hex", callback_data=f"hex|{encoded_text}"),
            InlineKeyboardButton("𝟘𝟙 Bin", callback_data=f"bin|{encoded_text}"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"📌 Texto recibido: {user_text}\n"
        "Elige el formato de conversión:",
        reply_markup=reply_markup
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Maneja las pulsaciones de los botones."""
    query = update.callback_query
    await query.answer()
    
    try:
        action, encoded_text = query.data.split("|", 1)
        original_text = urllib.parse.unquote_plus(encoded_text)
        
        if action == "qr":
            # Generar QR
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(original_text)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            bio = BytesIO()
            img.save(bio, format='PNG')
            bio.seek(0)
            
            await query.message.reply_photo(
                photo=bio,
                caption=f"🔳 Código QR para:\n{original_text}"
            )
            
        elif action == "hex":
            # Convertir a hexadecimal
            hex_text = ' '.join(f"{ord(c):02x}" for c in original_text)
            await query.message.reply_text(
                f"🅷 Texto en Hexadecimal:\n\n{hex_text}"
            )
            
        elif action == "bin":
            # Convertir a binario
            binary_text = ' '.join(format(ord(c), '08b') for c in original_text)
            await query.message.reply_text(
                f"𝟘𝟙 Texto en Binario:\n\n{binary_text}"
            )
        
        await query.edit_message_text(f"✅ Conversión completada para:\n{original_text}")
        
    except Exception as e:
        logger.error(f"Error en button_handler: {str(e)}", exc_info=True)
        await query.message.reply_text("⚠️ Lo siento, ocurrió un error al procesar tu texto")

def main() -> None:
    """Inicia el bot con configuración robusta."""
    try:
        application = (
            ApplicationBuilder()
            .token(TOKEN)
            .arbitrary_callback_data(True)  # Permite callback_data más largos
            .build()
        )
        
        # Handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
        application.add_handler(CallbackQueryHandler(button_handler))
        
        logger.info("Bot iniciado correctamente")
        application.run_polling()
        
    except Exception as e:
        logger.critical(f"Error al iniciar el bot: {str(e)}", exc_info=True)

if __name__ == "__main__":
    main() 
