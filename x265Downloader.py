from x265lk import x265LK
from colorama import init, Fore
from PyInquirer import prompt
import argparse
import os


x265lk = x265LK()
mode = ''
init(convert=True)

# Full Series
# Full Season
# Many Full Seasons
# One or Many Episodes
# Movie

# x265lk <link> <path> -s <seasonNumbers> -e <epNumbers>

def display_movie_copy_and_download(copy):
    copy_name = copy['copy_name']
    copy_size = copy['size']
    url = copy['url']

    copy_download_link = x265lk.get_download_link(url)
    print(f'[+] Copy: {copy_name}')
    print(f'[+] Size: {copy_size}')
    print(f"[+] URL: {copy_download_link['data']}")
    res = x265lk.download(copy_download_link['data'], path)

    if res['response_code'] == 1:
        print(Fore.GREEN + f"[+] Downloaded To {res['data']}" + Fore.RESET)
    
    elif res['response_code'] == 6:
        print(Fore.RED + f'[!] Download Unsuccessful' + Fore.RESET)

    elif res['response_code'] == 4:
        print(Fore.RESET + f'\n[+] Thank you for using...')
        exit()
    
    else:
        print(Fore.RED + '[+] Somthing went wrong. Please Check URL Again And Check Your Internet Connection' + Fore.RESET)
        exit()


def display_episode_and_download(episode, ep_name, ep_no):
    ep_copy_name = episode['copy_name']
    ep_copy_size = episode['size']
    ep_copy_url = episode['url']
    print(f'\t\t{ep_no}.{ep_name} {ep_copy_name} {ep_copy_size}')

    ep_download_link = x265lk.get_download_link(ep_copy_url)

    print(f"\t\t\t[+] Final Link : {ep_download_link['data']}")
    res = x265lk.download(ep_download_link['data'], path)

    if res['response_code'] == 1:
        print(Fore.GREEN + f"[+] Downloaded To {res['data']}" + Fore.RESET)
    
    elif res['response_code'] == 6:
        print(Fore.RED + f'[!] Download Unsuccessful' + Fore.RESET)

    elif res['response_code'] == 4:
        print(Fore.RESET + f'\n[+] Thank you for using...')
        exit()
    
    else:
        print(Fore.RED + '[+] Somthing went wrong. Please Check URL Again And Check Your Internet Connection' + Fore.RESET)
        exit()


def display_season(season, sn):   
    print(f'\n\t[+] Season : {sn}')
    episodes = season['episodes']
    for episode in episodes:
        ep_no = episode['epi_no']
        ep_name = episode['epi_name']
        ep_copy_response = x265lk.extract_movie_or_episode_copy(True, link=episode['epi_link'])

        if ep_copy_response['response_code'] == 1:
            ep_copy_data = ep_copy_response['data'][0]
            display_episode_and_download(ep_copy_data, ep_name, ep_no)

        elif ep_copy_response['response_code'] == 4:
            print(Fore.RESET + f'\n[+] Thank you for using...')
            exit()

        else:
            print(Fore.RED + '[+] Somthing went wrong. Please Check URL Again And Check Your Internet Connection' + Fore.RESET)
            exit()   


parser = argparse.ArgumentParser(
    description='x265lk.com Terminal Downloader',
    prog='x265lk',
    usage='%(prog)s LINK PATH [-s <seasonNumbers>] [-e <episodeNumbers>] ',
    epilog='By Hirusha Fernando'
)

parser.add_argument('LINK', type=str, help='Movie Or TV Series Link')
parser.add_argument('PATH', type=str, nargs='?', help='Download Location Path')
parser.add_argument('-s', type=str, metavar='SeasonNumbers', dest='sNums', help='Season Numbers To Download')
parser.add_argument('-e', type=str, metavar='EpisodeNumbers,', dest='eNums', help='Episode Numbers To Download')

args = parser.parse_args()

path = args.PATH 
link = args.LINK

if path and (not os.path.isdir(path)):
    print(Fore.RED + '[!] Invalid Path' + Fore.RESET)
    exit()
else:
    path = os.getcwd()

seasonNumbers = args.sNums.split(',') if args.sNums else False
episodeNumbers = args.eNums.split(',') if args.eNums else False

isValidated = lambda nums: all([ x.isdigit() for x in nums ])

if args.eNums and (not args.sNums):
    parser.print_help()
    exit()

if args.eNums and (not isValidated(episodeNumbers)):
    parser.print_help()
    exit()

if args.sNums and (not isValidated(seasonNumbers)):
    parser.print_help()
    exit()

if 'tvshows' in link:
    # Download Full Series
    if not args.sNums:
        print('[+] Extracting Links')
        seasons_response = x265lk.extract_seasons(link)
        
        if seasons_response['response_code'] == 1:
            series_name = ' '.join(link.split('/')[-2].split('-')).title()
            print(f'\n[+] TV Series : {series_name}')
            seasons_data = seasons_response['data']
            for season in seasons_data:
                sn = season['season_no']
                display_season(season, sn)

        elif seasons_response['response_code'] == 4:
            print(Fore.RESET + f'\n[+] Thank you for using...')
            exit()

        else:
            print(Fore.RED + '[+] Somthing went wrong. Please Check URL Again And Check Your Internet Connection' + Fore.RESET)
            exit()

    # Download Full Multiple Or Single Seasons
    if args.sNums and (not args.eNums):
        print('[+] Extracting Links')
        seasons_response = x265lk.extract_seasons(link)

        if seasons_response['response_code'] == 1:
            series_name = ' '.join(link.split('/')[-2].split('-')).title()
            print(f'\n[+] TV Series : {series_name}')
            seasons_data = seasons_response['data']
            for n in seasonNumbers:            
                sn = f'Season {n}'
                try:
                    season = seasons_data[int(n) - 1]
                    display_season(season, sn)

                except IndexError:
                    print(Fore.RED + f'\n\t[!] Could not find {series_name} Season {n}' + Fore.RESET)

        elif seasons_response['response_code'] == 4:
            print(Fore.RESET + f'\n[+] Thank you for using...')
            exit()

        else:
            print(Fore.RED + '[+] Somthing went wrong. Please Check URL Again And Check Your Internet Connection' + Fore.RESET)
            exit()

    # Download Multiple Or Single Episodes Of A Season
    if args.eNums and args.sNums and len(seasonNumbers) == 1:
        print('[+] Extracting Links')
        seasons_response = x265lk.extract_seasons(link)

        if seasons_response['response_code'] == 1:
            series_name = ' '.join(link.split('/')[-2].split('-')).title()
            print(f'\n[+] TV Series : {series_name}')
            seasons_data = seasons_response['data']
            n = seasonNumbers[0]
            season = seasons_data[int(n) - 1]
            print(f'\n\t[+] Season : {n}')
            episodes = season['episodes']

            for ep in episodeNumbers:
                try:
                    episode = episodes[int(ep) - 1]
                    ep_no = episode['epi_no']
                    ep_name = episode['epi_name']
                    ep_copy_response = x265lk.extract_movie_or_episode_copy(True, link=episode['epi_link'])

                    if ep_copy_response['response_code'] == 1:
                        ep_copy_data = ep_copy_response['data'][0]
                        display_episode_and_download(ep_copy_data, ep_name, ep_no)

                    elif ep_copy_response['response_code'] == 4:
                        print('[+] Thank you for using...')
                        exit()

                    else:
                        print(Fore.RED + '[+] Somthing went wrong. Please Check URL Again And Check Your Internet Connection' + Fore.RESET)
                        exit()

                except IndexError:
                    print(Fore.RED + f'\n\t\t[!] Could not find {series_name} Season {n} Episode {ep}\n' + Fore.RESET)

        elif seasons_response['response_code'] == 4:
            print(Fore.RESET + f'\n[+] Thank you for using...')
            exit()

        else:
            print(Fore.RED + '[+] Somthing went wrong. Please Check URL Again And Check Your Internet Connection' + Fore.RESET)
            exit()

    if args.eNums and args.sNums and len(seasonNumbers) != 1:
        parser.print_help()
        exit()


elif 'movies' in link:
    movie_title = ' '.join(link.split('/')[-2].split('-')).title()
    movie_response = x265lk.extract_movie_or_episode_copy(False, link=link)
    
    if movie_response['response_code'] == 1:
        copy_data = movie_response['data']
        print(f'\n[+] Movie: {movie_title}')

        if len(copy_data) == 1:
            copy = copy_data[0]
            display_movie_copy_and_download(copy)            

        else:
            copies = [f"{i}. {copy['copy_name']} {copy['size']}" for i, copy in enumerate(copy_data, 1)]            

            try:
                question = { 
                    'type': 'list', 
                    'name': 'copy', 
                    'message': 'Select One Of These Copies:', 
                    'choices': copies 
                }
                n = int(prompt(question)['copy'].split('.')[0]) - 1
                selected_copy = copy_data[n]
                print(f'\n[+] Movie: {movie_title}')
                display_movie_copy_and_download(selected_copy)
            except KeyError:
                print(Fore.RESET + f'\n[+] Thank you for using...')
                exit()

    elif movie_response['response_code'] == 4:
        print(Fore.RESET + f'\n[+] Thank you for using...')
        exit()



