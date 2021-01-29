from datetime import datetime


class Article:
    def __init__(self, link, image, text, posted):
        self.link = link
        self.image = image
        self.text = text
        self.date = datetime.now().strftime("%d/%m/%Y-%H:%M:%S"),
        self.posted = posted

    def serialize(self):
        return {
            'link': self.link,
            'image': self.image,
            'text': self.text,
            'date': self.date,
            'posted': self.posted
        }
