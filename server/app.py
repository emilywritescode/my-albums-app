import requests

import config
import calendar

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

from flask import Flask, request, json, make_response, jsonify

import albums
import artists

import mysql.connector

app = Flask(__name__)


#  API: Insert a new album into database
@app.route('/api/insertalbum', methods=['POST'])
def insertAlbum():
    return albums.insert_album(request.get_json())


#  API: Get album details by calling music APIs
@app.route('/api/getalbumdetails/<path:album>/<path:artist>', methods=['GET'])
def getAlbumDetails(album, artist, api_call=True):
    return albums.get_album_details(album, artist, api_call)


#  API: Fetch all tables from the database
@app.route('/api/gettables', methods=['GET'])
def getTables():
    try:  # connecting to MySQL database
        conn = mysql.connector.connect(user=config.mysqluser, password=config.mysqlpass, host=config.mysqlhost, database=config.mysqldb)
        cursor = conn.cursor(buffered=True)
    except Exception as e:
        print(f'Error with connecting to db: {str(e)}')
        return jsonify("Issue connecting to database")

    try:  # calling stored procedure
        data = cursor.callproc('getTables',)
    except Exception as e:
        return make_response(f'mysql getTables error: {str(e)}', 404)

    data = []
    for result in cursor.stored_results():
        data = result.fetchall()

    if len(data) == 0:
        return make_response('error occurred when fetching tables', 404)
    else:
        conn.commit()
        res_dict = []
        for row in data:
            row_dict = {
                'Name' : row[0],
                'NumAlbums' : row[1],
                'Year': str(row[0])[-4:]
            }
            res_dict.append(row_dict)
        return jsonify(res_dict)


#  API: Fetch year of albums from a table in the database
@app.route('/api/getalbums/<table>', methods=['GET'])
def getAlbums(table, api_call=True):
    try:  # connecting to MySQL database
        conn = mysql.connector.connect(user=config.mysqluser, password=config.mysqlpass, host=config.mysqlhost, database=config.mysqldb)
        cursor = conn.cursor(buffered=True)
    except Exception as e:
        print(f'Error with connecting to db: {str(e)}')
        return jsonify("Issue connecting to database")

    try:  # calling stored procedure
        cursor.callproc('getAlbums', (table,))
    except Exception as e:
        return make_response(f'mysql getAlbums error: {str(e)}', 404)

    data = []
    for result in cursor.stored_results():
        data = result.fetchall()

    if len(data) == 0:
        return make_response(f'error occurred when fetching albums for {table}', 404)
    else:
        res_dict = []
        for row in data:
            row_dict = {
                'Month' : calendar.month_name[row[0]],
                'Day' : row[1],
                'Album' : row[2],
                'Artist' : row[3],
                'Release_Year' : row[4]
            }
            res_dict.append(row_dict)
        if api_call:
            return jsonify(res_dict)
        else:
            return res_dict


#  API: Get stats about a listen year from the database
@app.route('/api/getstats/<table>', methods=['GET'])
def getStats(table):
    if table not in config.valid_table_years:
        return make_response('Invalid year', 404)

    year = int(table.split('albums_')[1])

    try:  # connecting to MySQL database
        conn = mysql.connector.connect(user=config.mysqluser, password=config.mysqlpass, host=config.mysqlhost, database=config.mysqldb)
        cursor = conn.cursor(buffered=True)
    except Exception as e:
        print(f'Error with connecting to db: {str(e)}', 404)
        return jsonify("Issue connecting to database")

    try:  # calling stored procedure
        cursor.callproc('getStats', (year,))
    except Exception as e:
        return make_response(f'mysql getStats error: {str(e)}', 404)

    data = []
    for result in cursor.stored_results():
        data = result.fetchall()
        print(data)

    if data[0][14] is None:  # time listened
        print('time listened in stats are not updated! printing out for manual updating')
        print(getYearlyTimeListened(table))
        return make_response('need to update stats...', 404)

    if data[0][5] is None or data[0][10] is None:  #  album covers
        print('covers in stats are not updated! printing out for manual updating...')
        first_listened_album = [x.strip() for x in data[0][1].split(',')]
        first_listened_artist = [x.strip() for x in data[0][2].split(',')]
        last_listened_album = [x.strip() for x in data[0][6].split(',')]
        last_listened_artist = [x.strip() for x in data[0][7].split(',')]
        get_covers_for_stats(first_listened_album, first_listened_artist, last_listened_album, last_listened_artist)
        return make_response('need to update stats...', 404)


    ''' in MySQL db, stats:
    year,
    first listened: album, artist, month, day, cover_image
    last listened: album, artist, month, day, cover_image
    top artist, number of albums, total time in days, hours, minutes, seconds (starting with highest possible)
    '''

    stats = data[0]

    res_dict = {
        'Table_Year': stats[0],
        'First_Listened_Album': [x.strip() for x in stats[1].split(',')],
        'First_Listened_Artist': [x.strip() for x in stats[2].split(',')],
        'First_Listened_Month': calendar.month_name[stats[3]],
        'First_Listened_Day': stats[4],
        'First_Listened_Cover': [x.strip() for x in stats[5].split(',')],
        'Last_Listened_Album': [x.strip() for x in stats[6].split(',')],
        'Last_Listened_Artist': [x.strip() for x in stats[7].split(',')],
        'Last_Listened_Month': calendar.month_name[stats[8]],
        'Last_Listened_Day': stats[9],
        'Last_Listened_Cover': [x.strip() for x in stats[10].split(',')],
        'Top_Artist': [x.strip() for x in stats[11].split(',')],
        'Top_Num': stats[12],
        'Total_Albums': stats[13],
        'Total_Time': convertMilliseconds(stats[14])
    }

    print(res_dict)
    return jsonify(res_dict)


def get_covers_for_stats(first_listened_album, first_listened_artist, last_listened_album, last_listened_artist):

    first_listened_cover = []
    for i in range(len(first_listened_album)):
        first_listened_cover.append(albums.get_album_details(first_listened_album[i],  first_listened_artist[i], False)['CoverArt'])

    last_listened_cover = []
    for i in range(len(last_listened_album)):
        last_listened_cover.append(albums.get_album_details(last_listened_album[i], last_listened_artist[i], False)['CoverArt'])

    first_covers = ','.join(cover for cover in first_listened_cover)
    last_covers = ','.join(cover for cover in last_listened_cover)

    print(first_covers)
    print(last_covers)


#  Calculate total duration in milliseconds of all albums in listen year
def getYearlyTimeListened(table):
    time = 0

    table_albums = getAlbums(table, api_call=False)

    for album in table_albums:
        title = album['Album']
        artist = album['Artist']
        print(f'{title}, {artist}')
        sp_search = albums.spotify_search_album(title, artist)
        if sp_search['albums']['total'] == 0:
            try:  # splice album title and try Spotify search again
                sp_search = albums.spotify_search_album(album_slice(title), artist)
            except Exception as e:
                print(f'failure to splice search for {title}')
                continue

        try:
            sp_album_id = sp_search['albums']['items'][0]['id']
        except Exception as e1:
            print(f'failure to spotify search for {title}')
            continue

        tracks = albums.spotify_get_album_tracks(sp_album_id)

        for track in tracks:
            time += track['duration_ms']

    print(f'Total of {time} milliseconds')
    return time


def convertMilliseconds(milliseconds):
    time_string = []

    if milliseconds / 86400000 >= 1:  # days
        time_string.append(str(milliseconds // 86400000) + ' days')
        milliseconds = milliseconds % 86400000
    if milliseconds / 3600000 >= 1:  # hours
        time_string.append(str(milliseconds // 3600000) + ' hours')
        milliseconds = milliseconds % 3600000
    if milliseconds / 60000 >= 1:  # minutes
        time_string.append(str(milliseconds // 60000) + ' minutes')
        milliseconds = milliseconds % 60000
    if milliseconds / 1000 >= 1:  # seconds
        time_string.append(str(milliseconds // 1000) + ' seconds')
        milliseconds = milliseconds % 1000
    return ' '.join(time_string)


@app.route('/api/getartist/<path:artist>', methods=['GET'])
def getArtist(artist):
    return artists.get_artist(artist)


if __name__ == '__main__':
    app.run(debug=True, port=8080)
