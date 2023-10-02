from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.types import InlineKeyboardMarkup as ikm
from pyrogram.types import InlineKeyboardButton as ikb
from pyrogram.enums import ChatMemberStatus
from pyrogram.handlers import MessageHandler
import time
import re
from bs4 import BeautifulSoup as bs
import requests
import pymongo
from pyrogram import enums
import asyncio
movieHandler = None

bot = Client(
    "TelegTRaam",
    bot_token="6006954134:AAGWGUDofKy5uXgaHDV0PVYC56uV7GxTMDY",
    api_id=1712043,
    api_hash="965c994b615e2644670ea106fd31daaf"
)

channel_id = -1001855899992

connection_string = "mongodb+srv://smit:smit@cluster0.nrkkfnp.mongodb.net/?retryWrites=true&w=majority"
clientt = pymongo.MongoClient(connection_string)
db = clientt["MovieBot"]
user_collection = db["users"]


def UsrRegorNot(user_id):
    user = user_collection.find_one({"user_id": user_id})
    return user is not None


channel_username = "@mrxedbot_updates"


def check_joined():
    async def func(flt, bot, message):
        join_msg = f"**To use this bot, please join our channel**"
        user_id = message.from_user.id
        chat_id = message.chat.id
        try:
            member_info = await bot.get_chat_member(channel_username, user_id)
            if member_info.status in (ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.MEMBER):
                return True
            else:
                await bot.send_message(chat_id, join_msg , reply_markup=ikm([[ikb("🎬 Join Channel", url="https://t.me/mrxedbot_updates")]]))
                return False
        except Exception as e:
            await bot.send_message(chat_id, join_msg , reply_markup=ikm([[ikb("🎬 Join Channel", url="https://t.me/mrxedbot_updates")]]))
            return False

    return filters.create(func)


@bot.on_message(filters.command("start") & check_joined())
async def start(bot, message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    global search_result
    search_result  = await bot.send_message(chat_id , "<b><i> This bot generates Top 3 Results of the search query. </i></b> ")
    await bot.send_message(chat_id, "Welcome to the Movie Bot\n <code> Developer :- </code> @mrxedbot_updates ", reply_markup=ikm([[ikb("🎬 Movies", callback_data="movie")]]))



async def movie(bot, message):
    await search_result.delete()
    await welcome_msg.delete()
    search_msg = await bot.send_message(message.chat.id, "<code> Searching... </code>")
    mname = message.text
    url = "https://filmyfly.store/site-search.html?to-search=" + mname
    print(url)
    r = requests.get(url)
    soup = bs(r.content, 'html.parser')
    links = soup.find_all('a', href=re.compile("/page-download"))
    if links == []:
        await search_msg.delete()
        nores_found = await bot.send_message(message.chat.id, "No Results Found")
        await asyncio.sleep(4)
        await nores_found.delete()

        return
    href_list = set()

    for link in links:
        href = link.get('href')
        linkjoin = "https://filmyfly.store" + href
        if href:
            href_list.add(linkjoin)
        if len(href_list) == 3:
            break
    
    

    await search_msg.edit("<code>Getting Download Links 🧐.... \n Please Wait</code>")
    await asyncio.sleep(1)
    await search_msg.edit("<code>Sending Links 😊...</code>")
    await asyncio.sleep(1)
    for i in href_list:
        m1 = requests.get(i)
        soup1 = bs(m1.content, "html.parser")
        
        movie_link4 = soup1.find("a", href=re.compile("https://linkmake.in/"))
        if movie_link4 == None:
            try:
                await search_msg.delete()
            except:
                pass
            nores_found = await bot.send_message(message.chat.id, "No Results Found")
            await asyncio.sleep(4)
            await nores_found.delete()
            return
        movie_link5 = movie_link4["href"]
       
        if movie_link5 == None:
            try:
                await search_msg.delete()
            except:
                pass
            nores_found = await bot.send_message(message.chat.id, "No Results Found")
            await asyncio.sleep(4)
            await nores_found.delete()
            return
        m2 = requests.get(movie_link5)
        soup2 = bs(m2.content, "html.parser")
        mn = soup2.find("div", class_="pt-fname").text
        m7 = soup2.find_all("div", class_="dlink dl")
        dbtn = []
        
        
        for i in m7:
            a = i.find('a')
            b = i.text
            c = a["href"]
            i.append(c)
            dbtn.append([ikb(text=b, url=c)])
        
        
        await bot.send_message(message.chat.id, f"**Movie Name :** `{mn}`", reply_markup=ikm(dbtn))
    await search_msg.delete()
    search_msg = await bot.send_message(message.chat.id, "<code> Search Completed👍 </code>")
    await asyncio.sleep(3)
    await search_msg.delete()
        


@bot.on_message(filters.private & filters.command("register"))
async def regusr(bot, message):
    user_id = message.from_user.id
    existing_user = user_collection.find_one({"user_id": user_id})

    if existing_user:
        user_collection.update_one({"user_id": user_id}, {
                                   "$set": {"registered": True}})
        user_alredy_reg_msg = await bot.send_message(message.chat.id, "You are already registered. Welcome back!")
        time.sleep(5)
        await user_alredy_reg_msg.delete()
    else:
        user_data = {
            "user_id": user_id,
            "username": message.from_user.username,
            "name": message.from_user.first_name,
            "registered": True
        }
        user_collection.insert_one(user_data)
        user_reg_msg = await bot.send_message(message.chat.id, "You have been registered!")
        time.sleep(5)
        await user_reg_msg.delete()


@bot.on_callback_query()
async def cb_data(bot, message):

    global movieHandler

    if movieHandler:
        bot.remove_handler(movieHandler)
        movieHandler = None

    if message.data == "movie":
        global welcome_msg
        welcome_msg =await message.message.edit_text("**Enter Movie Name :-**")
        movieHandler = bot.add_handler(MessageHandler(movie))
    else:
        pass


bot.run()
