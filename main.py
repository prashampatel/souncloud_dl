import os
import requests
import shutil
import eyed3
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import PySimpleGUI as sg

sg.theme('DarkGrey3')
layout = [[sg.Text('Enter a soundcloud link and hit GO!'), sg.Text(size=(15,1))],
          [sg.Input(key='-IN-')],
          [sg.Text(''), sg.Text(size=(5,10), key='-OUTPUT-')],
          [sg.Image(key="-IMAGE-")],
          [sg.Button('GO!'), sg.Button('Exit')]]

window = sg.Window('SoundCloud Downloader', layout)

def get_song_plus_cover(song):
    # get sc link as input
    # browser automation
    options = webdriver.ChromeOptions()
    options.add_extension('adblock.crx')
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    driver.set_window_size(75, 42)
    driver.get("https://scdownload.net/")
    search_bar = driver.find_element_by_name("sound-url")
    search_bar.clear()
    # search from input song
    search_bar.send_keys(song)
    search_bar.send_keys(Keys.RETURN)
    name = driver.find_element_by_id('title')
    # get name and artwork
    song_name = name.text
    window['-OUTPUT-'].update(song_name)
    with open('filename.png', 'wb') as file:
        file.write(driver.find_element_by_xpath('/html/body/div[1]/div/center[2]/table/tbody/tr[2]/td/img')
                   .screenshot_as_png)
    window['-IMAGE-'].update('filename.png')
    dlbutton = driver.find_element_by_id("manualDownload")
    dlbutton.click()
    popup_val = sg.popup_yes_no(f'Are you trying to download {song_name}?')
    print(popup_val)
    if popup_val == 'Yes':
        # download song
        dl_url = driver.current_url
        r = requests.get(dl_url)
        driver.quit()
        print(song_name)
        # format filex
        with open("song.mp3", 'wb') as f:
            f.write(r.content)
            audiofile = eyed3.load("song.mp3")
            if audiofile.tag == None:
                audiofile.initTag()

            audiofile.tag.images.set(3, open('filename.png', 'rb').read(), 'image/png')

            audiofile.tag.save()
            os.rename(r'song.mp3', rf'{song_name}')
            # put track in automatic dl folder
            # /Users/prashampatel/Music/Music/Media.localized/Automatically Add to Music.localized
            user_path = os.path.expanduser("~")
            shutil.move(f'{song_name}',
                        f'{user_path}/Music/Music/Media.localized/Automatically Add to Music.localized')
            os.remove('filename.png')
    else:
        window['-OUTPUT-'].update("Please enter a valid souncloud URL and try again")

while True:
    event, song = window.read()
    if event == sg.WIN_CLOSED or event == 'Exit':
        break
    if event == 'GO!':
        get_song_plus_cover(song['-IN-'])

window.close()



