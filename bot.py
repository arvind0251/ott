import os
import logging
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv
import razorpay
from aiogram.dispatcher.filters import Text

# Load API Keys from environment variables
load_dotenv()
API_KEY = os.getenv("OTPFAST_API_KEY")
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")
API_URL = "http://otpfast.co/stubs/handler_api.php"

# Setup bot
logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# Setup Razorpay client
razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

# Main Menu
async def main_menu(message: types.Message):
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("Buy Numbers", callback_data="buy_numbers"),
        InlineKeyboardButton("ReadyMade Accounts 🔥", callback_data="ready_accounts"),
        InlineKeyboardButton("Recharge", callback_data="recharge"),
        InlineKeyboardButton("Refer & Earn", callback_data="refer_earn"),
        InlineKeyboardButton("Numbers History", callback_data="num_history"),
        InlineKeyboardButton("Transaction History", callback_data="txn_history"),
        InlineKeyboardButton("API Tools", callback_data="api_tools"),
        InlineKeyboardButton("Contact Support", callback_data="contact_support")
    )
    await message.reply("\U0001F4C8 Welcome to the OTP Seller Bot! Select an option:", reply_markup=keyboard)

# Command: /start
@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await main_menu(message)

# Command: /balance
@dp.message_handler(commands=['balance'])
async def check_balance(message: types.Message):
    response = requests.get(f"{API_URL}?api_key={API_KEY}&action=getBalance")
    if response.status_code == 200:
        await message.reply(f"\U0001F4B8 Your Balance: {response.text} credits")
    else:
        await message.reply("❌ Error fetching balance. Please try again later.")

# Buy Numbers Handler
@dp.callback_query_handler(lambda call: call.data == "buy_numbers")
async def buy_numbers(call: types.CallbackQuery):
    await call.message.edit_text("\U0001F4F1 Select a country and service to buy a number.")

# ReadyMade Accounts Handler
@dp.callback_query_handler(lambda call: call.data == "ready_accounts")
async def ready_accounts(call: types.CallbackQuery):
    await call.message.edit_text("\U0001F4BB ReadyMade Accounts (IRCTC, etc.) will be available soon.")

# Recharge Handler with Payment Verification
@dp.callback_query_handler(lambda call: call.data == "recharge")
async def recharge(call: types.CallbackQuery):
    order_amount = 10000  # Amount in paise (100 INR)
    order_currency = "INR"
    order_receipt = f"order_rcptid_{call.from_user.id}"
    
    order = razorpay_client.order.create({
        "amount": order_amount,
        "currency": order_currency,
        "receipt": order_receipt,
        "payment_capture": 1
    })
    
    payment_link = f"https://rzp.io/i/{order['id']}"
    await call.message.edit_text(f"\U0001F4B5 Recharge your account using Razorpay: [Pay Now]({payment_link})", parse_mode="Markdown")

# Payment Verification Handler
@dp.message_handler(Text(startswith="/verify_payment "))
async def verify_payment(message: types.Message):
    payment_id = message.text.split()[1]
    try:
        payment = razorpay_client.payment.fetch(payment_id)
        if payment["status"] == "captured":
            await message.reply(f"✅ Payment successful! Transaction ID: {payment_id}")
        else:
            await message.reply("❌ Payment not successful. Please try again.")
    except Exception as e:
        await message.reply(f"❌ Error verifying payment: {str(e)}")

# Refer & Earn Handler
@dp.callback_query_handler(lambda call: call.data == "refer_earn")
async def refer_earn(call: types.CallbackQuery):
    await call.message.edit_text("\U0001F4B0 Invite friends and earn rewards! Feature coming soon.")

# Numbers History Handler
@dp.callback_query_handler(lambda call: call.data == "num_history")
async def num_history(call: types.CallbackQuery):
    await call.message.edit_text("\U0001F4DD Your purchased numbers history will be displayed here.")

# Transaction History Handler
@dp.callback_query_handler(lambda call: call.data == "txn_history")
async def txn_history(call: types.CallbackQuery):
    await call.message.edit_text("\U0001F4B3 Your transaction history will be displayed here.")

# API Tools Handler
@dp.callback_query_handler(lambda call: call.data == "api_tools")
async def api_tools(call: types.CallbackQuery):
    await call.message.edit_text("\U0001F50E Developer API tools will be available soon.")

# Contact Support Handler
@dp.callback_query_handler(lambda call: call.data == "contact_support")
async def contact_support(call: types.CallbackQuery):
    await call.message.edit_text("\U0001F4DE Contact us at: @SupportBot")

# Run bot
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
