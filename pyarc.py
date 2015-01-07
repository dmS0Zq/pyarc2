from hashids import Hashids
from pymongo import MongoClient
from urllib import parse
from urllib.request import urlopen
from urllib.request import Request
from flask import Flask
from flask import Response
from bs4 import BeautifulSoup
import pymongo
#import magic
import traceback

mongo_client = MongoClient()
db = mongo_client.pyarc2
base58_hashids = Hashids(
        # base 58 alphabet (like bitcoin)
        alphabet='123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz',
        # guaranteed random string
        salt='tuidk389t8vckxe96958329w30ogohkfdj3wjw98cxuv4jkr83')
app = Flask(__name__)

def get_hash_code(string):
    MOD = 1000000000000000
    MULT = 37
    #hash_code = 0
    #hash_code *= MULT
    #hash_code += len(string)
    hash_code = len(string)
    hash_code %= MOD
    for c in list(string):
        hash_code *= MULT
        hash_code += ord(c)
        hash_code %= MOD
    return hash_code

@app.route("/render/from_url/<path:page_url>")
def render_from_page_url(page_url):
    try:
        GET_headers = {'User-Agent': 'pyarc/alpha'}
        GET_request = Request(
            page_url,
            headers=GET_headers
        )
        GET_response = urlopen(page_url)
        mime_type = GET_response.info()['Content-Type']
        raw_data = GET_response.read()
        if 'text' in mime_type:
            if 'text/html' in mime_type:
                print(page_url,"is html")
                soup = BeautifulSoup(raw_data)
                for link in soup.find_all('link'):
                    if 'href' in link.attrs:
                        link['href'] = '/render/from_url/' + parse.urljoin(page_url, link['href'])
                for script in soup.find_all('script'):
                    if 'src' in script.attrs:
                        script['src'] = '/render/from_url/' + parse.urljoin(page_url, script['src'])
                for img in soup.find_all('img'):
                    if 'src' in img.attrs:
                        img['src'] = '/render/from_url/' + parse.urljoin(page_url, img['src'])

                for a in soup.find_all('a'):
                    if 'href' in a.attrs:
                        a['href'] = '/render/from_url/' + parse.urljoin(page_url, a['href'])
                return soup.prettify()
            else:
                return Response(raw_data, mimetype=mime_type)
                #return str(raw_data.decode('utf-8'))
        elif 'image' in mime_type:
            return Response(raw_data, mimetype=mime_type)
            #return send_file(io.BytesIO(raw_data))
        elif 'application/javascript' in mime_type:
            return Response(raw_data, mimetype=mime_type)
        return "Bad stuff happened"
        #return GET_response.read()
    except Exception as e:
        print(traceback.print_exc())


@app.route("/render/from_id/<page_id>")
def render_from_page_id(page_id):
    return page_id

if __name__ == "__main__":
    app.run()
