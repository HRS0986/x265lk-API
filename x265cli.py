from art import tprint
import requests as rq 
from colorama import init, Fore
import random
import os
from tqdm import tqdm
from bs4 import BeautifulSoup
from PyInquirer import prompt


init(convert=True)

CWD: str = os.getcwd()

class x265LK:

    def __init__(self):        
        self.__URL = 'https://x265lk.com/wp-json/dooplay/search/?keyword='        
        self.__seasons = []
        self.__episodes = []

    
    # Statring function
    def display_title(self):
        os.system('CLS')
        print(random.choice([Fore.LIGHTMAGENTA_EX, Fore.LIGHTBLUE_EX, Fore.LIGHTCYAN_EX]))
        tprint('x265LK', random.choice(["clossal", "banner3-d", "georgiall"]))
        print(Fore.RESET)


    # This function takes search term and return search result as list
    # dtype is a param for decide mode
    def search(self, term:str, dtype='tvshows') -> list:
        search_url = f'{self.__URL}{term}&nonce=deec18d3b5'

        r = rq.get(search_url)
        
        if r.status_code == 200:
            search_result = r.json()
            query_data = []
            
            if 'error' in search_result.keys():
                return -1

            for id, v in search_result.items():
                if dtype in v['url']:
                    item = { 'id': id, 'title': v['title'], 'url': v['url'] }
                    query_data.append(item)
            return query_data
        
        return (-9, r.status_code)


    # This function ask mode from user and return mode
    def get_mode(self) -> str:
        question =  {
            'type': 'list',
            'name': 'ui',
            'message': 'Select Mode',
            'choices': [
                'TV Series',
                'Movies',
            ],
            'filter': lambda val: val.lower()
        }
        answer = prompt(question)['ui']
        if answer[0] == 't':
            return 'tvshows'
        
        return 'movies'

    
    # This function takes user selected movie's data as a dictionary and scrape movie copy links from movie page
    def get_movie_page_links(self, movie_data: dict) -> list:
        r = rq.get(movie_data['url'])

        if r.status_code == 200:
            movie_copies = []
            soup = BeautifulSoup(r.text, 'html.parser')
            download_div = soup.find('div', {'id':'download'})
            links_data = download_div.find('tbody').findAll('tr')
            download_page_links = []
            for i, row in enumerate(links_data, 1):
                data = row.findAll('td')
                link = data[0].a['href']
                copy = data[1].strong.contents[0]                
                size = data[3].text               
                copy_data = { 'name': copy, 'url': link, 'size': size }
                movie_copies.append(copy_data)

            return movie_copies

        return (-9, r.status_code)


    # Only for movie download mode. Takes movie copies as a list of dictionaries and return    
    def select_copy(self, copy_list: list):

        print(Fore.LIGHTYELLOW_EX + '[+] Select Copy:')
        for i, copy in enumerate(copy_list, 1):
            print(f"\t{i}. {copy['name']} - {copy['size']}")

        print(Fore.RESET)
        print('\n[+] Enter Copy Number. Or')       
        print('[+] Enter -2 To Go Back')
        print('[+] Enter -9 To Exit')
        question = {
            'type': 'input',
            'name': 'epi_no',
            'message': 'Enter Copy Number:',
            'validate': lambda val: val in [*[str(x) for x in range(1, len(copy_list)+1)], '-2', '-9']
        }

        ans = prompt(question)['epi_no'].strip()
        copy_no = int(ans) - 1

        if ans == '-9':
            os.system('CLS')
            exit()

        elif ans == '-2':
            return -2

        copy = copy_list[copy_no]
        r = rq.get(copy['url'])

        if r.status_code == 200:
            sp = BeautifulSoup(r.text, 'html.parser')
            Link = sp.find('div', {'class':'inside'}).a['href']            
            return Link

        return (-9, r.status_code)
            
    
    # This function takes search result ans ask user for select one and return user's choice
    def select_series_or_movie(self, seriesOrMovieList:list) -> dict:
        question = {
            'type': 'input',
            'name': 'item_no',
            'message': 'Enter Number:',
            'validate': lambda val: val in [*[str(i) for i in range(1, len(seriesOrMovieList)+1)], '-1', '-9' ]
        }
        print(Fore.LIGHTYELLOW_EX + '[+] Search Result:')
        for ind, item in enumerate(seriesOrMovieList, 1):
            print(Fore.LIGHTYELLOW_EX + f"\t{ind}. {item['title']}")
        print(Fore.RESET)

        print('[+] Enter -1 to go back')
        print('[+] Enter -9 To Exit')
        number = prompt(question)['item_no']  

        if number == '-9':
            os.system('CLS')
            exit()

        if number.isdigit():
            item_ind = int(number) - 1                   
            return seriesOrMovieList[item_ind]
        
        return number


    # Only For TV Series Mode
    def select_season(self, series:dict) -> tuple:       
        print(Fore.LIGHTYELLOW_EX + f"[+] {series['title']} Seasons: ")
        r = rq.get(series['url'])

        if r.status_code == 200:
            html = r.text
            soup = BeautifulSoup(html, 'html.parser')
            seasonsDiv = soup.find('div', {'id': 'seasons'})
            seasons = seasonsDiv.findAll('div', {'class': 'se-c'})
            seasonCount = len(seasons)
                        
            for i, season in enumerate(seasons, 1):
                self.__seasons.append(str(season))
                print(f'\t{i}.', season.div.find('span', {'class' : 'title'}).text)
            print(Fore.RESET)

            print('[+] Enter Number To Select Episodes. Or,')
            print('[+] Enter 0<Number> to download all episodes in season.Or,')
            print('[+] Enter 0 to download all seasons')
            print('[+] Enter -1 for search again')
            print('[+] Enter -9 To Exit')
            nums = []

            try:
                question = {
                    'type': 'input',
                    'name': 'season_no',
                    'message': 'Enter Season Number:',
                    'validate': lambda val: all([int(v) in [*[i for i in range(seasonCount+1)], -1, -9] for v in val.split()])
                }
                season_number = prompt(question)['season_no']
                nums = season_number.split()
            
            except KeyboardInterrupt:
                exit()
            
            except Exception as e:
                self.display_title()
                self.select_season(series)

            # Download All Seasons
            if int(nums[0]) == 0:
                return (seasonCount, series['title'], 'A')
            
            # Go Back
            if int(nums[0]) == -1:
                return (-1, ' ', '-1')
            
            elif int(nums[0]) == -9:
                os.system('CLS')
                exit()

            # Download Full Single Season
            elif len(nums) == 1 and nums[0][0] == '0' :
                return (int(season_number), series['title'], 'a')

            # Go To Episode Selection
            elif len(nums) == 1:
                return (int(season_number), series['title'], 'e')

            else:
                full_seasons = [int(i) for i in nums]
                return (full_seasons, series['title'], 'm')

        return (-9, r.status_code, 0)


    # Only For TV Series Mode in download single or multiple episodes
    def select_episode(self, season_no:int, series_name:str, ask=True) -> list[int]:
        season = self.__seasons[season_no - 1]
        soup = BeautifulSoup(season, 'html.parser')
        episodesList = soup.find('div', {'class': 'se-a'}).find('ul')

        print(Fore.LIGHTYELLOW_EX + f"[+] {series_name} Season {season_no} Episodes: ")
        for i, episode in enumerate(episodesList, 1):
            epiData = episode.find('div',{'class':'episodiotitle'}).a
            epi = {'page_url': epiData['href'], 'title':epiData.text}
            self.__episodes.append(epi)
            print(f"\t{i}. {epi['title']}")
        print(Fore.RESET)

        if not ask:
            return [i for i in range(1, len(self.__seasons)+1)]

        print('[+] Enter Episode Number. Or')
        print('[+] Enter Episode Numbers Space Seperated. Or')
        print('[+] Enter 0 To Download All')
        print('[+] Enter -2 To Go Back')
        print('[+] Enter -1 To Search TV Series')
        print('[+] Enter -9 To Exit')
        question = {
            'type': 'input',
            'name': 'epi_no',
            'message': 'Enter Episode Number:',
            'validate': lambda val: all([v in [*[str(i) for i in range(len(episodesList)+1)], str(-1), str(-2), str(-9)] for v in val.split()])
        }

        epis = prompt(question)['epi_no'].strip().split()

        if int(epis[0]) == 0:
            return [i for i in range(1, len(self.__seasons)+1)]

        if int(epis[0]) == -1:
            return [-1]

        if int(epis[0]) == -2:
            return [-2]

        epi_numbers = [int(ep) for ep in epis]
        return epi_numbers


    # This function takes episode number as a param
    # First, request html page of the episode and scrape final episode page link
    # Second, request final episode page and scrape final download link from that page
    # Return Final download link and status code
    def get_ep_link(self, epi_no:int) -> tuple:
        r = rq.get(self.__episodes[epi_no-1]['page_url'])

        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
            download_div = soup.find('div', {'id':'download'})
            link_data = download_div.find('tbody').findAll('td')[0]
            download_page_link = link_data.a['href']
            self.__episodes[epi_no]['download_page_url'] = download_page_link

            r2 = rq.get(download_page_link)

            if r2.status_code == 200:
                sp = BeautifulSoup(r2.text, 'html.parser')
                Link = sp.find('div', {'class':'inside'}).a['href']
                self.__episodes[epi_no-1]['download_url'] = Link                

                return (Link, r2.status_code)
            
            return (-9, r2.status_code)

        return (-9, r.status_code)


    # This function takes link and path as a param and download link
    def download(self, link:str, path:str):
        r = rq.get(link, stream=True)
        
        if r.status_code == 200:            
            ep_name = link.split('/')[-1]
            removed_site_name = ep_name.split('.')[3:]
            removed_site_name = '.'.join(removed_site_name)
            decoded_name = rq.utils.unquote(removed_site_name)           
            filename = f'{path}\\{decoded_name}'

            epi_length = int(r.headers['content-length'])
            block_size: int = 1024

            print(Fore.CYAN+f'Downloading {decoded_name}')
            bar = tqdm(total=epi_length, unit='iB', unit_scale=True)

            with open(filename, 'wb') as episode:
                for data in r.iter_content(block_size):
                    bar.update(len(data))
                    episode.write(data)
                bar.close()
            
            if epi_length != 0 and bar.n != epi_length:
                print(Fore.RED+"ERROR, Something went wrong"+Fore.RESET)            
            else:
                print(Fore.GREEN+f'Downloaded {filename} \n'+Fore.RESET)

        else:
            print(Fore.LIGHTRED_EX + f'[!] Connection Error : {r.status_code}' + Fore.RESET)
            input('Press Any Key To Exit...')
            exit()
    

    # Get download path from user
    def get_save_path(self) -> str:

        try:
            print(Fore.LIGHTYELLOW_EX + '\n[!] Enter path to save episode. Just press enter to save episode in current directory.')
            path: str = input(Fore.YELLOW + '?' + Fore.RESET +' Save Path (without file name) :').strip()

            if not path:
                return CWD

            is_valid_path = os.path.isdir(path)

            if not is_valid_path:
                os.mkdir(path)
            
            return path

        except KeyboardInterrupt:
            os.system('CLS')
            exit()

        except OSError as e:
            print(Fore.RED+'Error : {e}\n'+Fore.RESET)
            save_path()



x265 = x265LK()
series = dict()
mode = ''

def mode_select():
    global mode
    x265.display_title()
    print('[+] Welcome to x265lk.com CLI\n')
    mode = x265.get_mode()
    get_search()


def get_search():
    question = {
        'type': 'input',
        'name': 'search_term',
        'message': 'Enter Title To Search :',        
        'validate': lambda val: val != ''
    }

    x265.display_title()

    if mode == 'tvshows':
        print('[+] TV Series Mode\n') 
    else:
        print('[+] Movies Mode\n') 

    print('[+] Enter -1 to go back')

    search_term: str = prompt(question)['search_term']

    if search_term == '-1':
        mode_select()

    search_result: list = x265.search(search_term, mode)
    
    
    if search_result == -1:
        print(Fore.LIGHTRED_EX + '[!] Nothing Found' + Fore.RESET)
        os.system('PAUSE')
        get_search()

    if search_result[0] == -9:
        print(Fore.LIGHTRED_EX + f'[!] Connection Error : {search_result[1]}' + Fore.RESET)
        input('Press Any Key To Exit...')
        exit()
    

    x265.display_title()
    ui = x265.select_series_or_movie(search_result) 

    if ui == '-1':
        get_search()
    
    else:   
        global series
        series = ui
        get_season()


def get_season():
    x265.display_title()

    if mode == 'tvshows':
        season_no, series_name, dtype = x265.select_season(series)
        
        if season_no == -9:
            print(Fore.LIGHTRED_EX + f'[!] Connection Error : {series_name}' + Fore.RESET)
            input('Press Any Key To Exit...')
            exit()

        get_episode(season_no, series_name, dtype)

    else:
        copies = x265.get_movie_page_links(series)
        print(f"[+] Movie : {series['title']}\n")
        selected_link = x265.select_copy(copies)
        
        if selected_link == -2:
            get_search()

        elif selected_link[0] == -9:
            print(Fore.RED + f'[!] Error : {selected_link[1]}' + Fore.RESET)
            exit()
        
        path = x265.get_save_path()
        x265.display_title()
        print(Fore.LIGHTYELLOW_EX + f'\nLink: {selected_link}' + Fore.RESET)
        x265.download(selected_link, path)

        question =  {
            'type': 'list',
            'name': 'ui',
            'message': 'What to do next?',
            'choices': [
                'Download Another Episode',
                'Mode Change',
                'Change Season',
                'Search TV Series',
                'Exit'
            ],
            'filter': lambda val: val.lower()
        }

        answer = prompt(question)['ui']
        
        if answer[0] == 'd':
            get_episode(season_no, series_name, dtype)
        elif answer[0] == 'c':
            get_season()
        elif answer[0] == 's':
            get_search()
        elif answer[0] == 'm':
            mode_select()
        else:
            exit()


def get_episode(season_no, series_name, dtype):

    x265.display_title()
    if dtype == 'e':    # Go To Episode Selection
        epi_nums: list[int] = x265.select_episode(season_no, series_name)
        
        if epi_nums[0] == -1:
            get_search()

        elif epi_nums[0] == -2:
            get_season()

        path:str = x265.get_save_path()

        x265.display_title()
        for epi in epi_nums:
            link, epi_no = x265.get_ep_link(epi)
            if link == -9:
                print(Fore.LIGHTRED_EX + f'[!] Connection Error : {epi_no}' + Fore.RESET)
                input('Press Any Key To Exit...')
                exit()
            print(Fore.LIGHTYELLOW_EX + f'\nLink: {link}' + Fore.RESET)
            x265.download(link, path)

    elif dtype == 'A':
        x265.display_title()
        for i in range(season_no):
            epi_nums: list[int] = x265.select_episode(i+1, series_name, False)
            path:str = x265.get_save_path()

            for epi in epi_nums:
                link, epi_no = x265.get_ep_link(epi)
                if link == -9:
                    print(Fore.LIGHTRED_EX + f'[!] Connection Error : {epi_no}' + Fore.RESET)
                    input('Press Any Key To Exit...')
                    exit()
                print(Fore.LIGHTYELLOW_EX + f'\nLink: {link}' + Fore.RESET)
                x265.download(link, path)

    elif dtype == 'a':
        epi_nums: list[int] = x265.select_episode(season_no, series_name, False)
        path:str = x265.get_save_path()

        x265.display_title()
        for epi in epi_nums:
            link, epi_no = x265.get_ep_link(epi)
            if link == -9:
                print(Fore.LIGHTRED_EX + f'[!] Connection Error : {epi_no}' + Fore.RESET)
                input('Press Any Key To Exit...')
                exit()
            print(Fore.LIGHTYELLOW_EX + f'\nLink: {link}' + Fore.RESET)
            x265.download(link, path)

    elif dtype == '-1':
        get_search()

    else:   # Download Full Multiple Seasons
        x265.display_title()
        for n in season_no:
            epi_nums: list[int] = x265.select_episode(n, series_name, False)
            path:str = x265.get_save_path()
            
            for epi in epi_nums:
                link, epi_no = x265.get_ep_link(epi)
                if link == -9:
                    print(Fore.LIGHTRED_EX + f'[!] Connection Error : {epi_no}' + Fore.RESET)
                    input('Press Any Key To Exit...')
                    exit()                
                print(Fore.LIGHTYELLOW_EX + f'\nLink: {link}' + Fore.RESET)
                x265.download(link, path)

    question =  {
        'type': 'list',
        'name': 'ui',
        'message': 'What to do next?',
        'choices': [
            'Download Another Episode',
            'Mode Change',
            'Change Season',
            'Search TV Series',
            'Exit'
        ],
        'filter': lambda val: val.lower()
    }
    answer = prompt(question)['ui']
    
    if answer[0] == 'd':
        get_episode(season_no, series_name, dtype)
    elif answer[0] == 'c':
        get_season()
    elif answer[0] == 'm':
        mode_select()
    elif answer[0] == 's':
        get_search()
    else:
        exit()


if __name__ == '__main__':
    try:
        mode_select()
    except KeyboardInterrupt:
        os.system('CLS')
        exit()

    except KeyError:
        os.system('CLS')
        exit()