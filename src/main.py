import asyncio
import json

import PySimpleGUI as sg
import subprocess
import animdl.core.config
import requests
import animdl.core.cli.helpers.searcher as search
from animdl.core.cli.http_client import client

def getNumberCaps(anime: str) -> int:
    # if it is a movie
    if "Movie" in anime:
        return 1

    if "Part" in anime and ":" in anime:
        if "Part" in anime[:anime.find(":")]:
            anime = anime[:anime.find("Part")] + anime[anime.rfind(":"):]

    url = 'https://graphql.anilist.co'
    query = '''
           query episodes($userPreferred: String, $type: MediaType) {
               Media (search : $userPreferred, type: $type) {
                   title{
                        userPreferred
                   }
                   episodes
               }
           }
           '''
    variables = {
        'userPreferred': anime,
        'type': 'ANIME'
    }

    response = requests.post(url, json={'query': query, 'variables': variables})
    if response.status_code == 404 or response.json()['data']['Media']['episodes'] is None:
        return 0
    return response.json()['data']['Media']['episodes']


async def getList(anime: str) -> list[str]:
    animeList = []
    player = search.provider_searcher_mapping.get(animdl.core.config.DEFAULT_CONFIG['default_provider'])(client,anime)
    for x in player:
        animeList.append(x["name"])
    return animeList

async def scrap(currentEpisode: int, index: int, animeName: str, file):
    for site in animdl.core.config.SITE_URLS:
        animdl.core.config.DEFAULT_CONFIG['default_provider'] = site
        subprocess.run('animdl grab -r ' + str(currentEpisode) + ' --index ' + str(index) + ' ' + animeName,
                                shell=True, stdout=file,stderr=subprocess.DEVNULL)
        try:
            break
        except:
            pass


async def play(firstCap: int, index: int, searchName: str, realName: str):
    # calculate the range
    lastCap = getNumberCaps(realName)
    if lastCap - (firstCap + 1) > 25:
        lastCap = firstCap + 24

    animeName = searchName.replace(' ', '-')

    sg.Popup('Warning', 'The program will now start scraping. This may take a while.')

    with open("episodes.txt", "w") as file:
        for i in range(firstCap, lastCap + 1):
            await scrap(i,index,animeName,file)

    with open("episodes.txt","r") as r:
        data = '{ "episodes": ['
        counter = 1

        for x in r.read().splitlines():
            if counter != 1:
                if x.find("{") != -1:
                    data += ','+ x
            else:
                data += x
            counter += 1

        data += ']}'

        episodes = json.loads(data)
        with open("playlist.m3u", "w") as f:
            j = 0
            for i in range(firstCap, lastCap + 1):
                try:
                    if i == episodes['episodes'][j]['episode']:
                        f.write(f"#EXTINF:-1,episode " + str(i) + "\n")
                        f.write(f"" + episodes['episodes'][j]['streams'][0]['stream_url'] + "\n")
                except:
                    pass
                j+=1
            # play
            player = await asyncio.create_subprocess_exec('mpv', '--no-terminal', 'playlist.m3u',
                                                          stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.DEVNULL)


async def mainWindow():
    sg.theme('DarkAmber')

    search_column = [
        [sg.InputText(size=(50, 1), key="-ANIME-"), sg.Button("Search", size=(8, 1))],
        [sg.Listbox(values=[], enable_events=True, size=(60, 20), key="-SEARCH-")]
    ]

    cap_column = [
        [sg.Text("caps list: ", size=(30, 1), key="-TITLE-", expand_x=True)],
        [sg.Listbox(values=[], enable_events=True, size=(40, 20), key="-CAPS-")]
    ]

    layout = [
        [sg.Column(search_column), sg.VSeperator(), sg.Column(cap_column)]
    ]

    window = sg.Window('reproductordeanimequepasadecapituloautomaticamente', layout, font=('Arial', 11))

    searchContent = ""
    currentAnime = ""
    currentAnimeList = []
    currentIndex = 0

    while True:
        # read events on GUI
        event, values = window.read()
        # windows closed finish task
        if event == sg.WIN_CLOSED:
            break
        # anime searched display search results
        elif event == "Search":
            try:
                searchContent = values["-ANIME-"]
                currentAnimeList = await getList(values["-ANIME-"])
                window.Element("-SEARCH-").update(currentAnimeList)
            except:
                pass
        # anime selected display episodes
        elif event == "-SEARCH-":
            try:
                currentAnime = values[event][0]
                # update episodes box title
                window["-TITLE-"].update(currentAnime + ": ")
                caps = getNumberCaps(values[event][0])
                episodes = []
                for i in range(1, caps + 1):
                    episodes.append("episode " + str(i))
                # updates episodes box
                window["-CAPS-"].update(episodes)
            except:
                pass
        # episode selected start play
        elif event == "-CAPS-":
            i = 0
            for n in currentAnimeList:
                i += 1
                if currentAnime == n:
                    currentIndex = i
                    break
            try:
                await play(int(values[event][0][values[event][0].rfind(' ') + 1:len(values[event][0])]), currentIndex,
                           searchContent, currentAnime)
            except:
                pass
    window.close()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(mainWindow())
