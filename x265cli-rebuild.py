import random
from art import tprint
from x265lk import x265LK
from colorama import init, Fore
from PyInquirer import prompt
import os

init(convert=True)

CWD: str = os.getcwd()


class x265LkCli:
    def __init__(self):
        self.x265lk_object = x265LK()
        self.mode = 'tvshows'
        self.search_term = 'Empty'
        self.search_result: list[dict[str, str]] = []
        self.selected_item: dict[str, str] = dict()
        self.copies = []
        self.selected_copy = dict()
        self.save_path = CWD
        self.seasons = []
        self.full_series = False
        self.full_seasons = False
        self.selected_seasons = []
        self.selected_episodes = []

    def display_title(self):
        os.system('CLS')
        print(random.choice([Fore.LIGHTMAGENTA_EX, Fore.LIGHTBLUE_EX, Fore.LIGHTCYAN_EX]))
        tprint('x265LK', random.choice(["clossal", "banner3-d", "georgiall"]))
        print(Fore.RESET)

    def mode_select(self):
        """
        This function will ask user to select mode to search. Mode saved in self.mode
        Available modes are:
            1.TV Series
            2.Movies
        """

        self.display_title()
        print('[+] Welcome to x265lk.com CLI\n')

        question = {
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
            self.mode = 'tvshows'
        else:
            self.mode = 'movies'

    def get_search_result(self):
        """
        This function will ask search term for search.
        Search Result saved to self.search_result
        """
        question = {
            'type': 'input',
            'name': 'search_term',
            'message': 'Enter Title To Search :',
            'validate': lambda val: val != ''
        }

        self.display_title()

        if self.mode == 'tvshows':
            print('[+] TV Series Mode\n')
        else:
            print('[+] Movies Mode\n')
        print('[+] Enter -1 to go back')

        search_term: str = prompt(question)['search_term']
        self.search_term = search_term
        if search_term == '-1':
            self.mode_select()
            self.get_search_result()
            return None

        tv: bool = True if self.mode == 'tvshows' else False
        search_result_data: dict = self.x265lk_object.search(self.search_term, tv)

        if search_result_data['response_code'] == 2:
            print(Fore.LIGHTRED_EX + '[!] Nothing Found' + Fore.RESET)
            os.system('PAUSE')
            self.get_search_result()

        elif search_result_data['response_code'] == 4:
            print(Fore.RESET + f'\n[+] Thank you for using...')
            exit()

        elif search_result_data['response_code'] == 3 or search_result_data['response_code'] == 5:
            print(
                Fore.RED + '[+] Something went wrong. Please Check URL Again And Check Your Internet Connection' + Fore.RESET)
            os.system('PAUSE')
            self.get_search_result()

        elif search_result_data['response_code'] == 1:
            self.search_result = search_result_data['data']

    def select_series_or_movie(self):
        """
        This function takes search result ans ask user for select one.
        User selected item saved to self.selected_tem
        """
        question = {
            'type': 'input',
            'name': 'item_no',
            'message': 'Enter Number:',
            'validate': lambda val: val in [*[str(i) for i in range(1, len(self.search_result) + 1)], '-1', '-9']
        }

        self.display_title()
        print(Fore.LIGHTYELLOW_EX + '[+] Search Result:')
        for ind, item in enumerate(self.search_result, 1):
            print(Fore.LIGHTYELLOW_EX + f"\t{ind}. {item['title']}")
        print(Fore.RESET)

        print('[+] Enter -1 to go back')
        print('[+] Enter -9 To Exit')
        number = prompt(question)['item_no']
        if number == '-9':
            os.system('CLS')
            exit()

        elif number == '-1':
            self.get_search_result()
            self.select_series_or_movie()

        elif number.isdigit():
            item_ind = int(number) - 1
            self.selected_item = self.search_result[item_ind]

    def select_movie_copy(self):
        copies_data = self.x265lk_object.extract_movie_or_episode_copy(False, self.selected_item['url'])

        if copies_data['response_code'] == 2:
            print(Fore.LIGHTRED_EX + '[!] Nothing Found' + Fore.RESET)
            os.system('PAUSE')
            self.select_series_or_movie()

        elif copies_data['response_code'] == 4:
            print(Fore.RESET + f'\n[+] Thank you for using...')
            exit()

        elif copies_data['response_code'] == 3 or copies_data['response_code'] == 5:
            print(
                Fore.RED + '[+] Something went wrong. Please Check URL Again And Check Your Internet Connection' + Fore.RESET)
            os.system('PAUSE')
            self.select_series_or_movie()

        elif copies_data['response_code'] == 1:
            self.copies = copies_data['data']

        self.display_title()
        print(Fore.LIGHTYELLOW_EX + f"[+] Movie: {self.selected_item['title']}")
        print(Fore.LIGHTYELLOW_EX + '[+] Select Copy:')
        for i, copy in enumerate(self.copies, 1):
            print(f"\t{i}. {copy['copy_name']} - {copy['size']}")

        print(Fore.RESET)
        print('\n[+] Enter Copy Number. Or')
        print('[+] Enter -1 To Go Back')
        print('[+] Enter -9 To Exit')

        question = {
            'type': 'input',
            'name': 'copy_no',
            'message': 'Enter Copy Number:',
            'validate': lambda val: val in [*[str(x) for x in range(1, len(self.copies) + 1)], '-1', '-9']
        }

        ans = prompt(question)['copy_no'].strip()
        copy_no = int(ans) - 1

        if ans == '-9':
            os.system('CLS')
            exit()

        elif ans == '-1':
            self.select_series_or_movie()
            self.select_movie_copy()

        else:
            self.selected_copy = self.copies[copy_no]

    def select_season(self):
        self.display_title()
        print(Fore.LIGHTYELLOW_EX + f"[+] {self.selected_item['title']} Seasons: ")

        season_data = self.x265lk_object.extract_seasons(self.selected_item['url'])

        if season_data['response_code'] == 4:
            print(Fore.RESET + f'\n[+] Thank you for using...')
            exit()

        elif season_data['response_code'] == 3 or season_data['response_code'] == 5:
            print(
                Fore.RED + '[+] Something went wrong. Please Check URL Again And Check Your Internet Connection' + Fore.RESET)
            os.system('PAUSE')
            self.select_series_or_movie()

        elif season_data['response_code'] == 1:
            self.seasons = season_data['data']

        season_count = len(self.seasons)

        for i, season in enumerate(self.seasons, 1):
            print(f"\t{i}. {season['season_no']}")
        print(Fore.RESET)

        print('[+] Enter Number To Select Episodes. Or,')
        print('[+] Enter 0<Number> to download all episodes in season.Or,')
        print('[+] Enter 0 to download all seasons')
        print('[+] Enter -1 For Go Back')
        print('[+] Enter -9 To Exit')
        nums = []
        season_number = ''

        try:
            question = {
                'type': 'input',
                'name': 'season_no',
                'message': 'Enter Season Number:',
                'validate': lambda val: all(
                    [int(v) in [*[i for i in range(season_count + 1)], -1, -9] for v in val.split()])
            }
            season_number = prompt(question)['season_no']
            nums = season_number.split()

        except KeyboardInterrupt:
            print(Fore.RESET + f'\n[+] Thank you for using...')
            exit()

        except Exception as e:
            self.display_title()
            self.select_season()

        # Download All Seasons
        if int(nums[0]) == 0:
            self.full_series = True

        # Go Back
        elif int(nums[0]) == -1:
            self.select_series_or_movie()
            self.select_season()

        # Exit
        elif int(nums[0]) == -9:
            os.system('CLS')
            exit()

        # Go To Episode Selection
        elif len(nums) == 1:
            self.selected_seasons.append(int(season_number) - 1)

        # Download Full Multiple Seasons
        else:
            self.full_seasons = True
            self.selected_seasons = [int(i) - 1 for i in nums]

    def select_episode(self):
        self.display_title()
        print(Fore.LIGHTYELLOW_EX + f"[+] Series : {self.selected_item['title']}")
        print(Fore.LIGHTYELLOW_EX + f"[+] Season : {self.selected_seasons[0] + 1}")
        print(Fore.LIGHTYELLOW_EX + f"[+] Episodes :")

        selected_season: dict = self.seasons[self.selected_seasons[0]]
        episodes = selected_season['episodes']
        for i, epi in enumerate(episodes, 1):
            print(f"\t{i}. {epi['epi_no']}-{epi['epi_name']}")

        print(Fore.RESET)
        print('[+] Enter Episode Number. Or')
        print('[+] Enter Episode Numbers Space Separated. Or')
        print('[+] Enter 0 To Download All')
        print('[+] Enter -1 To Go Back')
        print('[+] Enter -9 To Exit')
        question = {
            'type': 'input',
            'name': 'epi_no',
            'message': 'Enter Episode Number:',
            'validate': lambda val: all(
                [v in [*[str(i) for i in range(len(episodes) + 1)], str(-1), str(-2), str(-9)] for v in
                 val.split()])
        }

        selected_episodes = prompt(question)['epi_no'].strip().split()

        # All Episodes
        if int(selected_episodes[0]) == 0:
            self.selected_episodes = [i - 1 for i in range(1, len(episodes) + 1)]

        # Go Back
        elif int(selected_episodes[0]) == -1:
            self.select_season()
            self.select_episode()

        # Exit
        elif int(selected_episodes[0]) == -9:
            os.system('CLS')
            exit()

        # Multiple Episodes
        else:
            self.selected_episodes = [int(ep) - 1 for ep in selected_episodes]

    def set_save_path(self):
        """
        Get download path from user
        """
        try:
            print(
                Fore.LIGHTYELLOW_EX + '\n[!] Enter path to save episode. Just press enter to save episode in current directory.')
            path: str = input(Fore.YELLOW + '?' + Fore.RESET + ' Save Path (without file name) :').strip()

            if path:
                is_valid_path = os.path.isdir(path)

                if not is_valid_path:
                    os.mkdir(path)

                self.save_path = path

        except KeyboardInterrupt:
            os.system('CLS')
            exit()

        except OSError as e:
            print(Fore.RED + f'Error : {e}\n' + Fore.RESET)
            self.set_save_path()

    def download_series(self):

        def _start_download(tv, epi_page_link):
            episode_link_data = self.x265lk_object.extract_movie_or_episode_copy(tv, epi_page_link)
            if episode_link_data['response_code'] == 4:
                print(Fore.RESET + f'\n[+] Thank you for using...')
                exit()

            elif episode_link_data['response_code'] == 3 or episode_link_data['response_code'] == 5:
                print(Fore.RED + f'[+] Cannot download episode {i} ' + Fore.RESET)

            elif episode_link_data['response_code'] == 1:
                final_link_page_link = episode_link_data['data'][0]['url']

                final_link_data = self.x265lk_object.get_download_link(final_link_page_link)
                download_status = self.x265lk_object.download(final_link_data['data'], self.save_path)

                if download_status['response_code'] == 1:
                    print(Fore.GREEN + f"[+] Downloaded To {download_status['data']}" + Fore.RESET)

                elif download_status['response_code'] == 6:
                    print(Fore.RED + f'[+] Cannot download episode {i} ' + Fore.RESET)

                elif download_status['response_code'] == 4:
                    print(Fore.RESET + f'\n[+] Thank you for using...')
                    exit()

                else:
                    print(download_status['response_code'])
                    print(
                        Fore.RED + '[+] Something went wrong. Please Check URL Again And Check Your Internet Connection' + Fore.RESET)
                    exit()

        self.display_title()
        print(Fore.LIGHTYELLOW_EX + f"[+] Series   : {self.selected_item['title']}")

        # Full Series
        if self.full_series:
            self.set_save_path()
            for season in self.seasons:
                for i, episode in enumerate(season['episodes'], 1):
                    _start_download(True, episode['epi_link'])

        # Multiple Seasons
        elif self.full_seasons:
            seasons_to_display = ' '.join([str(i + 1) for i in self.selected_seasons])
            print(Fore.LIGHTYELLOW_EX + f"[+] Seasons  : {seasons_to_display}")
            self.set_save_path()
            for season in self.selected_seasons:
                selected_season = self.seasons[season]

                for i, episode in enumerate(selected_season['episodes'], 1):
                    _start_download(True, episode['epi_link'])

        # Download Multiple Episodes Of A Season
        else:
            print(Fore.LIGHTYELLOW_EX + f"[+] Season  : {self.selected_seasons[0] + 1}")
            episodes_to_display = ' '.join([str(i + 1) for i in self.selected_episodes])
            print(Fore.LIGHTYELLOW_EX + f"[+] Episodes : {episodes_to_display}\n")

            selected_season: dict = self.seasons[self.selected_seasons[0]]
            episodes: list[dict] = selected_season['episodes']

            self.set_save_path()

            for episode_no in self.selected_episodes:
                episode = episodes[episode_no]
                _start_download(True, episode['epi_link'])

    def download_movie(self):
        self.display_title()
        movie_title = self.selected_copy['movie'].title()
        copy_name = self.selected_copy['copy_name']
        print(Fore.LIGHTYELLOW_EX + f"[+] Movie : {movie_title}")
        print(Fore.LIGHTYELLOW_EX + f"[+] Copy  : {copy_name}")
        print(Fore.LIGHTYELLOW_EX + f"[+] Size  : {self.selected_copy['size']}")

        final_link_data = self.x265lk_object.get_download_link(self.selected_copy['url'])
        if final_link_data['response_code'] == 4:
            print(Fore.RESET + f'\n[+] Thank you for using...')
            exit()

        elif final_link_data['response_code'] == 3 or final_link_data['response_code'] == 5:
            print(
                Fore.RED + '[+] Something went wrong. Please Check URL Again And Check Your Internet Connection' + Fore.RESET)
            os.system('PAUSE')
            self.select_movie_copy()
            self.download_movie()
            return None

        elif final_link_data['response_code'] == 1:
            self.set_save_path()
            download_status = self.x265lk_object.download(final_link_data['data'], self.save_path)

            if download_status['response_code'] == 1:
                print(Fore.GREEN + f"[+] Downloaded To {download_status['data']}" + Fore.RESET)

            elif download_status['response_code'] == 6:
                print(Fore.RED + f"[+] Cannot download {movie_title} {copy_name}" + Fore.RESET)

            elif download_status['response_code'] == 4:
                print(Fore.RESET + f'\n[+] Thank you for using...')
                exit()

            else:
                print(download_status['response_code'])
                print(
                    Fore.RED + '[+] Something went wrong. Please Check URL Again And Check Your Internet Connection' + Fore.RESET)
                exit()


if __name__ == '__main__':
    x265lkcli = x265LkCli()
    series = dict()
    x265lkcli.mode_select()
    x265lkcli.get_search_result()
    x265lkcli.select_series_or_movie()

    if x265lkcli.mode == 'tvshows':
        x265lkcli.select_season()
        x265lkcli.select_episode()
        x265lkcli.download_series()
        print('Download')

        question = {
            'type': 'list',
            'name': 'ui',
            'message': 'What to do next?',
            'choices': [
                'Download Another Episode',
                'Search Movie',
                'Change Season',
                'Search TV Series',
                'Exit'
            ],
            'filter': lambda val: val.lower()
        }
        answer = prompt(question)['ui']

        if answer[0] == 'd':
            x265lkcli.select_episode()
            x265lkcli.download_series()

        elif answer[0] == 'c':
            x265lkcli.select_season()
            x265lkcli.select_episode()
            x265lkcli.download_series()

        elif answer.split()[1][0] == 'M':
            x265lkcli.get_search_result()
            x265lkcli.select_series_or_movie()
            x265lkcli.select_movie_copy()
            x265lkcli.download_movie()

        elif answer[0] == 's':
            x265lkcli.get_search_result()
            x265lkcli.select_series_or_movie()
            x265lkcli.select_season()
            x265lkcli.select_episode()
            x265lkcli.download_series()

        else:
            exit()

    else:
        x265lkcli.select_movie_copy()
        x265lkcli.download_movie()

        question = {
            'type': 'list',
            'name': 'ui',
            'message': 'What to do next?',
            'choices': [
                'Search Movie',
                'Search TV Series',
                'Exit'
            ],
            'filter': lambda val: val.lower()
        }

        answer = prompt(question)['ui']

        if answer[0] == 's':
            x265lkcli.get_search_result()
            x265lkcli.select_series_or_movie()
            x265lkcli.select_movie_copy()
            x265lkcli.download_movie()

        elif answer.split()[1][0] == 'T':
            x265lkcli.get_search_result()
            x265lkcli.select_series_or_movie()
            x265lkcli.select_season()
            x265lkcli.select_episode()
            x265lkcli.download_series()

        else:
            exit()

