import PySimpleGUI as sg
import subprocess
import json
import os
import animdl.core.config
import requests


def getNumberCaps()->int:
    url = 'https://graphql.anilist.co'
    query = '''
           query songImage($userPreferred: String, $type: MediaType) {
               Media (search : $userPreferred, type: $type) {
                   episodes
               }
           }
           '''
    variables = {
        'userPreferred': 'little witch academia tv',
        'type': 'ANIME'
    }
    response = requests.post(url, json={'query': query, 'variables': variables})
    print(response.json())
    return response.json()['data']['Media']['episodes']
def main():
    max = getNumberCaps()
    ind = 1
    x = ''
    salir = 0
    while True:
        for site in animdl.core.config.SITE_URLS:
            animdl.core.config.DEFAULT_CONFIG['default_provider'] = site
            print('grabbing cap ' + str(ind))
            print(animdl.core.config.DEFAULT_CONFIG['default_provider'])
            output = subprocess.run('animdl grab -r '+ str(ind) + ' --index 1 little-witch-academia',stdout=subprocess.PIPE,stderr=subprocess.DEVNULL).stdout.decode('utf-8')
            print(output)
            output = output[:output.rfind('}')+1]
            try:
                episode = json.loads(output)
                x += ' ' + episode['streams'][0]['stream_url']
                break
            except:
                pass
        ind += 1
        if ind > max:
            break

    os.system('mpv' + x)



    sg.theme('DarkAmber')

    layout = [[sg.Text('Some text on Row 1',key='-change-')],
              [sg.Text('Enter something on Row 2'), sg.InputText()],
              [sg.Button('Ok'), sg.Button('Cancel')]]

    #
    #
    #
    #window = sg.Window('reproductordeanimequepasadecapituloautomaticamente',layout)

    #while True:
    #   event, values = window.read()
    #   if event is not None and values is not None:
    #       window['-change-'].update(values[0])

    #    if event == sg.WIN_CLOSED or event == 'Cancel':  # if user closes window or clicks cancel
    #        break
    #window.close()
main()