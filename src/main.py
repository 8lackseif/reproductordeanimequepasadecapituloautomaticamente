import threading

import PySimpleGUI as sg
import subprocess
import json
import os
import animdl.core.config
import requests

capitulos = {

}
def getNumberCaps(anime: str)->int:
    #if it is a movie
    if "Movie" in anime:
        print("is a movie")
        return 1

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
    if response.json()['data']['Media']['episodes'] is None:
        return 0
    return response.json()['data']['Media']['episodes']

def getList(anime: str)-> list[str]:
    animeList = []
    anime = anime.replace(' ','-')
    output = subprocess.run('animdl search ' + anime, stdout=subprocess.PIPE,stderr=subprocess.PIPE).stderr.decode('utf-8')
    for line in output.splitlines():
        if line[0].isdigit():
            animeList.append(line[3:line.find('/') - 1])
    return animeList

def scrap(currentEpisode: int, index: int, animeName: str):
    for site in animdl.core.config.SITE_URLS:
        animdl.core.config.DEFAULT_CONFIG['default_provider'] = site
        output = subprocess.run('animdl grab -r ' + str(currentEpisode) + ' --index ' + str(index) + ' ' + animeName,
                                stdout=subprocess.PIPE, stderr=subprocess.DEVNULL).stdout.decode('utf-8')
        output = output[:output.rfind('}') + 1]
        try:
            episode = json.loads(output)
            capitulos[currentEpisode] = episode['streams'][0]['stream_url']
            break
        except:
            pass

def play(firstCap: int, index: int, searchName:str, realName: str):
    # calculate the range
    lastCap = getNumberCaps(realName)
    list = ''
    threads = []
    if lastCap - (firstCap + 1) > 25:
        lastCap = firstCap + 24

    animeName = searchName.replace(' ','-')

    for i in range(firstCap, lastCap + 1):
        threads.append(threading.Thread(target=scrap, args=(i,index,animeName)))
        threads[len(threads) - 1].start()

    for t in threads:
        t.join()

    for i in range(firstCap, lastCap + 1):
        list += ' ' + capitulos[i]
    #play
    if len(list) == 0:
        print("failed grabbing stream urls")
    else:
        os.system('mpv' + list)

def mainWindow():

    sg.theme('DarkAmber')

    search_column = [
        [sg.InputText(size=(55,1), key="-ANIME-"), sg.Button("Search",size=(5,1))],
        [sg.Listbox(values=[],enable_events=True,size=(60,20),key="-SEARCH-")]
    ]

    cap_column = [
        [sg.Text("caps list: ", key="-TITLE-")],
        [sg.Listbox(values=[],enable_events=True,size=(40,20),key="-CAPS-")]
    ]

    layout = [
        [sg.Column(search_column),sg.VSeperator(),sg.Column(cap_column)]
    ]

    window = sg.Window('reproductordeanimequepasadecapituloautomaticamente',layout)

    searchContent = ""
    currentAnime = ""
    currentAnimeList = []
    currentIndex = 0
    isPlaying = False

    while True:
        # read events on GUI
        event, values = window.read()
        # windows closed finish task
        if event == sg.WIN_CLOSED:
            break
        # anime searched display search results
        elif event == "Search":
            searchContent = values["-ANIME-"]
            currentAnimeList = getList(values["-ANIME-"])
            window.Element("-SEARCH-").update(currentAnimeList)
        #anime selected display episodes
        elif event == "-SEARCH-":
            currentAnime = values[event][0]
            #update episodes box title
            window["-TITLE-"].update(currentAnime + ": ")
            caps = getNumberCaps(values[event][0])
            episodes = []
            for i in range(1,caps + 1):
                episodes.append("episode " + str(i))
            #updates episodes box
            window["-CAPS-"].update(episodes)
        #episode selected start play
        elif event == "-CAPS-":
            i = 0
            for n in currentAnimeList:
                i += 1
                if currentAnime == n:
                    currentIndex = i
                    break
            if isPlaying:
                pass
            else:
                play(int(values[event][0][values[event][0].rfind(' ')+1:len(values[event][0])]), currentIndex, searchContent, currentAnime)

    window.close()

if __name__ == '__main__':
    mainWindow()


