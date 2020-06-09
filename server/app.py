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
    try:
        conn = mysql.connector.connect(user=config.mysqluser, password=config.mysqlpass, host=config.mysqlhost, database=config.mysqldb)
        cursor = conn.cursor(buffered=True)
    except Exception as e:
        print(f'Error with connecting to db: {str(e)}')
        return jsonify("Issue connecting to database")

    try:
        data = cursor.callproc('getTables',)
    except Exception as e:
        return make_response(f'mysql getTables error: {str(e)}', 404)

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
    try:
        conn = mysql.connector.connect(user=config.mysqluser, password=config.mysqlpass, host=config.mysqlhost, database=config.mysqldb)
        cursor = conn.cursor(buffered=True)
    except Exception as e:
        print(f'Error with connecting to db: {str(e)}')
        return jsonify("Issue connecting to database")

    try:
        data = cursor.callproc('getAlbums', (table,))
    except Exception as e:
        return make_response(f'mysql getAlbums error: {str(e)}', 404)

    for result in cursor.stored_results():
        data = result.fetchall()

    if len(data) == 0:
        return make_response(f'error occurred when fetching albums for {table}', 404)
    else:
        conn.commit()
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
    # check if year is not current year
    # connect to DB
    # try: get stats for year
        # success : return
        # failure: generate stats
    if table == config.latest_year:
        return None

    try:
        conn = mysql.connector.connect(user=config.mysqluser, password=config.mysqlpass, host=config.mysqlhost, database=config.mysqldb)
        cursor = conn.cursor(buffered=True)
    except Exception as e:
        print(f'Error with connecting to db: {str(e)}')
        return jsonify("Issue connecting to database")

    try:
        cursor.callproc('getStats', (table,))
    except Exception as e:
        return make_response(f'mysql getStats error: {str(e)}', 404)

    for result in cursor.stored_results():
        data = result.fetchall()

    if len(data) == 0:
        return make_response(f'error occurred when fetching stats for {table}', 404)
    else:
        conn.commit()
        print(data)
        res_dict = {
            'First_Listened' : albums.get_single_album(table, data[0][0], data[0][1]),
            'Last_Listened' : albums.get_single_album(table, data[0][2], data[0][3]),
            'Top_Artist' : data[0][4],
            'Total_Albums' : data[0][4],
            'Total_Time' : data[0][5]
        }
        print(res_dict)
        return jsonify(res_dict)


#  Calculate total duration in milliseconds of all albums in listen year
def getYearlyTimeListened(table):
    time = 0
    albums = getAlbums(table, api_call=False)
    for album in albums:
        title = album['Album']
        artist = album['Artist']
        print(f'{title}, {artist}')
        sp_search = albums.spotify_search_album(title, artist)
        if sp_search['albums']['total'] == 0:
            # splice album title and try Spotify search again
            try:
                sp_search = albums.spotify_search_album(album_slice(title), artist)
            except Exception as e:
                print(f'failure to splice search for {title}')
                continue
        try:
            sp_album_id = sp_search['albums']['items'][0]['id']
        except Exception as e1:
            print(f'failure to spotify search for {title}')
            continue
        tracks = spotify_get_album_tracks(sp_album_id)
        for track in tracks:
            time += track['duration_ms']
    print(time)
    return time


@app.route('/api/getartist/<path:artist>', methods=['GET'])
def getArtist(artist):
    return artists.get_artist(artist)


if __name__ == '__main__':
    app.run(debug=True, port=8080)
