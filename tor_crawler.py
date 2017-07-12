import stem.process
from requests import Session
from requests.exceptions import Timeout
from html.parser import HTMLParser
from urllib.parse import urlparse

#------------------------------------ Network ----------------------------

SOCKS_PORT = 7000

tor_process = stem.process.launch_tor_with_config(
    config = {
        'SocksPort': str(SOCKS_PORT),
    },
    init_msg_handler = print,
)

session = Session()

session.proxies.update(
    {
        'http': 'socks5h://127.0.0.1:' + str(SOCKS_PORT),
        'https': 'socks5h://127.0.0.1:' + str(SOCKS_PORT)
    }
)

session.headers.update(
    {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
        'Accept-Encoding': 'none',
        'Accept-Language': 'en-US,en;q=0.8',
        'Connection': 'keep-alive',
    }
)

def query(url):
    try:
        r = session.get(url, timeout=5)
    except Timeout:
        print("Connection with", url, "timed out")
        return ''
    return r.text

#------------------------------------ Parsing ----------------------------

class Parser(HTMLParser):

    urls = []
    
    def handle_starttag(self, tag, attrs):
        #print("Encountered a tag:", tag)
        if tag == 'a':
            for attr in attrs:
                if attr[0] == 'href':
                    url = attr[1]
                    #print("Found url:", url)
                    self.urls.append(url)

parser = Parser()


#--------------------------------- Main action ---------------------------

url_pool = ['http://zqktlwi4fecvo6ri.onion/wiki/index.php/Main_Page']

def is_absolute(url):
    return bool(urlparse(url).netloc)

def retrieve_valid_urls(seed_url):
    html = query(seed_url)
    parser.feed(html)
    urls = parser.urls
    
    domain = urlparse(seed_url).netloc

    for url in urls:
        if is_absolute(url):
            print(url)

retrieve_valid_urls(url_pool[0])


print("Closing Tor...")
tor_process.kill()
