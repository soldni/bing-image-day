from argparse import ArgumentParser
import datetime
import json
import os
import random
from time import sleep
from urllib.request import Request, urlopen, urlretrieve


def get_aic_search_public_domain(
    page: int = 1,
    limit: int = 1,
    url: str = 'https://api.artic.edu/api/v1/artworks/search'
) -> tuple[int, list[dict]]:
    data = {"query": {"term": {"is_public_domain": True}}}

    req = Request(
        url=f'{url}?page={page * limit}&limit={limit}',
        data=json.dumps(data).encode('utf-8'),
        headers={'Content-Type': 'application/json'},
        method='POST'
    )

    print(req.full_url)

    with urlopen(req) as response:
        data = json.loads(response.read())
        total_items = data['pagination']['total_pages']
        artworks = data['data']

    return total_items, artworks


def get_aic_artworks(
    page: int = 1,
    limit: int = 1,
    url: str = "https://api.artic.edu/api/v1/artworks"
) -> tuple[int, list[dict]]:

    req = Request(
        url=f'{url}?page={page * limit}&limit={limit}&fields=api_link,id',
        headers={'Content-Type': 'application/json'},
        method='GET'
    )

    with urlopen(req) as response:
        data = json.loads(response.read())
        total_items = data['pagination']['total_pages']
        artworks = data['data']

    return total_items, artworks


def get_aic_artwork(artwork: dict) -> tuple[str, str]:
    # check if artwork exists
    if os.path.exists(f'docs/images/{artwork["id"]}.jpg'):
        print(f"Artwork ID: {artwork['id']} already exists; skipping download...")
        with open(f'docs/metadata/{artwork["id"]}.json', 'r') as f:
            data = json.load(f)
        return f'docs/images/{artwork["id"]}.jpg', f'{data["title"]} by {data["artist_display"]}'

    # proceed to download image
    req = Request(url=artwork['api_link'] + '?fields=id,title,artist_display,date_display,image_id,thumbnail')
    with urlopen(req) as response:
        content = json.loads(response.read())
        data = content['data']
        config = content['config']

    width = data['thumbnail']['width']
    title = data['title'].replace('\n', ' ').strip()
    artist = data['artist_display'].replace('\n', ' ').strip()
    # date = data['date_display'].replace('\n', ' ').strip()
    image_id = data['image_id']
    iiif_url = config['iiif_url']

    url = f'{iiif_url}/{image_id}/full/{width},/0/default.jpg'
    caption = f'{title} by {artist}'
    print(f"Found artwork ID: {data['id']}; downloading image from {url} ...")

    # Download image to `docs/images` folder
    path = f'docs/images/{data["id"]}.jpg'
    urlretrieve(url, path)
    with open(f'docs/metadata/{data["id"]}.json', 'w') as f:
        json.dump(data, f, indent=2)

    return path, caption


def aic_image(offset=0, max_offset=10):
    try:
        # seed is today's date in YYYYMMDD format
        random.seed(int(datetime.datetime.now().strftime('%Y%m%d')) + offset)

        print("Getting number of artworks...")

        total_items, _ = get_aic_artworks()

        print(f"Total artworks: {total_items}")

        # Get random page
        page = random.randint(1, total_items)

        print(f"Getting artwork from page {page}...")

        _, artworks = get_aic_artworks(page=page)
        artwork = artworks[0]

        print(f"Found artwork {artwork}; getting full details...")

        return get_aic_artwork(artwork)

    except Exception as e:
        if offset < max_offset:
            # sleep between 1 and 5 seconds before retrying
            sleep(random.random() * 4 + 1)
            # Retry up to 10 times
            return aic_image(offset + 1, max_offset)
        else:
            raise e


def main_bing():
    req = Request('https://www.bing.com/HPImageArchive.aspx?format=js&idx=0&n=1&mkt=en-US')
    with urlopen(req) as response:
        data = json.loads(response.read())
        url = 'https://www.bing.com' + data['images'][0]['url']
        title = data['images'][0]['title']
        with open('template.html', 'r') as f, \
                open('docs/index.html', 'w') as f2:
            template = (
                f.read()
                .replace('INSERT_URL_HERE', url)
                .replace('INSERT_TITLE_HERE', title)
                .replace('INSERT_SOURCE_HERE', 'Bing Image of the Day')
            )
            f2.write(template)


def main_art():
    ap = ArgumentParser()
    ap.add_argument('-s', '--seed', type=int, default=0)
    ap.add_argument('-m', '--max-offset', type=int, default=10)
    args = ap.parse_args()

    path, caption = aic_image(offset=args.seed, max_offset=args.max_offset+args.seed)
    path = path.replace('docs/', '')
    with open('template.html', 'r') as f, \
            open('docs/index.html', 'w') as f2:
        template = (
            f.read()
            .replace('INSERT_URL_HERE', path)
            .replace('INSERT_TITLE_HERE', caption)
            .replace('INSERT_SOURCE_HERE', 'Art Institute of Chicago')
        )
        f2.write(template)


if __name__ == '__main__':
    main_art()
