import csv
import requests
from bs4 import BeautifulSoup as BS
from time import sleep
from random import randrange
import json
from selenium import webdriver
import selenium.common.exceptions as exc
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium_stealth import stealth

options = webdriver.ChromeOptions()
options.add_argument("start-maximized")

# options.add_argument("--headless")

options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
driver = webdriver.Chrome(options=options)

stealth(driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
        )

headers = {
    'Accept': '*/*',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0'
}


def get_artictles_urls(url):
    with requests.Session() as session:
        response = session.get(url=url, headers=headers)

        with open('index.html', 'w', encoding='utf-8') as file:
            file.write(response.text)

        articles_urls_list = []

    with requests.Session() as session:
        page = 0
        while True:
            page += 1
            response = session.get(f'https://announcements.bybit.com/en-US/?category=&page={page}', headers=headers)
            soup = BS(response.text, 'lxml')
            articles_urls = soup.find_all('a', class_='no-style')
            if (len(articles_urls)):
                for au in articles_urls:
                    art_url = au.get('href')
                    articles_urls_list.append(str(art_url))
            else:
                break

            # time.sleep(randrange(2, 5))

            print(f'Обработал {page}')

    with open('articles_urls.txt', 'w', encoding='utf-8') as file:
        for url in articles_urls_list:
            file.write(f'https://announcements.bybit.com{url}\n')

    print('Обработка законченна')
    return True


def get_data(file_path):
    with open(file_path) as file:
        urls_list = [line.strip() for line in file.readlines()]

    for url in urls_list:
        to_write = []
        driver.get(url)
        article_title = driver.find_element(By.CLASS_NAME, 'article-detail-title').text
        article_time = driver.find_element(By.CLASS_NAME, 'article-detail-date').text
        to_write.append(url)
        to_write.append(article_title)
        to_write.append(article_time)
        with open('data.csv', 'a', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(to_write)


def main():
    '''Получение всех ссылок(1 раз)'''

    #get_artictles_urls(url='https://announcements.bybit.com/en-US/?category=&page=1')

    '''Получение информации со всех ссылок'''

    if get_artictles_urls(url='https://announcements.bybit.com/en-US/?category=&page=1') is True:
        get_data('articles_urls.txt')

    '''Постоянный парсинг'''

    try:
        while True:
            if uniq_check(check()) is False:
                append_to_list(check())
                print('Добавлена новость')

            sleep(1)

    except Exception as ex:
        print(f'Что-то пошло не так {ex}')


def check():
    with requests.Session() as session:
        response = session.get(f'https://announcements.bybit.com/en-US/?category=&page=1', headers=headers)
        soup = BS(response.text, 'lxml')
        article_urls = soup.find('a', class_='no-style')
        art_url = article_urls.get('href')
        return 'https://announcements.bybit.com' + art_url


def uniq_check(url):
    with open('articles_urls.txt', 'r', encoding='utf-8') as file:
        for line in file:
            if url in line:
                return True
        else:
            return False


def append_to_list(url):
    with open('articles_urls.txt', 'a', encoding='utf-8') as file:
        file.write(f'https://announcements.bybit.com{url}\n')
    to_write = []
    driver.get(url)
    article_title = driver.find_element(By.CLASS_NAME, 'article-detail-title').text
    article_time = driver.find_element(By.CLASS_NAME, 'article-detail-date').text
    to_write.append(url)
    to_write.append(article_title)
    to_write.append(article_time)
    with open('data.csv', 'a', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(to_write)


if __name__ == '__main__':
    main()
    driver.quit()
