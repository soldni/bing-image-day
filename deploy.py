import json
import urllib.request


def main():
    req = urllib.request.Request(
        'http://www.bing.com/HPImageArchive.aspx'
        '?format=js&idx=0&n=1&mkt=en-US'
    )
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read())
        url = 'http://www.bing.com' + data['images'][0]['url']
        with open('template.html', 'r') as f, \
                open('docs/index.html', 'w') as f2:
            template = f.read().replace('INSERT_URL_HERE', url)
            f2.write(template)


if __name__ == '__main__':
    main()
