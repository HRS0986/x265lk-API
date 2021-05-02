import requests as rq
from bs4 import BeautifulSoup
from tqdm import tqdm
import re
from colorama import init, Fore

init(convert=True)


class x265LK:

    def __init__(self):
        self.__URL = 'https://x265lk.com/wp-json/dooplay/search/?keyword='
        self.__nonce = '&nonce=deec18d3b5'

        # Error Codes
        self.OK = 1
        self.NO_SEARCH_DATA = 2
        self.WEB_ERROR = 3
        self.KEYBOARD_INTERRUPT = 4
        self.CONNECTION_ERROR = 5
        self.DOWNLOAD_ERROR = 6

    def __str__(self):
        return f'<x265lk Object>'

    def search(self, term: str, tv=True) -> dict:
        """
        params:
            term - search term
            tv - mode. if it's value is true, mode is tv series else movies

        return a dictionary contains response_code, status_code, data.
        if not error, data contains list of dictionaries of search results
        """
        searchURL: str = f'{self.__URL}{term}{self.__nonce}'

        try:
            r = rq.get(searchURL)

            if r.status_code == 200:
                response_data: dict = r.json()
                search_result: list[dict[str, str]] = []

                dtype: str = 'tvshows' if tv else 'movies'
                for id, v in response_data.items():
                    # print(v, 'v')
                    if dtype in v['url']:
                        item: dict[str, str] = {'id': id, 'title': v['title'], 'url': v['url']}
                        search_result.append(item)

                # No Search Result
                if 'error' in response_data.keys():
                    print('TEST1')
                    return {'response_code': self.NO_SEARCH_DATA, 'status_code': r.status_code, 'data': 'Nothing Found'}

                # OK. No Errors
                return {'response_code': self.OK, 'status_code': r.status_code, 'data': search_result}

            # Web Errors Like 404, 500, 401...
            return {'response_code': self.WEB_ERROR, 'status_code': r.status_code, 'data': None}

        except KeyboardInterrupt:
            return {'response_code': self.KEYBOARD_INTERRUPT, 'status_code': None, 'data': None}

        except Exception as e:
            # Connection Error
            return {'response_code': self.CONNECTION_ERROR, 'status_code': None, 'data': None}

    def download(self, link: str, path: str, progress=True):
        """
        params:
            link - download link
            path - save path
            progress - show or hide downloading progress bar

        return a dictionary contains response_code, status_code, data.
        if not error, data contains downloaded file's location
        """

        try:
            r = rq.get(link, stream=True)

            if r.status_code == 200:
                name_from_link: str = link.split('/')[-1]
                removed_site_name_as_list: list = name_from_link.split('.')[3:]
                removed_site_name: str = '.'.join(removed_site_name_as_list)
                decoded_name: str = rq.utils.unquote(removed_site_name)
                filename: str = f'{path}\\{decoded_name}'

                item_length = int(r.headers['content-length'])
                block_size: int = 1024

                if progress:
                    print(Fore.CYAN + f'Downloading {decoded_name}')
                    bar = tqdm(total=item_length, unit='iB', unit_scale=True)

                with open(filename, 'wb') as item:
                    for data in r.iter_content(block_size):
                        if progress: bar.update(len(data))
                        item.write(data)
                    if progress: bar.close()

                if item_length != 0 and bar.n != item_length:
                    # Download Error
                    return {'response_code': self.DOWNLOAD_ERROR, 'status_code': r.status_code, 'data': None}

                else:
                    # # OK. No Errors. Download OK
                    return {'response_code': self.OK, 'status_code': r.status_code, 'data': filename}

            # Web Errors Like 404, 500, 401...
            return {'response_code': self.WEB_ERROR, 'status_code': r.status_code, 'data': None}

        except KeyboardInterrupt:
            return {'response_code': self.KEYBOARD_INTERRUPT, 'status_code': None, 'data': None}

        except Exception as e:
            # Connection Error
            return {'response_code': self.CONNECTION_ERROR, 'status_code': None, 'data': None}

    def extract_movie_or_episode_copy(self, tv: bool, link: str) -> dict:
        """
        params:
            link - TV Series Episode page or Movie Page link
            tv - TV or Movie Mode

        return a dictionary contains response_code, status_code, data.
        if not error, data contains list of dictionaries of movie or episode copies
        """

        movie_title: str = ''

        if not tv:
            movie_title = ' '.join(link.split('/')[-2].split('-'))

        try:
            r = rq.get(link)

            if r.status_code == 200:
                copies: list = []
                soup = BeautifulSoup(r.text, 'html.parser')
                download_div = soup.find('div', {'id': 'download'})  # Type : <class 'bs4.element.Tag'>
                links_data = download_div.find('tbody').findAll(
                    'tr')  # Type : <class 'bs4.element.ResultSet'>
                download_page_links: list = []
                for i, row in enumerate(links_data, 1):
                    data = row.findAll('td')
                    link: str = data[0].a['href']
                    copy: str = str(data[1].strong.contents[0])
                    size: str = data[3].text
                    copy_data: dict[str, str] = {'copy_name': copy, 'url': link, 'size': size}

                    if not tv:
                        copy_data['movie'] = movie_title

                    copies.append(copy_data)

                # OK. No Errors
                return {'response_code': self.OK, 'status_code': r.status_code, 'data': copies}

            # Web Errors Like 404, 500, 401...
            return {'response_code': self.WEB_ERROR, 'status_code': r.status_code, 'data': None}

        except KeyboardInterrupt:
            return {'response_code': self.KEYBOARD_INTERRUPT, 'status_code': None, 'data': None}

        except Exception as e:
            # Connection Error
            return {'response_code': self.CONNECTION_ERROR, 'status_code': None, 'data': None}

    def get_download_link(self, link: str) -> dict:
        """
        params:
            link - movie copy or episode link

        return a dictionary contains response_code, status_code, data.
        if not error, data contains movie or episode's final download link
        """

        try:
            r = rq.get(link)

            if r.status_code == 200:
                soup = BeautifulSoup(r.text, 'html.parser')
                final_link: str = soup.find('div', {'class': 'inside'}).a['href']

                # OK. No Errors
                return {'response_code': self.OK, 'status_code': r.status_code, 'data': final_link}

            # Web Errors Like 404, 500, 401...
            return {'response_code': self.WEB_ERROR, 'status_code': r.status_code, 'data': None}

        except KeyboardInterrupt:
            return {'response_code': self.KEYBOARD_INTERRUPT, 'status_code': None, 'data': None}

        except Exception as e:
            # Connection Error
            return {'response_code': self.CONNECTION_ERROR, 'status_code': None, 'data': None}

    def extract_seasons(self, link: str) -> dict:
        """
        params:
            link - link of the tv series's page

        return a dictionary contains response_code, status_code, data.
        if not error, data contains list like this:
            [ { season_no, date, episodes:[ { epi_no, epi_name, epi_link, epi_date }, ... ] }, ... ]
        """

        try:
            r = rq.get(link)

            if r.status_code == 200:
                soup = BeautifulSoup(r.text, 'html.parser')
                seasonsDiv = soup.find('div', {'id': 'seasons'})  # Type : <class 'bs4.element.Tag'>
                seasons = seasonsDiv.findAll('div', {'class': 'se-c'})  # Type : <class 'bs4.element.ResultSet'>

                seasons_data: list = []

                for season_html in seasons:
                    season_data_html = season_html.find('div', {'class': 'se-q'})  # Type : <class 'bs4.element.Tag'>
                    season_data = season_data_html.find('span',
                                                        {'class': 'title'})  # Type : <class 'bs4.element.ResultSet'>
                    season_data_text: list = season_data.text.split()
                    season_no: str = ' '.join(season_data_text[:2])
                    season_date: str = ' '.join(season_data_text[2:])

                    season: dict = {'season_no': season_no, 'date': season_date, 'episodes': []}
                    eps_data_html = season_html.find('div', {'class': 'se-a'}).find(
                        'ul')  # Type : <class 'bs4.element.Tag'>

                    for ep_html in eps_data_html:
                        ep_no_n_se_no: list = ep_html.find('div', {'class': 'numerando'}).text.split(' ')
                        ep_no: str = ep_no_n_se_no[-1]

                        epi_data_html = ep_html.find('div', {'class': 'episodiotitle'})  # <class 'bs4.element.Tag'>

                        ep_name_n_link = epi_data_html.a  # <class 'bs4.element.Tag'>
                        ep_name: str = ep_name_n_link.text
                        ep_link: str = ep_name_n_link['href']
                        ep_date: str = epi_data_html.span.contents[0]

                        episode: dict = {'epi_no': ep_no, 'epi_name': ep_name, 'epi_link': ep_link, 'epi_date': ep_date}
                        season['episodes'].append(episode)

                    seasons_data.append(season)

                # OK. No Errors
                return {'response_code': self.OK, 'status_code': r.status_code, 'data': seasons_data}

            # Web Errors Like 404, 500, 401...
            return {'response_code': self.WEB_ERROR, 'status_code': r.status_code, 'data': None}

        except KeyboardInterrupt:
            return {'response_code': self.KEYBOARD_INTERRUPT, 'status_code': None, 'data': None}

        except Exception as e:
            # Connection Error
            return {'response_code': self.CONNECTION_ERROR, 'status_code': None, 'data': None}

    def get_years(self):
        """
        return years data as a list of dictionaries
        """

        URL = 'https://x265lk.com/'

        try:
            r = rq.get(URL)
            if r.status_code == 200:
                soup = BeautifulSoup(r.text, 'html.parser')
                year_list_html = soup.find('ul', {'class': 'releases scrolling'})
                years_html = year_list_html.findAll('a')
                years = []
                for y in years_html:
                    year = y.text
                    link = y['href']
                    year_data = {'year': year, 'url': link}
                    years.append(year_data)

                # OK. No Errors
                return {'response_code': self.OK, 'status_code': r.status_code, 'data': years}

            # Web Errors Like 404, 500, 401...
            return {'response_code': self.WEB_ERROR, 'status_code': r.status_code, 'data': None}

        except KeyboardInterrupt:
            return {'response_code': self.KEYBOARD_INTERRUPT, 'status_code': None, 'data': None}

        except Exception as e:
            # Connection Error
            return {'response_code': self.CONNECTION_ERROR, 'status_code': None, 'data': None}

    def __get_from_pages(self, term: str, param: str, max=1):
        movie_data = []
        tv_data = []

        def get_from_page(page: int):
            try:
                URL = f'https://x265lk.com/{term}/{param}/page/{page}/'
                r = rq.get(URL)

                movies = []
                tv_series = []

                if r.status_code == 200:
                    soup = BeautifulSoup(r.text, 'html.parser')
                    movies_html = soup.findAll('article', {'class': 'item movies'})
                    tv_html = soup.findAll('article', {'class': 'item tvshows'})

                    for movie in movies_html:
                        movie_data = movie.find('div', {'class': 'data'}).a
                        title = movie_data.text
                        link = movie_data['href']

                        movie_d = {'title': title, 'url': link}
                        movies.append(movie_d)

                    for tv in tv_html:
                        series_data = tv.find('div', {'class': 'data'}).a
                        title = series_data.text
                        link = series_data['href']

                        series_d = {'title': title, 'url': link}
                        tv_series.append(series_d)

                    # OK. No Errors
                    return {'response_code': self.OK, 'status_code': r.status_code, 'data': (movies, tv_series)}

                elif r.status_code == 404:
                    # OK. No Errors
                    return {'response_code': self.OK, 'status_code': r.status_code, 'data': (movies, tv_series)}

                # Web Errors Like 500, 401...
                return {'response_code': self.WEB_ERROR, 'status_code': r.status_code, 'data': None}

            except KeyboardInterrupt:
                return {'response_code': self.KEYBOARD_INTERRUPT, 'status_code': None, 'data': None}

            except Exception as e:
                # Connection Error
                return {'response_code': self.CONNECTION_ERROR, 'status_code': None, 'data': None}

        for i in range(1, max + 1):
            response = get_from_page(i)
            if response['response_code'] == 1:
                movie_data.extend(response['data'][0])
                tv_data.extend(response['data'][1])
            else:
                return response

        data = {'movies': movie_data, 'tv_series': tv_data}

        # OK. No Errors
        return {'response_code': self.OK, 'status_code': 200, 'data': data}

    def get_by_year(self, year: str, max=1):
        """
        params:
            year - year to search
            max - number of pages to search

        return a dictionary contain movies and tv series released in given year
        """
        response = self.__get_from_pages('release', year, max)
        return response

    def get_genres(self):
        """
        return genres data as a list of dictionaries
        """

        URL_PTN = r'https://x265lk.com/genre/(?:.+?)/'
        REO = re.compile(URL_PTN)
        URL = 'https://x265lk.com/'

        try:
            r = rq.get(URL)
            if r.status_code == 200:
                genres_html = REO.findall(r.text)
                genres = []
                g_links = []
                for link in genres_html:
                    if not link in g_links:
                        g_links.append(link)
                        g_name = link.split('/')[-2]
                        genre_data = {'name': g_name, 'url': link}
                        genres.append(genre_data)

                        # OK. No Errors
                return {'response_code': self.OK, 'status_code': r.status_code, 'data': genres}

            # Web Errors Like 404, 500, 401...
            return {'response_code': self.WEB_ERROR, 'status_code': r.status_code, 'data': None}

        except KeyboardInterrupt:
            return {'response_code': self.KEYBOARD_INTERRUPT, 'status_code': None, 'data': None}

        except Exception as e:
            # Connection Error
            return {'response_code': self.CONNECTION_ERROR, 'status_code': None, 'data': None}

    def get_by_genre(self, genre: str, max=1):
        """
        params:
            genre - genre to search
            max - number of pages to search

        return a dictionary contain movies and tv series of the genre
        """
        response = self.__get_from_pages('genre', genre, max)
        return response
