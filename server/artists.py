# -*- coding: utf-8 -*-
import requests
from flask import jsonify
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

import config
import mysql.connector


def get_artist(artist):
    try: #connecting to DB
        conn = mysql.connector.connect(user=config.mysqluser, password=config.mysqlpass, host=config.mysqlhost, database=config.mysqldb)
        cursor = conn.cursor(buffered=True)
    except Exception as e:
        print('Error with connecting to db: {}'.format(e))
        return None

    try: #calling DB stored proc for searching artist
        sa_exec = 'call searchArtist (%s)'
        cursor.execute(sa_exec, (artist,))
        data = cursor.fetchall()
        if len(data) is 0: #artist not found in DB
            conn.close()
            init_artist(artist)
            conn = mysql.connector.connect(user=config.mysqluser, password=config.mysqlpass, host=config.mysqlhost, database=config.mysqldb)
            cursor = conn.cursor(buffered=True)
            cursor.execute(sa_exec, (artist,))
            data = cursor.fetchall()
    except Exception as e2:
        print('Error with searching artist: {}'.format(e2))
        return None

    res_dict = {
        'Spotify' : {
            'Followers': data[0][6],
            'Genres': data[0][5],
            'Image': data[0][7]
        },
        'WikiData' : {
            'OfficialSite': data[0][1],
            'Instagram' : data[0][4],
            'Twitter' : data[0][2],
            'Facebook': data[0][3]
        }
    }

    conn.close()

    return jsonify(res_dict)

def init_artist(artist):
    try: #connecting to DB
        conn = mysql.connector.connect(user=config.mysqluser, password=config.mysqlpass, host=config.mysqlhost, database=config.mysqldb, charset='utf8mb4', collation='utf8mb4_general_ci', use_unicode=True)
        cursor = conn.cursor(buffered=True)
    except Exception as e:
        print('Error with connecting to db: {}'.format(e))
        return None

    sp_artist_res = spotify_search_artist(artist)
    wiki_artist_res = wikidata_search_artist(artist)

    try: #calling DB stored proc for inserting artist
        args = (artist,
                wiki_artist_res['official'],
                wiki_artist_res['tw'],
                wiki_artist_res['fb'],
                wiki_artist_res['ig'],
                sp_artist_res['Genres'],
                sp_artist_res['Followers'],
                sp_artist_res['Image']
                )
        cursor.callproc('insertArtist', (args))
    except Exception as e:
        print("Something happened with attempting to insert {} into the DB: {}".format(artist, e))
        return

    conn.commit()
    conn.close()


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
        'Genres': ','.join(map(str, (spsearch['artists']['items'][0]['genres']))),
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
        'tw' : grabWikiValue(wbg_j['entities'][wikidata_id]['claims'], 'P2002'),
        'fb' : grabWikiValue(wbg_j['entities'][wikidata_id]['claims'], 'P2013').encode('utf-8')
    }

    print(res)
    return res

def grabWikiValue(j_results, wiki_key):
    try:
        res = j_results[wiki_key][0]['mainsnak']['datavalue']['value']
        return res
    except KeyError as e:
        print("Error Key for: {}".format(e))
        return None
