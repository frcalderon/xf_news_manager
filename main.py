import sys
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from request import Request
from thread import Thread
from europapress.scrapper import Scrapper as ep_Scrapper
from xataka.scrapper import Scrapper as x_Scrapper
from gacetadeltaxi.scrapper import Scrapper as gt_Scrapper
from electrobuzz.scrapper import Scrapper as eb_Scrapper
from europapresstaxi.scrapper import Scrapper as eptaxi_Scrapper


def main(driver, api, source):
    # print(driver)
    # print(api)
    # print(source)

    print('Config drivers...')

    # Config web driver
    options = Options()
    options.headless = True

    # Init web drivers
    browser = webdriver.Chrome(executable_path=driver, options=options)
    article_browser = webdriver.Chrome(executable_path=driver, options=options)

    print('Getting articles and publishing in forum...')

    # Init Scrapper with URL and path
    for category_source in source['categories']:
        # print(category_source)

        print('\tURL: ' + category_source['url'])

        scrapper = None

        if category_source['scrapper'] == 'europapress':
            scrapper = ep_Scrapper(category_source['url'], category_source['file'], browser)
        elif category_source['scrapper'] == 'xataka':
            scrapper = x_Scrapper(category_source['url'], category_source['file'], browser, article_browser)
        elif category_source['scrapper'] == 'gacetadeltaxi':
            scrapper = gt_Scrapper(category_source['url'], category_source['file'], browser, article_browser)
        elif category_source['scrapper'] == 'electrobuzz':
            scrapper = eb_Scrapper(category_source['url'], category_source['file'], browser)
        elif category_source['scrapper'] == 'europapress-taxi':
            scrapper = eptaxi_Scrapper(category_source['url'], category_source['file'], browser)

        if scrapper is not None:
            article_list = scrapper.get_articles()
            
            # Get no posted articles from article list
            no_posted_articles = article_list.get_no_posted_articles()
            
            # Loop through all articles in no posted articles list
            for article in no_posted_articles:
                # Convert articles to threads with template
                thread = Thread(article)
                data = thread.convert_article_to_thread(category_source)

                # Init request with config and data to send
                request = Request(api, data)

                # Send POST request to create thread
                if request.send_request():
                    # If response is 200 OK mark article as posted
                    article_list.mark_article_as_posted(article)
            
            # Update articles.json
            article_list.update()
            
            print('\tFinished!')
        else:
            print('\tScrapper could not be initialized!')


if __name__ == "__main__":
    # Get first argument as source
    source_argument = sys.argv[1]

    # Get config from config.json
    with open('config.json', 'r') as file:
        config = json.load(file)

    # Init configs
    driver_config = config['system']['windows']
    source_config = config[source_argument]
    api_config = source_config['api']

    main(driver_config, api_config, source_config)
