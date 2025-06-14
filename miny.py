import telebot
from telebot import types

# التوكن الخاص بك
BOT_TOKEN = "7614130669:AAFVyV6j4u5PtC9ZR2Xru-LYyxWBK-h8brM"

bot = telebot.TeleBot(BOT_TOKEN)

# --- قاموس النصوص للترجمة ---
# كل نصوص البوت موجودة هنا باللغتين
texts = {
    'ar': {
        "welcome": "👋 أهلًا بك في بوت حساب السعرات.\n\nالرجاء اختيار لغتك:",
        "lang_chosen": "✅ تم اختيار اللغة العربية.",
        "gender_prompt": "لنبدأ، يرجى اختيار جنسك:",
        "gender_male": "ذكر 🧍‍♂",
        "gender_female": "أنثى 🧍‍♀",
        "weight_prompt": "الآن، من فضلك أدخل وزنك بالكيلوجرام (مثال: 75) ⚖:",
        "height_prompt": "💪 ممتاز، الآن أدخل طولك بالسنتيمتر (مثال: 170):",
        "age_prompt": "👍 جيد، والآن عمرك بالسنوات؟",
        "activity_prompt": "آخر خطوة، ما هو مستوى نشاطك اليومي؟ 🏃‍♂",
        "calculating": "⏳ تمام! جاري حساب سعراتك، لحظات من فضلك...",
        "error_numeric": "❌ خطأ. يرجى إدخال رقم صحيح.",
        "activity_sedentary": "قليل جداً (عمل مكتبي)",
        "activity_light": "خفيف (تمرين 1-3 أيام بالأسبوع)",
        "activity_moderate": "متوسط (تمرين 3-5 أيام بالأسبوع)",
        "activity_active": "عالي (تمرين 6-7 أيام بالأسبوع)",
        "activity_very_active": "عالي جداً (مجهود بدني عنيف)",
        "result_message": (
            "═══════ 📈 *نتيجتـك* ═══════\n\n"
            "سعرات الثبات اليومية للحفاظ على وزنك هي:\n\n"
            " caloric *{final_calories}* \n\n"
            "-----------------------------------------\n"
            "💡 *لتحقيق هدفك:*\n"
            "  - *لزيادة الوزن (تضخيم):* أضف 500 إلى 800 سعر حراري.\n"
            "  - *لخسارة الوزن (تنشيف):* أنقص 500 إلى 800 سعر حراري."
        )
    },
    'en': {
        "welcome": "👋 Welcome to the Calorie Calculator Bot.\n\nPlease choose your language:",
        "lang_chosen": "✅ English has been selected.",
        "gender_prompt": "Let's start, please select your gender:",
        "gender_male": "Male 🧍‍♂",
        "gender_female": "Female 🧍‍♀",
        "weight_prompt": "Now, please enter your weight in kilograms (e.g., 75) ⚖:",
        "height_prompt": "💪 Excellent, now enter your height in centimeters (e.g., 170):",
        "age_prompt": "👍 Great, and now your age in years?",
        "activity_prompt": "Last step, what is your daily activity level? 🏃‍♂",
        "calculating": "⏳ Perfect! Calculating your calories, one moment please...",
        "error_numeric": "❌ Error. Please enter a valid number.",
        "activity_sedentary": "Sedentary (office job)",
        "activity_light": "Light (exercise 1-3 days/week)",
        "activity_moderate": "Moderate (exercise 3-5 days/week)",
        "activity_active": "Active (exercise 6-7 days/week)",
        "activity_very_active": "Very Active (hard physical job)",
        "result_message": (
            "═══════ 📈 *Your Result* ═══════\n\n"
            "Your daily maintenance calories are:\n\n"
            " calories *{final_calories}* \n\n"
            "-----------------------------------------\n"
            "💡 *To achieve your goal:*\n"
            "  - *To gain weight (bulking):* Add 500 to 800 calories.\n"
            "  - *To lose weight (cutting):* Subtract 500 to 800 calories."
        )
    }
}

user_data = {}

def calculate_calories(data):
    s = 5 if data['gender'] == 'male' else -161
    bmr = (10 * data['weight']) + (6.25 * data['height']) - (5 * data['age']) + s
    tdee = bmr * data['activity_level']
    return round(tdee)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.chat.id
    user_data[user_id] = {}
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    ar_btn = types.InlineKeyboardButton("العربية 🇸🇾", callback_data='lang_ar')
    en_btn = types.InlineKeyboardButton("English 🇬🇧", callback_data='lang_en')
    markup.add(ar_btn, en_btn)
    bot.send_message(user_id, texts['ar']['welcome'] + "\n\n" + texts['en']['welcome'], reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('lang_'))
def language_callback(call):
    user_id = call.message.chat.id
    lang = call.data.split('_')[1]
    user_data[user_id]['lang'] = lang
    
    bot.edit_message_text(texts[lang]['lang_chosen'], user_id, call.message.message_id)
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    male_btn = types.InlineKeyboardButton(texts[lang]['gender_male'], callback_data='gender_male')
    female_btn = types.InlineKeyboardButton(texts[lang]['gender_female'], callback_data='gender_female')
    markup.add(male_btn, female_btn)
    bot.send_message(user_id, texts[lang]['gender_prompt'], reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('gender_'))
def gender_callback(call):
    user_id = call.message.chat.id
    lang = user_data[user_id]['lang']
    user_data[user_id]['gender'] = 'male' if call.data == 'gender_male' else 'female'
    
    bot.delete_message(user_id, call.message.message_id)
    msg = bot.send_message(user_id, texts[lang]['weight_prompt'])
    bot.register_next_step_handler(msg, get_weight)

def get_weight(message):
    user_id = message.chat.id
    lang = user_data[user_id]['lang']
    try:
        weight = float(message.text)
        if not (20 < weight < 250): raise ValueError
        user_data[user_id]['weight'] = weight
        msg = bot.send_message(user_id, texts[lang]['height_prompt'])
        bot.register_next_step_handler(msg, get_height)
    except (ValueError, TypeError):
        msg = bot.send_message(user_id, texts[lang]['error_numeric'])
        bot.register_next_step_handler(msg, get_weight)

def get_height(message):
    user_id = message.chat.id
    lang = user_data[user_id]['lang']
    try:
        height = float(message.text)
        if not (100 < height < 250): raise ValueError
        user_data[user_id]['height'] = height
        msg = bot.send_message(user_id, texts[lang]['age_prompt'])
        bot.register_next_step_handler(msg, get_age)
    except (ValueError, TypeError):
        msg = bot.send_message(user_id, texts[lang]['error_numeric'])
        bot.register_next_step_handler(msg, get_height)

def get_age(message):
    user_id = message.chat.id
    lang = user_data[user_id]['lang']
    try:
        age = int(message.text)
        if not (10 < age < 100): raise ValueError
        user_data[user_id]['age'] = age
        
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(types.InlineKeyboardButton(texts[lang]['activity_sedentary'], callback_data='activity_1.2'))
        markup.add(types.InlineKeyboardButton(texts[lang]['activity_light'], callback_data='activity_1.375'))
        markup.add(types.InlineKeyboardButton(texts[lang]['activity_moderate'], callback_data='activity_1.55'))
        markup.add(types.InlineKeyboardButton(texts[lang]['activity_active'], callback_data='activity_1.725'))
        markup.add(types.InlineKeyboardButton(texts[lang]['activity_very_active'], callback_data='activity_1.9'))
        
        bot.send_message(user_id, texts[lang]['activity_prompt'], reply_markup=markup)
    except (ValueError, TypeError):
        msg = bot.send_message(user_id, texts[lang]['error_numeric'])
        bot.register_next_step_handler(msg, get_age)

@bot.callback_query_handler(func=lambda call: call.data.startswith('activity_'))
def activity_callback(call):
    user_id = call.message.chat.id
    lang = user_data[user_id]['lang']
    activity_level = float(call.data.split('_')[1])
    user_data[user_id]['activity_level'] = activity_level
    
    bot.edit_message_text(texts[lang]['calculating'], user_id, call.message.message_id)
    
    final_calories = calculate_calories(user_data[user_id])
    
    result_template = texts[lang]['result_message']
    result_text = result_template.format(final_calories=final_calories)
    
    bot.send_message(user_id, result_text, parse_mode='Markdown')

print("Bot is running...")
bot.polling(none_stop=True)
