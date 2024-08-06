import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from states import Registration, LocationStates
from database import Database
from buttons import get_contact_button, main_menu, tanlov, order_plant_buttons, go_site
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = "6827097914:AAFzFaHv3YCouH9NpTaz0869aB10Y9yKCCk"
ADMIN_CHAT_IDS = ["1921911753", "7149602547"]  # Replace with actual admin chat IDs

bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
storage = MemoryStorage()
dp = Dispatcher(bot=bot, storage=storage)

db = Database()

async def on_startup(dispatcher):
    for admin_id in ADMIN_CHAT_IDS:
        await bot.send_message(admin_id, "Bot started successfully!")

async def on_shutdown(dispatcher):
    for admin_id in ADMIN_CHAT_IDS:
        await bot.send_message(admin_id, "Bot is shutting down. Goodbye!")

@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    user_id = message.from_user.id
    user = db.get_user(user_id)
    
    if user:
        full_name = message.from_user.full_name
        await message.answer(f"👋 Salom <b>{full_name}</b> Botimizga xush kelibsiz!", reply_markup=main_menu())
    else:
        full_name = message.from_user.full_name
        await message.answer(f"Salom {full_name}. Botimizga xush kelibsiz!")
        await message.answer("⚠️ Botimizdan to'liq foydalanish uchun registratsiyadan o'tishingiz kerak ⚠️")
        await message.answer("👤  Ismingizni kiriting: ")
        await Registration.waiting_for_name.set()

@dp.message_handler(state=Registration.waiting_for_name, content_types=types.ContentTypes.TEXT)
async def process_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['full_name'] = message.text
    await message.answer("☎️ Telefon raqamingizni yuboring:", reply_markup=get_contact_button())
    await Registration.waiting_for_phone_number.set()

@dp.message_handler(state=Registration.waiting_for_phone_number, content_types=types.ContentTypes.CONTACT)
async def process_phone_number(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['phone_number'] = message.contact.phone_number
        user_id = message.from_user.id

        # Save to SQLite3
        try:
            db.add_user(user_id, data['full_name'], data['phone_number'])
            await message.answer("🥳🥳 Registratsiyadan muvaffaqiyatli o'tdingiz!" , reply_markup=main_menu())
        except Exception as e:
            await message.answer(f"Xatolik yuz berdi: {str(e)}")

    await state.finish()

# Main menu default button handler

@dp.message_handler(text="♻️ Chiqindilarni tozalash xizmati")
async def chiqindi_handler(message: types.Message):
    user_id = message.from_user.id
    user = db.get_user(user_id)
    
    if user:
        await message.answer("Lokatsiya yuboring. Matn ko'rinishidami yoki Lokatsiya ko'rinishidami?", reply_markup=tanlov())  

@dp.message_handler(text="📍 Lokatsiya yuboraman")
async def send_location_handler(message: types.Message):
    await message.answer("Iltimos, lokatsiyangizni yuboring.", reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton("Lokatsiyani yuborish", request_location=True)))
    await LocationStates.waiting_for_location.set()

@dp.message_handler(content_types=types.ContentTypes.LOCATION, state=LocationStates.waiting_for_location)
async def receive_location(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['location'] = message.location
    await message.answer("Rasm yuboring.", reply_markup=ReplyKeyboardRemove())
    await LocationStates.waiting_for_image.set()

@dp.message_handler(content_types=types.ContentTypes.PHOTO, state=LocationStates.waiting_for_image)
async def receive_image(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['image'] = message.photo[-1].file_id
        user_id = message.from_user.id
        user = db.get_user(user_id)

    await message.answer("Ma'sullar tez orada habardor etiladi")
    await LocationStates.waiting_for_order_response.set()


    await message.answer("Chiqindi tozalangan joyga o'simlik sotib olasizmi? ",  reply_markup=order_plant_buttons())


    # Send a message to the admins
    location = data['location']
    location_url = f"https://www.google.com/maps?q={location.latitude},{location.longitude}"
    for admin_id in ADMIN_CHAT_IDS:
        await bot.send_message(admin_id, f"Foydalanuvchi {user[2]} ({user[3]}) quyidagi joyda chiqindilarni tashlagan:\n\nLokatsiya: {location_url}\n\nRasm:", parse_mode="HTML")
        await bot.send_photo(admin_id, photo=data['image'])

@dp.message_handler(state=LocationStates.waiting_for_order_response, text="Ha")
async def order_plant_yes(message: types.Message, state: FSMContext):
    await message.answer("""Agarda siz o'simlikar arzon narxda o'simliklar sotib olmoqchi bo'lsangiz, unda bizning saytimizga murojaat qilishingiz mumkin!
Bu saytda o'simliklar va daraxtlar narxlarini bilib olishingiz mumkin. Agarda sizga qulay bo'lsa bemalol sotib olishingiz mumkin!

Saytga o'tish uchun 👇BOSING👇
    """, reply_markup=go_site())
    await state.finish()

@dp.message_handler(state=LocationStates.waiting_for_order_response, text="Yo'q")
async def order_plant_no(message: types.Message, state: FSMContext):
    await message.answer("Xizmatimizdan foydalanganingiz uchun rahmat.", reply_markup=main_menu())
    await state.finish()

@dp.message_handler(text="✍️ Matn yuboraman")
async def send_matn_handler(message: types.Message):
    await message.answer("Lokatsiyani matn ko'rinishida yuboring:", reply_markup=ReplyKeyboardRemove())
    await LocationStates.waiting_for_text_location.set()

@dp.message_handler(state=LocationStates.waiting_for_text_location, content_types=types.ContentTypes.TEXT)
async def receive_text_location(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['text_location'] = message.text
    await message.answer("Rasm yuboring.")
    await LocationStates.waiting_for_image_text.set()

@dp.message_handler(content_types=types.ContentTypes.PHOTO, state=LocationStates.waiting_for_image_text)
async def receive_image_text(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['image'] = message.photo[-1].file_id
        user_id = message.from_user.id
        user = db.get_user(user_id)

    await message.answer("Ma'sullar tez orada habardor etiladi")
    await LocationStates.waiting_for_order_response.set()


    await message.answer("Chiqindi tozalangan joyga o'simlik sotib olasizmi? ", reply_markup=order_plant_buttons())


    # Send a message to the admins
    # for admin_id in ADMIN_CHAT_IDS:
    #     await bot.send_message(admin_id, f"Foydalanuvchi {user[2]} ({user[3]}) quyidagi joyda chiqindilarni tashlagan:\n\nLokatsiya: {data['text_location']}\n\nRasm:", parse_mode="HTML")
    #     await bot.send_photo(admin_id, photo=data['image'])

@dp.message_handler(state=LocationStates.waiting_for_order_response, text="Ha")
async def order_plant_yes(message: types.Message, state: FSMContext):
    await message.answer("""Agarda siz o'simlikar arzon narxda o'simliklar sotib olmoqchi bo'lsangiz, unda bizning saytimizga murojaat qilishingiz mumkin!
Bu saytda o'simliklar va daraxtlar narxlarini bilib olishingiz mumkin. Agarda sizga qulay bo'lsa bemalol sotib olishingiz mumkin!

Saytga o'tish uchun 👇BOSING👇
    """, reply_markup=go_site())
    await state.finish()

@dp.message_handler(state=LocationStates.waiting_for_order_response, text="Yo'q")
async def order_plant_no(message: types.Message, state: FSMContext):
    await message.answer("Xizmatimizdan foydalanganingiz uchun rahmat.", reply_markup=main_menu())
    await state.finish()











@dp.message_handler(text="🌱 O'simliklarga buyurtma berish")

async def buyurtma_handler(message: types.Message):
    user_id = message.from_user.id
    user = db.get_user(user_id)

    if user:
        await message.answer("""Agarda siz o'simlikar arzon narxda o'simliklar sotib olmoqchi bo'lsangiz, unda bizning saytimizga murojaat qilishingiz mumkin!
Bu saytda o'simliklar va daraxtlar narxlarini bilib olishingiz mumkin. Agarda sizga qulay bo'lsa bemalol sotib olishingiz mumkin!

Saytga o'tish uchun 👇BOSING👇
    """, reply_markup=go_site())






if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup, on_shutdown=on_shutdown)
