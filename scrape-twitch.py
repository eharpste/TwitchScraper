import argparse
import os
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup


def scrape_data(pages=10, sleepTime=10, dump=False):
    print('SCRAPING DATA')
    print('You should see an incognito Chrome window appear. Be sure to click on and'
          'focus that window while the scraping process is running. Please do not do'
          'anything else your computer until the scrape is complete.')

    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--incognito')
    # options.add_argument('--headless')
    driver = webdriver.Chrome(
        "C:/Users/Erik/Downloads/chromedriver_win32/chromedriver", options=options)
    driver.implicitly_wait(sleepTime)

    driver.get("https://www.twitch.tv/directory")

    stamp = datetime.now()

    cards = []
    body = driver.find_element_by_tag_name('body')

    for i in range(pages):
        body.send_keys(Keys.PAGE_DOWN)
        body.send_keys(Keys.PAGE_DOWN)
        body.send_keys(Keys.PAGE_DOWN)
        time.sleep(sleepTime)
        cards = driver.find_elements_by_class_name("tw-box-art-card")

        print("Page:", i, "Cards:", len(cards))

    page_source = driver.page_source

    if dump:
        d_name = 'DUMP' + \
            datetime.strftime(stamp, '%Y-%m-%d %H-%M-%S') + '.html'
        with open(d_name, 'w') as out_F:
            out_F.write(page_source)

    driver.close()

    return page_source, stamp


def load_old(f_name):
    print('LOADING OLD DUMP')
    with open(f_name, 'r') as in_f:
        text = in_f.read()
        stamp = datetime.fromtimestamp(os.path.getctime(in_f))
        return text, stamp


def parse_page(page_source):
    print('PARSING PAGE')
    soup = BeautifulSoup(page_source, 'lxml')

    games = []
    games_selector = soup.find_all('div', class_='tw-box-art-card')

    for game_sel in games_selector:
        name = game_sel.find('h3').string
        views = game_sel.find('p', class_='tw-c-text-alt-2').string.split()[0]
        if views[-1] == 'M':
            views = int(float(views[:-1]) * 1000000)
        elif views[-1] == 'K':
            views = int(float(views[:-1]) * 1000)
        else:
            views = int(views)

        tags = [ele.string for ele in game_sel.find_all(
            'div', class_='tw-tag__content')]

        game = {'title': name,
                'viewers': views,
                'tags': tags}
        games.append(game)

    return games


def output_tsv(games, stamp):
    print('OUTPUTTING FILE')
    f_name = 'Sample_' + datetime.strftime(stamp, '%Y-%m-%d %H-%M-%S') + '.tsv'
    print('Data available in:', f_name)

    all_tags = set()
    for g in games:
        all_tags.update(g['tags'])

    all_tags = list(all_tags)
    all_tags.sort()

    header = ['title', 'viewers', 'sample.time',
              'main.tag', 'appended.tags', 'num.tags'] + all_tags

    with open(f_name, 'w') as out_f:
        out_f. write('\t'.join(header))

        for g in games:
            row = [g['title'], str(g['viewers']),
                   datetime.strftime(stamp, '%Y-%m-%d %H:%M:%S'),
                   g['tags'][0] if len(g['tags']) > 0 else '',
                   ','.join(g['tags']), str(len(g['tags']))]

            row += ['1' if t in g['tags'] else '0' for t in all_tags]
            out_f.write('\n' + '\t'.join(row))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='This is a script for point sampling the'
                                     'current most popular game categories on Twitch.tv'
                                     'by loading up the category directory page and'
                                     'scraping the page using Selenium.')

    parser.add_argument('-pages', type=int, default=10,
                        help="The number of times to page down the directory page to"
                        "dynamically load more content")
    parser.add_argument('-sleepTime', type=int, default=10,
                        help="The number of seconds to wait between pages to allow for"
                        "more content to load in")
    parser.add_argument('-dump', action='store_true',
                        help="Whether to dump the html data from paging for further"
                        "analysis or formatting")
    parser.add_argument('-load_from', type=str, default=None,
                        help="An existing html dump to create a tsv file from instead of"
                        "pulling new data from the web. Note that the sample time will be"
                        " assumed to be creation time of the dump file.")

    args = parser.parse_args()

    if args.load_from is not None:
        page_source, stamp = load_old(args.load_from)
    else:
        page_source, stamp = scrape_data(args.pages, args.sleepTime, args.dump)

    games = parse_page(page_source)
    output_tsv(games, stamp)
