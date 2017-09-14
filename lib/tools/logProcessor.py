#!/usr/bin/env python

import os
import re
import datetime

from decimal import Decimal

from udger import Udger

class LogProcessor:
    """
    Prepare data for learning
    """

    def __init__(self, source_log, formatted_log_dir, filter_crawlers=True):
        """
        :param source_log: Source log file
        :param formatted_log: formatted log file
        :param filter_crawlers: Use crawler filter udger.com
        """
        self.__source_log = source_log
        self.__formatted_log_dir = formatted_log_dir

        data_dir = os.path.join(os.path.dirname(__file__), '../parsers/udger-data')
        self.__udger = Udger(data_dir) if filter_crawlers else None

    def __is_crawler(self, client_ip, client_ua):

        bots_ua_family = {
            # Search engine or antivirus or SEO bots
            'googlebot',
            'siteexplorer',
            'sputnikbot',
            'bingbot',
            'mj12bot',
            'yandexbot',
            'cliqzbot',
            'avast_safezone',
            'megaindex',
            'genieo_web_filter',
            'uptimebot',
            'ahrefsbot',
            'wordpress_pingback',
            'admantx_platform_semantic_analyzer',
            'leikibot',
            'mnogosearch',
            'safednsbot',
            'easybib_autocite',
            'sogou_spider',
            'surveybot',
            'baiduspider',
            'indy_library',
            'mail-ru_bot',
            'pocketparser',
            'virustotal',
            'feedfetcher_google',
            'virusdie_crawler',
            'surdotlybot',
            'yoozbot',
            'facebookbot',
            'linkdexbot',
            'prlog',
            'thinglink_imagebot',
            'obot',
            'spyonweb',
            'easybib_autocite',
            'avira_crawler',
            'pulsepoint_xt3_web_scraper',
            'comodospider',
            'girafabot',
            'avira_scout',
            'salesintelligent',
            'kaspersky_bot',
            'xenu',
            'maxpointcrawler',
            'seznambot',
            'magpie-crawler',
            'yesupbot',
            'startmebot',
            'brandprotect_bot',
            'ask_jeeves-teoma',
            'duckduckgo_app',
            'linqiabot',
            'flipboardbot',
            'cat_explorador',
            'huaweisymantecspider',
            'coccocbot',

            # I think next is potencial bad bot (framework for apps or bad crowler)
            'grapeshotcrawler',
            'netestate_crawler',
            'ccbot',
            'plukkie',
            'metauri',
            'silk',
            'phantomjs',
            'python-requests',
            'okhttp',
            'python-urllib',
            'netcraft_crawler',
            'go_http_package',
            'google_app',
            'android_httpurlconnection',
            'curl',
            'w3m',
            'wget',
            'getintentcrawler',
            'scrapy',
            'crawler4j',
            'apache-httpclient',
            'feedparser',
            'php',
            'simplepie',
            'lwp::simple',
            'libwww-perl',
            'apache_synapse',
            'scrapy_redis',
            'winhttp',
            'johnhew_crawler',
            'poe-component-client-http',
            'joc_web_spider',
            'java',
            'www::mechanize',
            'powermarks', 
            'prism', 
            'leechcraft', 
            'wkhtmltopdf',

            #Text Browsers
            'elinks',
            'links',
            'lynx'
        }

        ua_c = self.__udger.parse_ua(client_ua)

        if ((self.__udger.parse_ip(client_ip)['ip_classification_code'] == 'crawler') or
                (ua_c['ua_class_code'] == 'crawler') or (ua_c['ua_family_code'] in bots_ua_family)):
            return True
        else:
            return False

    @staticmethod
    def __carefool_split(s):
        splitted = s.split(': ', 1)
        if len(splitted) < 2:
            splitted.append("")
        splitted[1] = splitted[1].rstrip()
        return splitted

    def __single_log_handler(self, lines, ip):
        timestamp = 0

        json = dict(self.__carefool_split(s) for s in lines[1:])
        if 'host' in json:
            if json['host'].strip == ('servicer.adskeeper.co.uk' or 'servicer.traffic-media.co.uk'):
                return False
        if 'Host' in json:
            if json['Host'].strip == ('servicer.adskeeper.co.uk' or 'servicer.traffic-media.co.uk'):
                return False
#        ip = json['HTTP_X_REAL_IP'][:-1] if 'HTTP_X_REAL_IP' in json else json['X-Real-IP'][:-1]
        if 'user-agent' in json:
            json['User-Agent'] = json.pop('user-agent')
        if 'User-Agent' not in json:
            return False
        if not self.__udger is None:
            if self.__is_crawler(ip, json['User-Agent']):
                return False
#        if 'accept' in json:
#            json['Accept'] = json.pop('accept')
#        if 'accept-encoding' in json:
#            json['Accept-Encoding'] = json.pop('accept-encoding')
#        if 'accept-charset' in json:
#            json['Accept-Charset'] = json.pop('accept-charset')

        return "{},{},\'{}\'\n".format(timestamp, ip, json)

    def reformat_train_sample(self):
        """
        Entry point
        """
        print('Started formatting {}'.format(datetime.datetime.now().time()))
        with open(self.__source_log) as infile:
            single_log = []
            writed_log_counter = 0
            platform = None
            ip = None
            for line in infile:
                if line and line.strip():
                    if '.00080' not in line and '.00443' not in line and ': ' in line:
                        single_log.append(line)
                    elif '.00080: GET /' in line:
                        platform = line.split('.00080: GET /', 1)[1].split('/', 1)[0].split('?', 1)[0]
                        if not platform[1:].isdigit():  # 'uXXXX' is compatible
                            platform = None
                        ip = '.'.join(str(int(part)) for part in line[:15].split('.'))
                        #print("platform: " + platform)
                        #print(platform.isdigit())
                        #print("ip: " + ip)
                else:
                    if single_log and ip:
                        result = self.__single_log_handler(single_log, ip)
                        single_log = []
                        ip = None
                        if result and platform:
                            platform_dir = os.path.join(self.__formatted_log_dir, str(platform)[:2])
                            if not os.path.exists(platform_dir):
                                os.makedirs(platform_dir)
                            open(os.path.join(platform_dir, platform + '.formatted.log'), "a").write(result)
                            writed_log_counter += 1
                            platform = None
                            print('{}: {} log reformatted'.format(datetime.datetime.now().time(), writed_log_counter), end="\r")

if __name__ == '__main__':
    log_file = os.path.join(os.path.dirname(__file__),
                            '../../ProdLogs/test_samples/nginx0.dt07.net-2017-08-31_16-00-01.header.log')
    formatted_log_dir = os.path.join(os.path.dirname(__file__), '../../ResProds')
    reformatter = LogProcessor(log_file, formatted_log_dir, True)
    reformatter.reformat_train_sample()
