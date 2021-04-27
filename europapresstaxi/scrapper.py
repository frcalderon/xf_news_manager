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
    def __init__(self, url, file, browser):
        self.url = url
        self.file = file
        self.browser = browser
        self.link_list = []

    def init_link_list(self):
        try:
            elements = self.browser.find_elements_by_css_selector(
                'h2.articulo-titulo a'
            )

            for element in elements:
                self.link_list.append(element.get_attribute('href'))
        except Exception:
            print('An error has ocurred')

    def create_article(self, link):
        try:
            title = self.browser.find_element_by_xpath('//*[@id="ContenedorDocNomral"]/div[2]/div/h1').text
        except Exception:
            title = ''

        try:
            image = self.browser.find_element_by_xpath('//*[@id="fotoPrincipalNoticia"]').get_attribute('src')
        except Exception:
            image = ''

        article_body = ''
        article_body_list = self.browser.find_elements_by_xpath('//*[@id="CuerpoNoticiav2"]')
        if article_body_list:
            article_body = article_body_list[0].get_attribute('innerHTML')
        else:
            article_body_list = self.browser.find_elements_by_xpath('//*[@id="CuerpoNoticia"]')
            if article_body_list:
                article_body = article_body_list[0].get_attribute('innerHTML')
            else:
                article_body_list = self.browser.find_elements_by_xpath('//*[@id="NoticiaPrincipal"]')
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
            'text': f'{text}\n\nFuente: {link}',
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
            self.browser.get(link)
            articles_list.add_article(self.create_article(link))

        articles_list.update()
        return articles_list
