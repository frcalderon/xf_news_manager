class Thread:
    def __init__(self, article):
        self.article = article

    def convert_article_to_thread(self, source):
        message = """
        [IMG width="500px"]%(image)s[/IMG]
        
        %(text)s
        """ % {'image': self.article['image'], 'text': self.article['text']}

        return {
            'node_id': source['category'],
            'title': self.article['title'],
            'message': message,
            'tags': source['tags'],
            'discussion_open': 1
        }
