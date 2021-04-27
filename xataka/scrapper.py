import re
from datetime import datetime
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
                line = line.replace(tag, '[/HEADING]')
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
        self.link_list = []

    def init_link_from_xpath_list(self):
        first_link = self.browser.find_element_by_css_selector('h2.poster-title a').get_attribute('href')
        if 'https://www.xataka.com/' in first_link:
            self.link_list.append(first_link)

        elements = self.browser.find_elements_by_css_selector('h2.abstract-title a')
        for element in elements:
            link = element.get_attribute('href')
            if 'https://www.xataka.com/' in link:
                self.link_list.append(link)

        """
        for xpath in self.xpath_list:
            article_item = self.browser.find_element_by_xpath(xpath)
            link = article_item.get_attribute('href')
            if 'https://www.xataka.com/' in link:
                self.link_list.append(link)
        """

    def create_article(self, link):
        title = self.article_browser.find_element_by_css_selector('h1 span').text

        image = ''
        image_list = self.article_browser.find_elements_by_xpath(
            '/html/body/div[2]/div/div[3]/div/main/article/div/div[1]/div[1]/header/div[1]/img'
        )
        if image_list:
            image = image_list[0].get_attribute('src')
        else:
            image_list = self.article_browser.find_elements_by_xpath(
                    '/html/body/div[2]/div/div[3]/div/main/article/div[2]/div[1]/div[1]/header/div/div[1]/img'
                )
            if image_list:
                image = image_list[0].get_attribute('src')
            else:
                image_list = self.article_browser.find_elements_by_xpath(
                    '/html/body/div[2]/div/div[2]/div/main/article/div[2]/div[1]/div[1]/header/div/div[1]/img'
                )
                if image_list:
                    image = image_list[0].get_attribute('src')
                else:
                    image_list = self.article_browser.find_elements_by_xpath(
                        '/html/body/div[2]/div/div[3]/div/main/article/div[3]/div[1]/div[1]/header/div/div[1]/img'
                    )
                    if image_list:
                        image = image_list[0].get_attribute('src')

        try:
            article_body = self.article_browser.find_element_by_css_selector('div.blob.js-post-images-container')\
                .get_attribute('innerHTML')
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
            'text': f'{text.encode("cp850", "replace").decode("cp850")}\n\nFuente: {link}',
            'date': datetime.now().strftime("%d/%m/%Y-%H:%M:%S"),
            'posted': False
        }

        return article

    def get_articles(self):
        articles_list = ArticleList(self.file)
        articles_list.initialize()

        self.browser.get(self.url)

        self.init_link_from_xpath_list()
        
        for index, link in enumerate(self.link_list):
            self.article_browser.get(link)
            articles_list.add_article(self.create_article(link))

        articles_list.update()
        return articles_list
