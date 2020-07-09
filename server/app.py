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
    if table == config.latest_year:
        return make_response(f'Invalid year', 404)

    year = int(table.split('albums_')[1])

    try:  # connecting to MySQL database
        conn = mysql.connector.connect(user=config.mysqluser, password=config.mysqlpass, host=config.mysqlhost, database=config.mysqldb)
        cursor = conn.cursor(buffered=True)
    except Exception as e:
        print(f'Error with connecting to db: {str(e)}')
        return jsonify("Issue connecting to database")

    try:  # calling stored procedure
        cursor.callproc('getStats', (year,))
    except Exception as e:
        return make_response(f'mysql getStats error: {str(e)}', 404)

    data = []
    for result in cursor.stored_results():
        data = result.fetchall()

    if data[0][12] is None:
        print('stats are not updated! trying again...')
        update_stats(table, year)

        try:  # calling stored procedure again
            conn = mysql.connector.connect(user=config.mysqluser, password=config.mysqlpass, host=config.mysqlhost, database=config.mysqldb)
            cursor = conn.cursor(buffered=True)
            cursor.callproc('getStats', (year,))
        except Exception as e:
            return make_response(f'mysql getStats error: {str(e)}', 404)

        data = []
        for result in cursor.stored_results():
            data = result.fetchall()

    ''' in MySQL db, stats:
    year,
    first listened: album, artist, month, day,
    last listened: album, artist, month, day,
    top artist, number of albums, total time in milliseconds
    '''

    stats = data[0]
    res_dict = {
        'Year': stats[0],
        'First_Listened_Album': stats[1].split(','),
        'First_Listened_Artist': stats[2].split(','),
        'First_Listened_Month': calendar.month_name[stats[3]],
        'First_Listened_Day': stats[4],
        'Last_Listened_Album': stats[5].split(','),
        'Last_Listened_Artist': stats[6].split(','),
        'Last_Listened_Month': calendar.month_name[stats[7]],
        'Last_Listened_Day': stats[8],
        'Top_Artist': stats[9].split(','),
        'Top_Num': stats[10],
        'Total_Albums': stats[11],
        'Total_Time': convertMilliseconds(stats[12])
    }

    print(res_dict)
    return jsonify(res_dict)


def update_stats(table, year):
    milliseconds = getYearlyTimeListened(table)

    try:  # connecting to MySQL database
        conn = mysql.connector.connect(user=config.mysqluser, password=config.mysqlpass, host=config.mysqlhost, database=config.mysqldb)
        cursor = conn.cursor(buffered=True)
    except Exception as e:
        print(f'Error with connecting to db: {str(e)}')
        return jsonify("Issue connecting to database")

    try:  # calling stored procedure
        args = (year, milliseconds)
        print(args)

        cursor.callproc('updateStats', args)
        print(f'updated stats for {year} successfully')
    except Exception as e:
        print(f'Error with updating stats for {year}: {str(e)}')

    conn.commit()
    conn.close()


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
