import requests

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

from flask import Flask, render_template, request, json, make_response, jsonify

from flaskext.mysql import MySQL

import config

import calendar

app = Flask(__name__)

mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = config.mysqluser
app.config['MYSQL_DATABASE_PASSWORD'] = config.mysqlpass
app.config['MYSQL_DATABASE_DB'] = config.mysqldb
mysql.init_app(app)


# @app.route("/")
# def main():
#     return render_template('index.html')
#
# @app.route("/insert")
# def insertpage():
#     return render_template('insert.html')

@app.route("/insertrecord", methods=['POST'])
def insertRecord():
    try:
        _tab = request.form['table']
        _m = request.form['month']
        _d = request.form['day']
        _t = request.form['title']
        _a = request.form['artist']
        _r = request.form['relyear']
    except Exception:
        return render_template('error.html', error_msg = "form data not submitted properly")

    if _tab and _m and _d and _t and _a and _r:
        conn = mysql.connect()
        cursor = conn.cursor()
        try:
            cursor.callproc('insertRecord', (_tab, _m, _d, _t, _a, _r))
        except Exception as e:
            return render_template('error.html', error_msg= str(e))

        data = cursor.fetchall()

        if len(data) is 0:
            conn.commit()
            return render_template('insert.html', success_msg="Nice tunes! Record successfully entered!")
        else:
            return render_template('error.html', error_msg= "no data was returned")
    else:
        return render_template('error.html', error_msg= "one or more form fields not filled out")

# @app.route("/select")
# def selectpage():
#     return render_template('select.html')

@app.route("/api/showrecords/<table>", methods=['GET'])
def showRecords(table):
    conn = mysql.connect()
    cursor = conn.cursor()
    try:
        cursor.callproc('selectrecords', (table,))
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

@app.route("/album/<path:album>/<path:artist>")
def getAlbum(album, artist):
    # try Spotify search
    sp_search_results = spotify_search_album(album, artist)

    if sp_search_results['albums']['total'] == 0:
        # splice album title and try Spotify search again
        sp_search_results = spotify_search_album(album_slice(album), artist)

    # get album cover
    sp_album_cover = sp_search_results['albums']['items'][0]['images'][0]['url']

    #get album Spotify URL for play embed
    sp_album_uri = sp_search_results['albums']['items'][0]['uri']
    sp_album_embed = "https://open.spotify.com/embed/album/" + sp_album_uri[sp_album_uri.rfind(':')+1:]


    # try Last.fm search
    # lfm_search_results = lfm_search_album(album, artist)

    # try Wikipedia search
    # wp_search_results = wp_search_album(album, artist)


    return render_template('album_info.html', album_name = album, artist_name = artist, album_cover_SP = sp_album_cover, album_play_SP = sp_album_embed)


def spotify_search_album(album, artist):
    client_credentials_manager = SpotifyClientCredentials(client_id=config.SPOTIPY_CLIENT_ID, client_secret=config.SPOTIPY_CLIENT_SECRET)
    sp = spotipy.Spotify(client_credentials_manager = client_credentials_manager)
    res = sp.search(q = 'album:' + album + ' artist:' + artist, limit=1, type = 'album', market = 'US')

    return res

# def lfm_search_album(album, artist):
#     pass
#
# def wp_search_album(album, artist):
#     pass

def album_slice(album):
    return album[:album.index('(')]

@app.route("/artist/<path:artist>")
def getArtist(artist):
    # try Spotify search
    sp_artist_results = spotify_search_artist(artist)
    # try Last.fm search

    # try Google search
    return render_template('artist_info.html', artist_name = artist, res = sp_artist_results)

def spotify_search_artist(artist):
    client_credentials_manager = SpotifyClientCredentials(client_id=config.SPOTIPY_CLIENT_ID, client_secret=config.SPOTIPY_CLIENT_SECRET)
    sp = spotipy.Spotify(client_credentials_manager = client_credentials_manager)
    res = sp.search(q = 'artist:' + artist, limit=1, type = 'artist')
    return res

if __name__ == "__main__":
    app.run(debug=True, port=8080)
