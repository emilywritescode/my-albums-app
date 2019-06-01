import requests

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

from flask import Flask, render_template, request, json, make_response, jsonify

from flaskext.mysql import MySQL

import config
import calendar

import pylast

from artists import get_artist

app = Flask(__name__)

mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = config.mysqluser
app.config['MYSQL_DATABASE_PASSWORD'] = config.mysqlpass
app.config['MYSQL_DATABASE_DB'] = config.mysqldb
mysql.init_app(app)


@app.route("/api/insertrecord", methods=['POST'])
def insertRecord():
    req = request.get_json()

    _tab = config.latest_year
    _m = req['month']
    _d = req['day']
    _t = req['album']
    _a = req['artist']
    _r = req['rel_year']

    if _tab and _m and _d and _t and _a and _r:
        conn = mysql.connect()
        cursor = conn.cursor()
        try:
            args = (_tab,
                    _m,
                    _d,
                    _t,
                    _a,
                    _r
                    )
            cursor.callproc('insertRecord', (args))
        except Exception as e:
            print(str(e))
            return jsonify("Error with inserting into database.")

        conn.commit()
        conn.close()
        return jsonify('Record for {} by {} successfully inserted into database'.format(_t, _a))

    else:
        return jsonify("Some input fields were missing")


@app.route('/api/showtables', methods=['GET'])
def showTables():
    conn = mysql.connect()
    cursor = conn.cursor()
    try:
        cursor.callproc('showTables',)
    except Exception as e:
        return make_response(str(e), 404)

    data = cursor.fetchall()

    if len(data) is 0:
        return make_response("not found", 404)
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


@app.route("/api/showrecords/<table>", methods=['GET'])
def showRecords(table):
    conn = mysql.connect()
    cursor = conn.cursor()
    try:
        cursor.callproc('selectRecords', (table,))
    except Exception as e:
        return make_response(str(e), 404)

    data = cursor.fetchall()

    if len(data) is 0:
        return make_response("not found", 404)
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
        return jsonify(res_dict)

@app.route("/api/getalbum/<path:album>/<path:artist>")
def getAlbum(album, artist):
    # try Spotify search
    sp_search_results = spotify_search_album(album, artist)

    if sp_search_results['albums']['total'] == 0:
        # splice album title and try Spotify search again
        try:
            sp_search_results = spotify_search_album(album_slice(album), artist)
        except Exception as e:
            return make_response("Error occured trying to query Spotify for album.", 404)

    # get album cover
    sp_album_cover = sp_search_results['albums']['items'][0]['images'][0]['url']

    #get album Spotify URL for play embed
    sp_album_uri = sp_search_results['albums']['items'][0]['uri']
    sp_album_embed = "https://open.spotify.com/embed/album/" + sp_album_uri[sp_album_uri.rfind(':')+1:]

    # try Last.fm search
    lfm_summary = lfm_search_album(album, artist)

    # try Wikipedia search
   # wp_summary = wp_search_album(album, artist)

    res_dict = [{
        'CoverArt' : sp_album_cover,
        'SpotifyPlayer' : sp_album_embed,
        'LFM_Summary': lfm_summary,
        #'WP_Summary': wp_summary
    }]
    print(res_dict)


    return jsonify(res_dict)


def spotify_search_album(album, artist):
    client_credentials_manager = SpotifyClientCredentials(client_id=config.SPOTIFY_CLIENT_ID, client_secret=config.SPOTIFY_CLIENT_SECRET)
    sp = spotipy.Spotify(client_credentials_manager = client_credentials_manager)
    res = sp.search(q = 'album:' + album + ' artist:' + artist, limit=1, type = 'album', market = 'US')

    return res

def lfm_search_album(album, artist):
    network = pylast.LastFMNetwork(api_key=config.LAST_FM_KEY, api_secret=config.LAST_FM_SECRET)

    get_album = network.get_album(artist, album)
    r = str(get_album.get_wiki_content())
    if r.rfind("<a href") == -1:
        return None
    else:
        return r[:r.rfind("<a href")]

# def wp_search_album(album, artist):
#     pass

def album_slice(album):
    return album[:album.index('(')]

@app.route("/api/getartist/<path:artist>", methods=['GET'])
def getArtist(artist):
    return get_artist(artist)

if __name__ == "__main__":
    app.run(debug=True, port=8080)
