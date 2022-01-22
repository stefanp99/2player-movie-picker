import ctypes
import json
import webbrowser
import PySimpleGUIQt as sg
import random
import textwrap
from PIL import Image, ImageTk
import requests
import io
import socket
import pickle
import threading


def get_img_data(f, maxsize=(400, 450), first=False):
    img = Image.open(f)
    img.thumbnail(maxsize)
    if first:
        bio = io.BytesIO()
        try:
            img.save(bio, format="PNG")
        except OSError:
            return
        del img
        return bio.getvalue()
    return ImageTk.PhotoImage(img)


def print_on_screen(show, total_shows, after_like=False):
    if not after_like:
        layout = [
            [sg.Text(f'{len(skipped_shows) + len(liked_shows) + 1}/{total_shows}', background_color='transparent')]]
    else:
        layout = [[sg.Text(f'{len(skipped_shows) + len(liked_shows)}/{total_shows}', background_color='transparent')]]
    buttons = [sg.Button('Next'), sg.Button('Open IMDB page')]
    if not after_like:
        buttons.append(sg.Button('Like'))
    if show['trailer']:
        buttons.append(sg.Button('Open Trailer'))
    layout.append(buttons)
    output = f"Name: {show['name']} ({show['year']})\n\n"
    output += 'Genre: '
    for genre in show['genre']:
        output += genre + ', '
    output = output[:-2]
    output += f"\n\nRating: {show['rating']['ratingValue']} ({show['rating']['ratingCount']})\n\n"
    output += f"Actors:\n"
    for actor in show['actors']:
        output += f"{actor['name']}\n"
    description = textwrap.fill(show['description'], 92)
    output += '\n\nDescription:\n'
    output += f"{description}\n\n"
    response = requests.get(show['image'], stream=True)
    img_data = get_img_data(response.raw, first=True)
    layout += [[sg.Text(output, background_color='transparent')], [sg.Image(data=img_data, pad=(215, 0))]]
    window = sg.Window('ranShow', layout, size=(755, 931), background_image='photo.jpeg',
                       background_color='#57605b',
                       location=((user32.GetSystemMetrics(0)) / 2 - 200, 0)).Finalize()
    event, values = window.read()
    while event != 'Next':
        if event == sg.WINDOW_CLOSED:
            window.close()
            return -1
        if event == 'Open IMDB page':
            webbrowser.open(show['url'])
        if event == 'Open Trailer':
            webbrowser.open(show['trailer'])
        if event == 'Like':
            liked_shows.append(show['name'])
            window.close()
            return 0
        event, values = window.read()
    if not after_like:
        skipped_shows.append(show)
    window.close()
    return 0


def get_show(shows_array, event):
    while event != sg.WINDOW_CLOSED and len(shows_array) > len(skipped_shows) + len(liked_shows):
        show = random.choice(shows_array)
        while show in skipped_shows:
            show = random.choice(shows_array)
        if print_on_screen(show, len(shows_array)) == -1:
            break


def get_common_shows():
    common_shows.append(pickle.loads(sock.recv(1024)))


genres = []
with open('movie_db.json', 'r') as file:
    data = json.load(file)
    i = 0
    for show in data:
        i += 1
        for genre in show['genre']:
            if genre not in genres:
                genres.append(genre)
genres = sorted(genres)
user32 = ctypes.windll.user32
layout = [[sg.Text('Choose genre: ', background_color='transparent')]]
for genre in genres:
    layout.append([sg.Checkbox(f'{genre}', background_color='transparent')])
layout.append([sg.Button('Submit')])
window = sg.Window('ranShow', layout, size=(755, 931), background_image='photo_andreia_755x931.jpeg',
                   background_color='#57605b', location=((
                                                             user32.GetSystemMetrics(0)) / 2,
                                                         0)).Finalize()
chosen_genres = []
liked_shows = []
skipped_shows = []
event, values = window.read()
while event != sg.WINDOW_CLOSED:
    if event == 'Submit':
        for i in range(len(values)):
            if values[i]:
                chosen_genres.append(genres[i])
        break
    event, values = window.read()
shows = []
if chosen_genres:
    for show in data:
        for genre in show['genre']:
            if genre in chosen_genres:
                shows.append(show)
                break
    window.close()
    get_show(shows, event)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('192.168.0.105', 12345))
data = pickle.dumps(liked_shows)
sock.send(data)

common_shows = []
thread = threading.Thread(target=get_common_shows)
thread.start()
waiting_layout = [[sg.Text('Please wait, while your friend is choosing shows', background_color='transparent')],
                  [sg.Text('You can close this window', background_color='transparent')]]
waiting_window = sg.Window('ranShow', waiting_layout, size=(755, 931), background_image='photo_andreia_755x931.jpeg',
                           background_color='#57605b', location=((
                                                                     user32.GetSystemMetrics(0)) / 2 - 200,
                                                                 0)).Finalize()
while not common_shows:
    event_waiting, values_waiting = waiting_window.read()
waiting_window.hide()
common_shows = common_shows[0]

liked_shows = []
skipped_shows = []
exit_loop = False
for show_name in common_shows:
    for show in shows:
        if show['name'] == show_name:
            liked_shows.append(show)
            if print_on_screen(show, len(common_shows), after_like=True) == -1:
                exit_loop = True
                break
        if exit_loop:
            break
sock.close()
