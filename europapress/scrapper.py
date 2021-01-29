from datetime import datetime
from selenium.common.exceptions import NoSuchElementException
from article_list import ArticleList


def clean_article(article_body):
    text = ''
    article_body_clean = []
    article_body_split = article_body.splitlines()
    for line in article_body_split:
        if line and all(text not in line for text in
                        ['EUROPA PRESS', '<div>', '</div>', '<!--', '-->', '<script', '</script>']):
            line = line.replace('<p>', '')
            line = line.replace('</p>', '')
            line = line.replace('<em>', '[I]')
            line = line.replace('</em>', '[/I]')
            line = line.replace('<h2>', '[HEADING=2]')
            line = line.replace('<h2 class=\"ladillo\">', '[HEADING=2]')
            line = line.replace('</h2>', '[/HEADING]')
            line = line.replace('<b>', '[B]')
            line = line.replace('</b>', '[/B]')
            line = line.replace('<strong>', '[B]')
            line = line.replace('</strong>', '[/B]')
            line = line.replace('<br>', '')
            line = line.strip()
            line += '\n\n'
            article_body_clean.append(line)

    for line_clean in article_body_clean:
        text = text + line_clean

    return text


class Scrapper:
    def __init__(self, url, file, browser, article_browser):
        self.url = url
        self.file = file
        self.browser = browser
        self.article_browser = article_browser
        self.xpath_list = [
            '//*[@id="ContenidoCentralNoticiasSticky"]/article[1]/div/div/h2/a',
            '//*[@id="ContenidoCentralNoticiasSticky"]/article[2]/div/div/h2/a',
            '//*[@id="ContenidoCentralNoticiasSticky"]/article[3]/div/div/h2/a',
            '//*[@id="ContenidoCentralNoticiasSticky"]/article[4]/div/div/h2/a',
            '//*[@id="ContenidoCentralNoticiasSticky"]/article[5]/div/div/h2/a',
            '//*[@id="ContenidoCentralNoticiasSticky"]/article[6]/div/div/h2/a',
            '//*[@id="ContenidoCentralNoticiasSticky"]/article[7]/div/div/h2/a',
            '//*[@id="ContenidoCentralNoticiasSticky"]/article[8]/div/div/h2/a',
            '//*[@id="ContenidoCentralNoticiasSticky"]/article[9]/div/div/h2/a',
            '//*[@id="ContenidoCentralNoticiasSticky"]/article[10]/div/div/h2/a',
            '//*[@id="ContenidoCentralNoticiasSticky"]/article[11]/div/div/h2/a',
            '//*[@id="ContenidoCentralNoticiasSticky"]/article[12]/div/div/h2/a',
            '//*[@id="ContenidoCentralNoticiasSticky"]/article[13]/div/div/h2/a',
            '//*[@id="ContenidoCentralNoticiasSticky"]/article[14]/div/div/h2/a',
            '//*[@id="ContenidoCentralNoticiasSticky"]/article[15]/div/div/h2/a',
            '//*[@id="ContenidoCentralNoticiasSticky"]/article[16]/div/div/h2/a',
            '//*[@id="ContenidoCentralNoticiasSticky"]/article[17]/div/div/h2/a'
        ]

    def get_article_from_primary_article(self):
        article_root = self.browser.find_element_by_xpath('//*[@id="aspnetForm"]/div[4]/div[1]/div[2]')
        article_item = article_root.find_element_by_css_selector(
            'article.primaria div.home-articulo-interior h2.titulo-principal a'
        )
        link = article_item.get_attribute('href')
        self.article_browser.get(link)

        article = self.create_article(link)
        return article

    def get_articles_from_secondary_articles(self):
        articles = []

        article_root = self.browser.find_element_by_xpath('//*[@id="aspnetForm"]/div[4]/div[1]/div[2]')
        article_items = article_root.find_elements_by_css_selector(
            'article.secundaria div.home-articulo-interior div.home-articulo-info h2.articulo-titulo a'
        )
        for item in article_items:
            link = item.get_attribute('href')
            self.article_browser.get(link)
            articles.append(self.create_article(link))

        return articles

    def get_article_from_xpath(self, xpath):
        article_item = self.browser.find_element_by_xpath(xpath)
        link = article_item.get_attribute('href')
        self.article_browser.get(link)

        article = self.create_article(link)
        return article

    def create_article(self, link):
        title = self.article_browser.find_element_by_xpath('//*[@id="ContenedorDocNomral"]/div[2]/div/h1').text

        try:
            image = self.article_browser.find_element_by_xpath('//*[@id="fotoPrincipalNoticia"]').get_attribute('src')
        except NoSuchElementException:
            image = ''

        try:
            article_body = self.article_browser.find_element_by_xpath('//*[@id="CuerpoNoticiav2"]').get_attribute(
                'innerHTML')
            text = clean_article(article_body)
        except NoSuchElementException:
            try:
                article_body = self.article_browser.find_element_by_xpath('//*[@id="CuerpoNoticia"]').get_attribute(
                    'innerHTML')
                text = clean_article(article_body)
            except NoSuchElementException:
                text = ''

        article = {
            'link': link,
            'title': title,
            'image': image,
            'text': text,
            'date': datetime.now().strftime("%d/%m/%Y-%H:%M:%S"),
            'posted': False
        }

        return article

    def get_articles(self):
        articles_list = ArticleList(self.file)
        articles_list.initialize()

        self.browser.get(self.url)

        articles_list.add_article(self.get_article_from_primary_article())

        for article in self.get_articles_from_secondary_articles():
            articles_list.add_article(article)

        for xpath in self.xpath_list:
            articles_list.add_article(self.get_article_from_xpath(xpath))

        articles_list.update()
        return articles_list
