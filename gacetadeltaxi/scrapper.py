import re
from datetime import datetime
from article_list import ArticleList


def clean_input(input_dirty):
    input_splitted = input_dirty.splitlines()

    # Clean invalid tags from input
    input_without_invalid_tags = []
    for num, line in enumerate(input_splitted):
        start_index = line.find('<')
        if (start_index + 1) < len(line) and line[start_index + 1] == '/':
            start_index = line.find('<', start_index + 1)

        space_index = line.find(' ', start_index)
        tag_index = line.find('>', start_index)
        index = min(space_index, tag_index)
        tag = line[start_index:index]

        if any(tag_name in tag for tag_name in ['<p', '<h2', '<span']):
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
                line = line.replace(tag, '[/HEADING]')
            else:
                line = line.replace(tag, '')

        line = line.replace(' / TAMBIÉN ES NOTICIA', '')
        line = line.replace(' /TAMBIÉN ES NOTICIA', '')
        line = line.replace('/TAMBIÉN ES NOTICIA', '')
        line = line.replace(' / [B]TAMBIÉN ES NOTICIA[/B]', '')
        line = line.replace(' /[B]TAMBIÉN ES NOTICIA[/B]', '')
        line = line.replace('/[B]TAMBIÉN ES NOTICIA[/B]', '')

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
        self.link_list = []

    def init_link(self):
        elements = self.browser.find_elements_by_css_selector('div#bloque h2 a')

        for element in elements:
            link = element.get_attribute('href')
            self.link_list.append(link)

    def create_article(self, link):
        title = self.article_browser.find_element_by_xpath('//*[@id="contenido_principal"]/div/div/div[1]/div/h1').text

        image = ''
        image_list = self.article_browser.find_elements_by_xpath(
            '//*[@id="contenido_principal"]/div/div/div[1]/div/p[2]/img'
        )
        if image_list:
            image = image_list[0].get_attribute('src')
        else:
            image_list = self.article_browser.find_elements_by_xpath(
                '//*[@id="contenido_principal"]/div/div/div[1]/div/p[2]/span/span/img'
            )
            if image_list:
                image = image_list[0].get_attribute('src')

        try:
            article_body = self.article_browser.find_element_by_xpath(
                '//*[@id="contenido_principal"]/div/div/div[1]/div'
            ).get_attribute('innerHTML')
        except:
            article_body = ''

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

        self.init_link()

        for index, link in enumerate(self.link_list):
            self.article_browser.get(link)
            articles_list.add_article(self.create_article(link))

        articles_list.update()
        return articles_list
