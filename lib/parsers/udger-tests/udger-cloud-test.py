import json
import pprint
 
try:
    from urllib.parse import urlencode
    from urllib.request import urlopen
except ImportError:
    from urllib import urlencode, urlopen   # Python 2
 
 
post_data = {
    'accesskey': '0bd479a4d5e17abf4c3a9e07838644c4',
    'ua': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.95 YaBrowser/17.1.0.2034 Yowser/2.5 Safari/537.36',
    #'ip': '66.249.64.1',
    #'ip': '212.90.173.122'
    'ip': '212.90.173.122'
}
 
try:
    response_bytes = urlopen(
        'https://api.udger.com/v3/parse',
        urlencode(post_data).encode('UTF-8'),
    ).read()
 
    data_dict = json.loads(
        response_bytes.decode('UTF-8'),
    )
except Exception as e:
    print("Udger.com request failed:", e)
 
else:
    pprint.pprint(data_dict)
