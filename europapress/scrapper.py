import re
from datetime import datetime
from selenium.common.exceptions import NoSuchElementException
from article_list import ArticleList


def clean_input(input_dirty):

    input_splitted = input_dirty.splitlines()

    # Clean invalid tags from input
    input_without_invalid_tags = []
    for num, line in enumerate(input_splitted):
        start_index = line.find('<')
        space_index = line.find(' ', start_index)
        tag_index = line.find('>', start_index)
        index = min(space_index, tag_index)
        tag = line[start_index:index]

        if any(tag_name in tag for tag_name in ['<p', '<h2']):
            input_without_invalid_tags.append(line)

    pattern = re.compile(r'<.*?>')

    # Generate output
    output = []
    for num, line in enumerate(input_without_invalid_tags):
        line = line.replace('&nbsp;', '')
        line = line.replace('<br>', '')

        for tag in re.findall(pattern, line):
            if '<strong' in tag:
                line = line.replace(tag, '[B]')
            elif '</strong' in tag:
                line = line.replace(tag, '[/B]')
            elif '<b' in tag:
                line = line.replace(tag, '[B]')
            elif '</b' in tag:
                line = line.replace(tag, '[/B]')
            elif '<em' in tag:
                line = line.replace(tag, '[I]')
            elif '</em' in tag:
                line = line.replace(tag, '[/I]')
            elif '<h2' in tag:
                line = line.replace(tag, '[HEADING=2]')
            elif '</h2' in tag:
                line = line.replace(tag, '[/HEADING]\n\n')
            elif '</p' in tag:
                line = line.replace(tag, '\n\n')
            else:
                line = line.replace(tag, '')

        line = line.strip()

        if line:
            output.append(line)

    return '\n\n'.join(output)


class Scrapper:
    def __init__(self, url, file, browser, article_browser):
        self.url = url
        self.file = file
        self.browser = browser
        self.article_browser = article_browser
        self.xpath_list = [
            '//*[@id="ContenidoCentralNoticiasSticky"]/article[2]/div[1]/div/h2/a',
            '//*[@id="ContenidoCentralNoticiasSticky"]/article[3]/div[1]/div/h2/a',
            '//*[@id="ContenidoCentralNoticiasSticky"]/article[4]/div[1]/div/h2/a',
            '//*[@id="ContenidoCentralNoticiasSticky"]/article[5]/div[1]/div/h2/a',
            '//*[@id="ContenidoCentralNoticiasSticky"]/article[6]/div[1]/div/h2/a',
            '//*[@id="ContenidoCentralNoticiasSticky"]/article[7]/div[1]/div/h2/a',
            '//*[@id="ContenidoCentralNoticiasSticky"]/article[8]/div[1]/div/h2/a',
            '//*[@id="ContenidoCentralNoticiasSticky"]/article[9]/div[1]/div/h2/a',
            '//*[@id="ContenidoCentralNoticiasSticky"]/article[10]/div[1]/div/h2/a',
            '//*[@id="ContenidoCentralNoticiasSticky"]/article[11]/div[1]/div/h2/a',
            '//*[@id="ContenidoCentralNoticiasSticky"]/article[12]/div[1]/div/h2/a',
            '//*[@id="ContenidoCentralNoticiasSticky"]/article[13]/div[1]/div/h2/a',
            '//*[@id="ContenidoCentralNoticiasSticky"]/article[14]/div[1]/div/h2/a',
            '//*[@id="ContenidoCentralNoticiasSticky"]/article[15]/div[1]/div/h2/a',
            '//*[@id="ContenidoCentralNoticiasSticky"]/article[16]/div[1]/div/h2/a',
            '//*[@id="ContenidoCentralNoticiasSticky"]/article[17]/div[1]/div/h2/a',
            '//*[@id="ContenidoCentralNoticiasSticky"]/article[18]/div[1]/div/h2/a'
        ]
        self.link_list = []

    def init_link_list(self):
        self.init_link_primary()
        self.init_link_secondary()
        self.init_link_from_xpath_list()

    def init_link_primary(self):
        article_root = self.browser.find_element_by_xpath('//*[@id="ContenidoCentralNoticiasSticky"]')
        article_item = article_root.find_element_by_css_selector(
            'article.primaria div.home-articulo-interior div h2 a'
        )
        link = article_item.get_attribute('href')
        self.link_list.append(link)

    def init_link_secondary(self):
        article_root = self.browser.find_element_by_xpath('//*[@id="aspnetForm"]/div[4]/div[2]/div[1]/div[2]/div')
        article_items = article_root.find_elements_by_css_selector(
            'article.secundaria div.home-articulo-interior div.home-articulo-info h2.articulo-titulo a'
        )
        for item in article_items:
            link = item.get_attribute('href')
            self.link_list.append(link)

    def init_link_from_xpath_list(self):
        for xpath in self.xpath_list:
            article_item = self.browser.find_element_by_xpath(xpath)
            link = article_item.get_attribute('href')
            self.link_list.append(link)

    def create_article(self, link):
        try:
            title = self.article_browser.find_element_by_xpath('//*[@id="ContenedorDocNomral"]/div[2]/div/h1').text
        except NoSuchElementException:
            title = ''

        try:
            image = self.article_browser.find_element_by_xpath('//*[@id="fotoPrincipalNoticia"]').get_attribute('src')
        except NoSuchElementException:
            image = ''

        article_body = ''
        article_body_list = self.article_browser.find_elements_by_xpath('//*[@id="CuerpoNoticiav2"]')
        if article_body_list:
            article_body = article_body_list[0].get_attribute('innerHTML')
        else:
            article_body_list = self.article_browser.find_elements_by_xpath('//*[@id="CuerpoNoticia"]')
            if article_body_list:
                article_body = article_body_list[0].get_attribute('innerHTML')
            else:
                article_body_list = self.article_browser.find_elements_by_xpath('//*[@id="NoticiaPrincipal"]')
                if article_body_list:
                    article_body = article_body_list[0].get_attribute('innerHTML')

        if not (article_body == ''):
            text = clean_input(article_body)
        else:
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

        self.init_link_list()

        for index, link in enumerate(self.link_list):
            self.article_browser.get(link)
            articles_list.add_article(self.create_article(link))

        articles_list.update()
        return articles_list
