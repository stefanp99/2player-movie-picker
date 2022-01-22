import json
import requests
import re


class Show:
    def __init__(self, name, show_type, url, genre, description, year, rating, image, actors, trailer):
        self.name = name
        self.show_type = show_type
        self.url = url
        self.genre = genre
        self.description = description
        self.year = year
        self.rating = rating
        self.image = image
        self.actors = actors
        self.trailer = trailer


def ids_on_page(page_url):
    response = requests.get(page_url)
    if response.status_code == 200:
        content = response.content.decode('utf-8')
        ids = re.findall('/title/(.*)/vote', content)
        return ids


def show_class(id):
    url = f'https://www.imdb.com/title/{id}'
    response = requests.get(url)
    if response.status_code == 200:
        content = response.content.decode('utf-8')
        ind = content.find('<script type="application/ld+json">{') + len('<script type="application/ld+json">{') - 1
        json_string = content[ind:]
        ind = json_string.find('}</script>') + 1
        json_string = json_string.replace(json_string[ind:], '')
        resp = json.loads(json_string)
        has_genre = True
        has_description = True
        has_date = True
        has_rating = True
        has_image = True
        has_actors = True
        has_trailer = True
        if 'genre' not in resp:
            has_genre = False
        if 'description' not in resp:
            has_description = False
        if 'datePublished' not in resp:
            has_date = False
        if 'aggregateRating' not in resp:
            has_rating = False
        if 'image' not in resp:
            has_image = False
        if 'actor' not in resp:
            has_actors = False
        if 'trailer' not in resp:
            has_trailer = False
        a = []
        s = Show(resp['name'], resp['@type'], 'https://www.imdb.com' + resp['url'], '', '', -1, '', '', a, '')
        if has_genre:
            s.genre = resp['genre']
        if has_description:
            # s.description = resp['description']
            result = re.search('<meta name="description" content="(.*)" />', content)
            if len(result.group(1)) > len(resp['description']):
                s.description = result.group(1)
            else:
                s.description = resp['description']
        if has_date:
            s.year = resp['datePublished']
            s.year = int(s.year[:4])
        if has_rating:
            s.rating = resp['aggregateRating']
        if has_image:
            s.image = resp['image']
        if has_actors:
            s.actors = resp['actor']
        if has_trailer:
            s.trailer = 'https://www.imdb.com' + resp['trailer']['embedUrl']
            if 'description' in resp['trailer']:
                if resp['trailer']['description'].lower().find('trailer') == -1 and \
                        resp['trailer']['description'].lower().find('watch') == -1 and\
                        len(resp['trailer']['description']) > len(s.description):
                    s.description = resp['trailer']['description']
        return s


index = 1
shows = []
nr = 0
while index < 1000:
    url = f'https://www.imdb.com/search/title/?groups=top_1000&start={index}'
    print(ids_on_page(url))
    for id in ids_on_page(url):
        nr += 1
        print(f'{nr}/1000 - {id}')
        show = show_class(id)
        print(show.description)
        shows.append(show.__dict__)
        json_string = json.dumps(shows)
        with open('movie_db.json', 'w') as file:
            file.write(json_string)
    index += 50
# with open('movie_db.txt') as file:
#     data = json.load(file)
#     i = 0
#     for d in data:
#         i += 1
#         print(f"{i} - {d['name']} {d['year']} {d['description']}")
