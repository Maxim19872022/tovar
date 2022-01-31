from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import telebot
from telebot import types
from aiogram import types
import time
import os
import re
import requests
import zipfile
from multiprocessing import *
import schedule

users = {}
bot = telebot.TeleBot('1996841383:AAGPGqKYEbJydjwCs5UbdzGVcdgdteC5PEE')
bot2 = telebot.TeleBot('5006738865:AAEHeK674HD23VpGmu_MC35og7QNYjaGb1A')
global soup_op,r,z,p,l,id_kye,id_s,id_call

XML_INFO_URL = 'https://chromedriver.storage.googleapis.com/LATEST_RELEASE_'
DRIVER_PATH = 'https://chromedriver.storage.googleapis.com'
ZIPPED_DRIVER_FILE_NAME = 'chromedriver_linux64.zip'
UNZIPPED_DRIVER_FILE_NAME = 'chromedriver'
PATH_TO_CHROMEDRIVER = '.'


def start_process():
    p1 = Process(target=start_schedule, args=()).start()


def start_schedule():
    schedule.every().day.at("14:08").do(chrome_new)
    while True:
        schedule.run_pending()
        time.sleep(1)


def chrome_new():
    driver_file_url = DRIVER_PATH + '/' + get_driver_latest_version(get_browser_major_version()) + '/' + ZIPPED_DRIVER_FILE_NAME
    download_file(driver_file_url, ZIPPED_DRIVER_FILE_NAME)
    print('скачено')
    with zipfile.ZipFile(ZIPPED_DRIVER_FILE_NAME, 'r') as zip_ref:
        zip_ref.extractall(PATH_TO_CHROMEDRIVER)
        os.chmod(PATH_TO_CHROMEDRIVER + '/' + UNZIPPED_DRIVER_FILE_NAME, 0o744)
        os.remove(ZIPPED_DRIVER_FILE_NAME)
    print('rename')

@bot.message_handler(commands=['start'])
def start_command(message):
    bot.send_message(message.chat.id,'Здравствуйте! Этот бот выполняет поиск товара для сравнения цен по интернет магазинам. '
                                     '\n (Пример поиска - IPhone 12 64 ГБ синий)'
                                     '\n *Введите наименование товара:*',parse_mode='Markdown')
    user_id = str(message.from_user.id)
    last_name = str(message.from_user.last_name)
    first_name = str(message.from_user.first_name)
    user_name = str(message.from_user.username)
    print(last_name+' '+first_name+' '+user_name)
    file = open('id.txt','r+')
    read_file = file.read()
    c = read_file.count(user_id)
    if c == 0:
        file.write(user_id+' '+last_name+' '+first_name+' '+user_name)
        file.write('\n')
        file.close()

@bot.message_handler(commands=['send'])
def start_command(message):
    if message.chat.id == 733671309:
        msg = bot.send_message(message.chat.id,'Введите текст')
        bot.register_next_step_handler(msg,send)
def send (message):
    file = open('id.txt', 'r')
    read_file = file.read()
    id_ = re.findall(r'\d+',read_file)
    j = int(len(id_))
    file.close()
    print(j)
    for c in range(0,j-1):
        bot.send_message(chat_id= id_[c],text=message.text)

@bot.message_handler(commands=['id'])
def start_command(message):
    if message.chat.id == 733671309:
        id_len = len(re.findall(r"[\n']+", open('id.txt').read()))
        bot.send_message(message.chat.id, 'Количество подписанных на бота: ' + str(id_len))
    else:
        bot.send_message(message.chat.id, 'У вас нет доступа')


def get_browser_major_version():
    stream = os.popen('google-chrome --version')
    output = stream.read()
    print(output)
    version_info_str = re.search(r'\d+\.\d+\.\d+', output).group(0)
    return re.search(r'^\d+', version_info_str).group(0)


def get_driver_latest_version(browser_major_version):
    return requests.get(XML_INFO_URL + browser_major_version).text


def download_file(url, file_name):
    file = requests.get(url)
    with open(file_name, "wb") as code:
        code.write(file.content)



@bot.message_handler(content_types=['text'])
def start_message(message: types.Message):
            global id_,soup_op, r, z, p, l, id_kye,cid
            j = 0
            cid = message.chat.id
            slovo = message.text
            slovo_w = str(slovo.replace(' ', '+'))
            katalog_url = 'https://www.e-katalog.ru/ek-list.php?search_='+slovo_w
            driver = ChromeDriverManager().install()
            driver = webdriver.Chrome(driver)
            driver.get(katalog_url)
            time.sleep(3)
            sours_e = driver.page_source
            driver.close()
            soup = BeautifulSoup(sours_e, 'html.parser')
            soup_op = soup.findAll('form',id='list_form1')
            spisok_id_dir = []
            id_ = []
            id_kye = []
            id_call = []
            if soup_op != []:
                for span in soup_op:
                    id_dir = re.findall(r'\b[mr_]\w+',str(span))
                    for i in range(0,len(id_dir)):
                        len_w = len(id_dir[i])
                        if len_w == 14:
                            spisok_id_dir.append(id_dir[i])
                    print(spisok_id_dir)
                    print(list(set(spisok_id_dir)))
                    dir_id = span.find_all_next('div',class_='model-short-div list-item--goods')
                    j = 0
                    for span_title in dir_id:
                        if j != 6:
                            span_title_ = span_title.find_next('a', class_='model-short-title no-u')
                            title_ = span_title_.get('title')
                            id_.append(str(j)+span_title_.get('id'))
                            span_sale = span_title.find_next('td',class_='model-hot-prices-td')
                            span_sale_td = span_sale.find_next('div',class_='model-price-range')
                            print(span_sale_td.text.split('.',1)[0])
                            print('ok',title_)
                            print(id_)
                            mainmenu = types.InlineKeyboardMarkup()
                            key = types.InlineKeyboardButton(text=str(span_sale_td.text.split('.',1)[0]), callback_data=id_[j])
                            print(key.callback_data)
                            mainmenu.add(key)
                            bot_id_call = bot.send_message(message.chat.id,'*'+title_+'*', reply_markup=mainmenu, parse_mode='Markdown')
                            bot_id_kye = bot.send_message(message.chat.id,'----------------------------------------------------', parse_mode='Markdown')
                            z = bot_id_kye.message_id
                            q = bot_id_call.message_id
                            id_call.append(q)
                            id_kye.append(z)
                            j = j+1
                            print(id_kye)
                        else: break
            else:
                bot.send_message(message.chat.id, '*Товар не найден, попробуйте изменить название товара*', parse_mode='Markdown')
@bot.callback_query_handler(func=lambda call: True)
def answer_f(call:types.CallbackQuery):
    r = []
    l = 0
    global id_s

    for l in range(0,len(id_)):
        if call.data == id_[l]:
            print('id_',id_[l])
            id_new = str(id_[l]).split('_',1)[1]
            id_s = int(str(id_[l]).split('p',1)[0])
            print('айди id_s',id_s)
            for magaz in soup_op:
                magaz_ = magaz.find_all_next('td', class_ = 'model-shop-name')
                for d in magaz_:
                    c = d.find_next('a')
                    e = c.get('onclick')
                    onclic = e.find(id_new)
                    if onclic > -1:
                        p = c.text+c.find_next('a').text+'\n'
                        spisok = re.sub('(?<=\().+?(?=\))', '', p)
                        spisok = spisok.replace('(','')
                        spisok = spisok.replace(')', '')
                        href = c.get('onmouseover')
                        h = href[href.find('"') + 1:-1].split('"')[0]
                        r.append('[' + spisok + ']'+'('+h+')')
                        print('r',r)
    vivod = ''.join(r)
    print('id_key',id_kye[id_s])
    print('vivod',vivod)
    bot.edit_message_text(chat_id=cid,message_id=int(id_kye[id_s]),disable_web_page_preview=True,text='---------------------------------------------\n'+vivod+'\n---------------------------------------------',parse_mode='Markdown')


if __name__ == '__main__':
    while True:
        try:
            start_process()
            bot.polling(none_stop=True)
        except Exception as e:
            print(e)
            time.sleep(10)
