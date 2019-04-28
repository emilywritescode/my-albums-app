import requests

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

from flask import Flask, render_template, request, json, make_response, jsonify

from flaskext.mysql import MySQL

import config
import calendar

import pylast


app = Flask(__name__)

mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = config.mysqluser
app.config['MYSQL_DATABASE_PASSWORD'] = config.mysqlpass
app.config['MYSQL_DATABASE_DB'] = config.mysqldb
mysql.init_app(app)


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
    wp_summary = wp_search_album(album, artist)

    res_dict = [{
        'CoverArt' : sp_album_cover,
        'SpotifyPlayer' : sp_album_embed,
        'LFM_Summary': lfm_summary,
        'WP_Summary': wp_summary
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
    res = get_album.get_wiki_content()

    return res

def wp_search_album(album, artist):
    pass

def album_slice(album):
    return album[:album.index('(')]

@app.route("/api/getartist/<path:artist>", methods=['GET'])
def getArtist(artist):
    # try Spotify search
    sp_artist_results = spotify_search_artist(artist)
    wikidata_artist_results = wikidata_search_artist(artist)

    res_dict = {
        'Spotify' : {
            'Followers': sp_artist_results['Followers'],
            'Genres': sp_artist_results['Genres'],
            'Image': sp_artist_results['Image']
        },
        'WikiData' : {
            'OfficialSite': wikidata_artist_results['official'],
            'Instagram' : wikidata_artist_results['ig'],
            'Twitter' : wikidata_artist_results['tw']
        }
    }

    print(res_dict)

    return jsonify(res_dict)

def spotify_search_artist(artist):
    client_credentials_manager = SpotifyClientCredentials(client_id=config.SPOTIFY_CLIENT_ID, client_secret=config.SPOTIFY_CLIENT_SECRET)
    sp = spotipy.Spotify(client_credentials_manager = client_credentials_manager)

    try:
        spsearch = sp.search(q = 'artist:' + artist, limit=1, type = 'artist')
    except Exception as e:
        print("spotipy search for {} failed with exception: {}".format(artist, e))
        return None

    res = {
        'Followers': spsearch['artists']['items'][0]['followers']['total'],
        'Genres': spsearch['artists']['items'][0]['genres'],
        'Image': spsearch['artists']['items'][0]['images'][0]['url']
    }
    return res

def wikidata_search_artist(artist):
    try:
        wbsearch = requests.get('https://www.wikidata.org/w/api.php', params =
        {
            'action' : 'wbsearchentities',
            'search' : artist,
            'language' : 'en',
            'limit' : 1,
            'format' : 'json'
        })
    except Exception as e:
        print("wikidata search for {} failed with exception: {}".format(artist, e))
        return None

    wbs_j = wbsearch.json()
    wikidata_id = wbs_j['search'][0]['id']

    try:
        wbget = requests.get('https://www.wikidata.org/w/api.php', params = {
            'action' : 'wbgetentities',
            'ids' : wikidata_id,
            'languages' : 'en',
            'props' : 'claims',
            'format' : 'json'
        })
    except Exception as e:
        print("wikidata get failed with exception: {}".format(e))
        return None

    wbg_j = wbget.json()

    res = {
        'official' : grabWikiValue(wbg_j['entities'][wikidata_id]['claims'], 'P856'),
        'ig' : grabWikiValue(wbg_j['entities'][wikidata_id]['claims'], 'P2003'),
        'tw' : grabWikiValue(wbg_j['entities'][wikidata_id]['claims'], 'P2002')
    }
    return res

def grabWikiValue(j_results, wiki_key):
    try:
        res = j_results[wiki_key][0]['mainsnak']['datavalue']['value']
        return res
    except KeyError as e:
        print("Error Key for: {}".format(e))
        return None


if __name__ == "__main__":
    app.run(debug=True, port=8080)
