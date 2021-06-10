import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from article_list import ArticleList

class Scrapper:
    def __init__(self, url, file, browser):
        self.url = url
        self.file = file
        self.browser = browser

    def init_link(self):
        links = []

        try:
            elements = self.browser.find_elements_by_css_selector(
                'div#content div#primary div.g1-collection div.g1-collection-viewport ul.g1-collection-items li.g1-collection-item article div.entry-body header h3.entry-title a'
            )

            for element in elements:
                links.append(element.get_attribute('href'))
        except Exception:
            print('An error has ocurred')
        
        return links

    def create_article(self, link):
        title = ''
        image = ''
        playlist = []
        download_link = ''

        try:
            title = self.browser.find_element_by_css_selector('h1.entry-title').text
        except Exception:
            print('An error has ocurred')
        
        try:
            image = self.browser.find_element_by_css_selector('div.entry-content p img').get_attribute('src')
        except Exception:
            print('An error has ocurred')
        
        try:
            playlist = self.browser.find_elements_by_css_selector('div.entry-content ol li')
        except Exception:
            print('An error has ocurred')
        
        try:
            download_link = self.browser.find_element_by_css_selector('div.entry-content div.well a').get_attribute('href')
        except Exception:
            print('An error has ocurred')
        
        text = ''

        for index, song in enumerate(playlist):
            text = f'{text}{(index + 1)}. {song.text}\n'

        if download_link:
            text = f'{text}\n Download: {download_link} \n\n (For reupload , please reply and tag DjCyry)' 
        
        article = {
            'link': link,
            'title': f'{title.encode("cp850", "replace").decode("cp850")}',
            'image': image,
            'text': f'{text.encode("cp850", "replace").decode("cp850")}',
            'date': datetime.now().strftime("%d/%m/%Y-%H:%M:%S"),
            'posted': False
        }

        return article
    
    def get_articles(self):
        articles_list = ArticleList(self.file)
        articles_list.initialize()

        self.browser.get(self.url)

        links = self.init_link()

        for index, link in enumerate(links):
            self.browser.get(link)
            time.sleep(0.5)
            articles_list.add_article(self.create_article(link))
        
        articles_list.update()
        return articles_list
