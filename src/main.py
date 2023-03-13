import PySimpleGUI as sg
import subprocess
import json
import os
import animdl.core.config
import requests

def getNumberCaps(anime: str)->int:
    #if it is a movie
    if "Movie" in anime:
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

def play(firstCap: int, index: int, name:str):
    # calculate the range
    lastCap = getNumberCaps(name)
    if lastCap - (firstCap + 1) > 25:
        lastCap = firstCap + 24
    #search for the caps
    list = ''
    while True:
        for site in animdl.core.config.SITE_URLS:
            animdl.core.config.DEFAULT_CONFIG['default_provider'] = site
            print('grabbing cap ' + str(firstCap) + ' from ' + animdl.core.config.DEFAULT_CONFIG['default_provider'])
            output = subprocess.run('animdl grab -r ' + str(firstCap) + ' --index ' + str(index) + ' ' + name.replace(' ','-'),
                                    stdout=subprocess.PIPE, stderr=subprocess.DEVNULL).stdout.decode('utf-8')
            output = output[:output.rfind('}') + 1]
            try:
                episode = json.loads(output)
                list += ' ' + episode['streams'][0]['stream_url']
                break
            except:
                pass
        firstCap += 1
        if firstCap > lastCap:
            break
    #play
    if len(list) == 0:
        print("failed grabbing stream urls")
    else:
        os.system('mpv' + list)
def main():

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

    currentAnime = ""
    currentAnimeList = []
    currentIndex = 0

    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED:
            break
        elif event == "Search":
            currentAnimeList = getList(values["-ANIME-"])
            window.Element("-SEARCH-").update(currentAnimeList)
        elif event == "-SEARCH-":
            currentAnime = values[event][0]
            window["-TITLE-"].update(currentAnime + ": ")
            caps = getNumberCaps(values[event][0])
            episodes = []
            for i in range(1,caps + 1):
                episodes.append("episode " + str(i))
            window["-CAPS-"].update(episodes)
        elif event == "-CAPS-":
            for n in currentAnimeList:
                if currentAnime == n:
                    currentIndex = n
                    break
            play(int(values[event][0][len(values[event][0])-1]), currentIndex, currentAnime)

    window.close()



main()
