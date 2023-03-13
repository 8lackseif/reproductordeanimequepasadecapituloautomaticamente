import PySimpleGUI as sg
import subprocess
import json
import os
import animdl.core.config
import requests

def getNumberCaps(anime: str)->int:
    url = 'https://graphql.anilist.co'
    query = '''
           query songImage($userPreferred: String, $type: MediaType) {
               Media (search : $userPreferred, type: $type) {
                   episodes
               }
           }
           '''
    variables = {
        'userPreferred': anime,
        'type': 'ANIME'
    }
    response = requests.post(url, json={'query': query, 'variables': variables})
    print(response.json())
    return response.json()['data']['Media']['episodes']

def getList(anime: str)-> list[str]:
    animeList = []
    anime = anime.replace(' ','-')
    output = subprocess.run('animdl search ' + anime, stdout=subprocess.PIPE,stderr=subprocess.PIPE).stderr.decode('utf-16')
    for line in output.splitlines():
        if line[0].isdigit():
            animeList.append(line[4:line.find('/')])
    return animeList

def play(firstCap: int, index: int, name:str):
    # calculate the range
    lastCap = getNumberCaps(name)
    if lastCap - firstCap + 1 > 25:
        lastCap = firstCap + 24
    #search for the caps
    list = ''
    while True:
        for site in animdl.core.config.SITE_URLS:
            animdl.core.config.DEFAULT_CONFIG['default_provider'] = site
            print('grabbing cap ' + str(firstCap))
            print(animdl.core.config.DEFAULT_CONFIG['default_provider'])
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
    os.system('mpv' + list)
def main():

    sg.theme('DarkAmber')

    layout = [[sg.Text('Some text on Row 1',key='-change-')],
              [sg.Text('Enter something on Row 2'), sg.InputText()],
              [sg.Button('Ok'), sg.Button('Cancel')]]

    window = sg.Window('reproductordeanimequepasadecapituloautomaticamente',layout)

    while True:
       event, values = window.read()
       if event is not None and values is not None:
           window['-change-'].update(values[0])

       if event == sg.WIN_CLOSED or event == 'Cancel':  # if user closes window or clicks cancel
            break
    window.close()



main()
