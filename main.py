from dotenv import load_dotenv
from time import sleep
from threading import Thread

import schedule
import requests
from os import getenv
from telebot import TeleBot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator

load_dotenv()

BOT_TOKEN = getenv("TOKEN")
MY_URL = 'https://www.kw.ac.kr/ko/life/notice.jsp?srCategoryId=&mode=list&searchKey=1&searchVal='

bot = TeleBot(token=BOT_TOKEN)
translator = GoogleTranslator(target="ru")


@bot.message_handler(commands=["start"])
def cmd_start(message):
    with open("users.txt", "a") as file:
        user_id = message.from_user.id
        user_name = f"{message.from_user.first_name} {
            message.from_user.last_name}"
        file.write(f"{user_id}, {user_name}\n")


@bot.message_handler(commands=["send"])
def send_info(message):
    with open("users.txt", "r") as file:
        for line in file.readlines():
            id, name = line.split(", ")
            bot.send_message(id, f"Hello, {name}!")


def fetch_data(url):
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(response.text, "html.parser")
    list_elements = soup.find_all("div", class_="board-text")

    data = []

    for element in list_elements:
        text = (
            element.find("a")
            .get_text()
            .strip()
            .replace("Attachment", "")
            .replace("\n", "")
            .replace(" ", "")
        )

        link = element.find("a").get("href")
        data = element.find("p").get.text().split("|")[2][5:].strip()

        data.append((text, "https://www.kw.ac.kr" + link))

    return data


def main():
    news = fetch_data(MY_URL)
    for news_for_foreigners in news:
        if "외국인" in news_for_foreigners[0]:
            translated_news = translator.translate(news_for_foreigners[0])

            kb = InlineKeyboardMarkup()
            kb.add(InlineKeyboardButton("Click", url=news_for_foreigners[1]))

            with open("users.txt", "r") as file:
                for line in file.readlines():
                    id, name = line.split(",")
                    bot.send_message(id, translated_news, reply_markup=kb)


def run_schedule():
    schedule.every().day.at("00:00").do(main)
    schedule.every(1).hours.do(main)

    while True:
        schedule.run_pending()
        sleep(1)


Thread(target=run_schedule).start()
bot.infinity_polling()
