"""Telegram-бот «Закупка фруктов» — оптовые заказы."""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime
from pathlib import Path

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO,
)
log = logging.getLogger("fruit-order-bot")

# Состояния разговора
CHOOSING_FRUIT, ENTERING_QUANTITY, ATTACHING_FILE, CONFIRMING = range(4)

DATA_FILE = Path(__file__).resolve().parent / "orders.json"


def load_fruits() -> list[str]:
    raw = os.environ.get(
        "FRUITS",
        "Яблоки,Бананы,Апельсины,Мандарины,Груши,Киви,Виноград,Ананасы",
    )
    return [s.strip() for s in raw.split(",") if s.strip()]


def get_supplier_chat_id() -> int | None:
    value = os.environ.get("SUPPLIER_CHAT_ID")
    if not value:
        log.warning("SUPPLIER_CHAT_ID не установлен!")
        return None
    try:
        return int(value)
    except ValueError:
        log.error("SUPPLIER_CHAT_ID должен быть числом!")
        return None


def load_orders() -> list[dict]:
    if not DATA_FILE.exists():
        return []
    try:
        return json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except Exception as e:
        log.error(f"Ошибка чтения orders.json: {e}")
        return []


def save_orders(items: list[dict]) -> None:
    try:
        DATA_FILE.write_text(
            json.dumps(items, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except Exception as e:
        log.error(f"Ошибка сохранения orders.json: {e}")


async def cmd_start(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    name = user.first_name if user else "покупатель"
    await update.message.reply_text(
        f"🍎 Привет, {name}!\n\n"
        "Я бот для оформления **оптовых заказов** фруктов.\n\n"
        "Команды:\n"
        "/order  — оформить заказ\n"
        "/list   — мои последние заказы\n"
        "/help   — помощь\n"
        "/cancel — отменить текущее действие"
    )


async def cmd_help(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "🍏 **Как оформить заказ:**\n\n"
        "1. Напишите /order\n"
        "2. Выберите фрукт\n"
        "3. Укажите количество в кг\n"
        "4. При желании пришлите фото + /skip\n"
        "5. Подтвердите заказ\n\n"
        "Поставщик получит заказ автоматически.",
        parse_mode="Markdown"
    )


async def cmd_list(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    orders = [o for o in load_orders() if o.get("user_id") == user_id]
    orders = orders[-10:]

    if not orders:
        await update.message.reply_text("📭 У вас пока нет заказов.")
        return

    lines = ["📋 **Ваши последние заказы:**"]
    for order in reversed(orders):
        ts = datetime.fromisoformat(order['ts']).strftime("%d.%m %H:%M")
        lines.append(f"• {ts} — {order['fruit']}: {order['quantity']} кг")
    
    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")


async def cmd_order(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    fruits = load_fruits()
    keyboard = [[InlineKeyboardButton(f"🍎 {f}", callback_data=f"fruit::{f}")] for f in fruits]

    await update.message.reply_text(
        "🍎 **Выберите фрукт для заказа:**",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )
    context.user_data.clear()
    return CHOOSING_FRUIT


async def on_fruit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    fruit = query.data.split("::")[1]

    context.user_data["fruit"] = fruit
    await query.edit_message_text(
        f"✅ Вы выбрали: **{fruit}**\n\n"
        "Укажите количество в килограммах (например: `50`, `120.5`):",
        parse_mode="Markdown"
    )
    return ENTERING_QUANTITY


async def on_quantity(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = (update.message.text or "").strip()
    
    # Проверка на число (включая десятичные)
    try:
        qty = float(text.replace(",", "."))
        if qty <= 0:
            raise ValueError
        context.user_data["quantity"] = str(qty)
    except ValueError:
        await update.message.reply_text("❌ Пожалуйста, введите корректное количество (например: 50 или 120.5)")
        return ENTERING_QUANTITY

    await update.message.reply_text(
        "📸 Пришлите фото (по желанию) или отправьте /skip"
    )
    return ATTACHING_FILE


async def on_file(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    msg = update.message
    if msg.document:
        context.user_data["attachment"] = {
            "kind": "document",
            "file_id": msg.document.file_id,
            "name": msg.document.file_name
        }
    elif msg.photo:
        context.user_data["attachment"] = {
            "kind": "photo",
            "file_id": msg.photo[-1].file_id
        }
    else:
        await msg.reply_text("❌ Пришлите фото или документ.")
        return ATTACHING_FILE

    return await preview(update, context)


async def on_skip(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["attachment"] = None
    return await preview(update, context)


async def preview(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    fruit = context.user_data.get("fruit", "?")
    quantity = context.user_data.get("quantity", "?")
    att = context.user_data.get("attachment")
    att_text = att["kind"] if att else "нет"

    keyboard = [
        [
            InlineKeyboardButton("✅ Подтвердить", callback_data="send"),
            InlineKeyboardButton("❌ Отмена", callback_data="cancel"),
        ]
    ]

    text = (
        f"**Проверьте заказ:**\n\n"
        f"🍏 Фрукт: {fruit}\n"
        f"⚖️ Количество: {quantity} кг\n"
        f"📎 Фото/файл: {att_text}"
    )

    await update.effective_message.reply_text(
        text, 
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )
    return CONFIRMING


async def on_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    if query.data == "cancel":
        await query.edit_message_text("❌ Заказ отменён.")
        return ConversationHandler.END

    user = update.effective_user
    supplier_chat_id = get_supplier_chat_id()
    fruit = context.user_data.get("fruit")
    quantity = context.user_data.get("quantity")
    att = context.user_data.get("attachment")

    record = {
        "user_id": user.id,
        "user_name": user.full_name,
        "username": user.username,
        "fruit": fruit,
        "quantity": quantity,
        "ts": datetime.now().isoformat(timespec="seconds"),
        "attachment": att,
    }

    orders = load_orders()
    orders.append(record)
    save_orders(orders)

    await query.edit_message_text("✅ **Заказ успешно оформлен!**")

    # Пересылка поставщику
    if supplier_chat_id:
        try:
            header = (
                f"🛒 **Новый заказ!**\n\n"
                f"👤 Заказчик: {user.full_name}\n"
                f"🔗 @{user.username or '—'}\n"
                f"🍏 Фрукт: {fruit}\n"
                f"⚖️ Количество: {quantity} кг\n"
                f"🕒 {datetime.now().strftime('%d.%m.%Y %H:%M')}"
            )
            await context.bot.send_message(supplier_chat_id, header, parse_mode="Markdown")

            if att:
                caption = f"Заказ: {fruit} — {quantity} кг"
                if att["kind"] == "document":
                    await context.bot.send_document(supplier_chat_id, att["file_id"], caption=caption)
                elif att["kind"] == "photo":
                    await context.bot.send_photo(supplier_chat_id, att["file_id"], caption=caption)
        except Exception as e:
            log.error("Не удалось отправить заказ поставщику", exc_info=True)

    return ConversationHandler.END


async def cmd_cancel(update: Update, _: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("❌ Действие отменено.")
    return ConversationHandler.END


def build_application() -> Application:
    token = os.environ.get("BOT_TOKEN")
    if not token:
        raise SystemExit("❌ BOT_TOKEN не установлен в переменных окружения!")

    app = Application.builder().token(token).build()

    order_conv = ConversationHandler(
        entry_points=[CommandHandler("order", cmd_order)],
        states={
            CHOOSING_FRUIT: [CallbackQueryHandler(on_fruit, pattern=r"^fruit::")],
            ENTERING_QUANTITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, on_quantity)],
            ATTACHING_FILE: [
                CommandHandler("skip", on_skip),
                MessageHandler(filters.Document.ALL | filters.PHOTO, on_file),
            ],
            CONFIRMING: [CallbackQueryHandler(on_confirm, pattern=r"^(send|cancel)$")],
        },
        fallbacks=[CommandHandler("cancel", cmd_cancel)],
        name="fruit_order_conversation",
        persistent=False,
    )

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("list", cmd_list))
    app.add_handler(order_conv)

    return app


def main() -> None:
    app = build_application()
    log.info("🍎 Бот для закупки фруктов успешно запущен")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()