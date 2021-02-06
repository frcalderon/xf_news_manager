import json


class ArticleList:
    def __init__(self, file):
        self.path = './' + file
        self.article_list = []
        self.initialize()

    def initialize(self):
        with open(self.path, 'r') as file:
            data = json.load(file)
            self.article_list = data['articles']

    def serialize(self):
        return {
            'articles': self.article_list
        }

    def add_article(self, article):
        if article['link'] not in [article_in_list['link'] for article_in_list in self.article_list]:
            if len(self.article_list) == 50:
                for article in self.article_list:
                    if article['posted']:
                        self.article_list.remove(article)

            self.article_list.insert(0, article)

    def update(self):
        with open(self.path, 'w') as file:
            json.dump({'articles': self.article_list}, file, ensure_ascii=False, indent=4, separators=(',', ': '))
            """
            try:
                json.dump({'articles': self.article_list}, file, ensure_ascii=False, indent=4, separators=(',', ': '))
            except:
                json.dump({'articles': []}, file, ensure_ascii=False, indent=4, separators=(',', ': '))
            """

    def get_no_posted_articles(self):
        return [article for article in self.article_list if not article['posted']]

    def mark_article_as_posted(self, update):
        for article in self.article_list:
            if article['link'] == update['link']:
                article['posted'] = True
