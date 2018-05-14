import configparser
import csv

from src.web_monitor import web_monitor


def read_config():
    config = configparser.ConfigParser()
    config.read('config.ini')
    #config.add_section('url_content')
    with open("websites.txt", "r") as web_config:
        tsv_reader = csv.DictReader(web_config, delimiter='\t')
        web_dict = {}
        for row in tsv_reader:
            web_dict[row['website']] = row['content_file']

    config['url_content'] = web_dict
    return config


def main():
    config = read_config()
    web_monitor.main(config)


if __name__ == '__main__':
    main()
