# -*- coding: utf-8 -*-
import requests
import config

from flask import jsonify

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials


import mysql.connector


def get_artist(artist):
    try:  # connecting to DB
        conn = mysql.connector.connect(user=config.mysqluser, password=config.mysqlpass, host=config.mysqlhost, database=config.mysqldb)
        cursor = conn.cursor(buffered=True)
    except Exception as e:
        print(f'Error with connecting to db: {str(e)}')
        return None

    data = cursor.callproc('searchArtist', [artist,])
    for result in cursor.stored_results():
        data = result.fetchall()
    if(len(data) == 0):
        print(f'Artist not found in DB: {artist}')
        init_artist(artist)
        conn = mysql.connector.connect(user=config.mysqluser, password=config.mysqlpass, host=config.mysqlhost, database=config.mysqldb)
        cursor = conn.cursor(buffered=True)
        cursor.callproc('searchArtist', [artist,])
        for result in cursor.stored_results():
            data = result.fetchall()

    ''' in MySQL db, artists:
    artist_name,
    official (website), twitter, facebook, instagram,
    sp_URI
    '''

    sp_data = spotify_updated_search_artist(artist)

    res_dict = {
        'Spotify' : {
            'Artist_URI': data[0][5],
            'Followers': sp_data['Followers'],
            'Genres': sp_data['Genres'].split(','),
            'Image': sp_data['Image']
        },
        'WikiData' : {
            'OfficialSite': data[0][1],
            'Facebook': data[0][3],
            'Instagram' : data[0][4],
            'Twitter' : data[0][2],
        },
        'LastFM' : {
            'Artist_URL': artist.replace(' ', '+')
        }
    }

    conn.close()
    print(res_dict)
    return jsonify(res_dict)


def init_artist(artist):
    try:  # connecting to DB
        conn = mysql.connector.connect(user=config.mysqluser, password=config.mysqlpass, host=config.mysqlhost, database=config.mysqldb, charset='utf8mb4', collation='utf8mb4_general_ci', use_unicode=True)
        cursor = conn.cursor(buffered=True)
    except Exception as e:
        print(f'Error with connecting to db: {str(e)}')
        return None

    sp_artist_res = spotify_init_search_artist(artist)
    wiki_artist_res = wikidata_search_artist(artist)

    try:  # calling DB stored proc for inserting artist
        args = (artist,
                wiki_artist_res['official'],
                wiki_artist_res['tw'],
                wiki_artist_res['fb'],
                wiki_artist_res['ig'],
                sp_artist_res['Artist_URI']
                )
        cursor.callproc('insertArtist', (args))
        print(f'Successfully init artist: {artist}')
    except Exception as e:
        print(f'error when attempting to insert {artist} into the DB: {str(e)}')
        return

    conn.commit()
    conn.close()


def update_artist(artist, column, value):
    try:  # connecting to DB
        conn = mysql.connector.connect(user=config.mysqluser, password=config.mysqlpass, host=config.mysqlhost, database=config.mysqldb, charset='utf8mb4', collation='utf8mb4_general_ci', use_unicode=True)
        cursor = conn.cursor(buffered=True)
    except Exception as e:
        print(f'Error with connecting to db: {str(e)}')
        return None

    try:
        cursor.callproc('updateArtist', (artist, column, value))
        print(f'Successfully updated {artist}. col: {column} with value: {value}')
    except Exception as e:
        print(f'error when attempting to update {artist}. col: {column} with value: {value} + {str(e)}')
        return

    conn.commit()
    conn.close()


def spotify_init_search_artist(artist):
    client_credentials_manager = SpotifyClientCredentials(client_id=config.SPOTIFY_CLIENT_ID, client_secret=config.SPOTIFY_CLIENT_SECRET)
    sp = spotipy.Spotify(client_credentials_manager = client_credentials_manager)

    res = {
        'Artist_URI': None
    }

    try:
        spsearch = sp.search(q = 'artist:' + artist, limit=1, type = 'artist')
    except Exception as e:
        print(f'spotipy init search for {artist} failed with exception: {str(e)}')
        return res

    res = {
        'Artist_URI': spsearch['artists']['items'][0]['id']
    }
    return res


def spotify_updated_search_artist(artist):
    client_credentials_manager = SpotifyClientCredentials(client_id=config.SPOTIFY_CLIENT_ID, client_secret=config.SPOTIFY_CLIENT_SECRET)
    sp = spotipy.Spotify(client_credentials_manager = client_credentials_manager)

    try:
        spsearch = sp.search(q = 'artist:' + artist, limit=1, type = 'artist')
    except Exception as e:
        print(f'spotipy search for {artist} failed with exception: {str(e)}')
        return None

    res = {
        'Genres': ','.join(map(str, (spsearch['artists']['items'][0]['genres']))),
        'Followers': spsearch['artists']['items'][0]['followers']['total'],
        'Image': spsearch['artists']['items'][0]['images'][0]['url']
    }
    return res


def wikidata_search_artist(artist):
    res = {
        'official' : None,
        'ig' : None,
        'tw' : None,
        'fb' : None
    }
    try:
        wbsearch = requests.get('https://www.wikidata.org/w/api.php', params =
        {
            'action' : 'wbsearchentities',
            'search' : artist,
            'language' : 'en',
            'limit' : 1,
            'format' : 'json'
        })
        wbs_j = wbsearch.json()
        wikidata_id = wbs_j['search'][0]['id']
    except Exception as e:
        print(f'wikidata search for {artist} failed with exception: {str(e)}')
        return res

    try:
        wbget = requests.get('https://www.wikidata.org/w/api.php', params = {
            'action' : 'wbgetentities',
            'ids' : wikidata_id,
            'languages' : 'en',
            'props' : 'claims',
            'format' : 'json'
        })
        wbg_j = wbget.json()
    except Exception as e:
        print(f'wikidata get failed with exception: {str(e)}')
        return res

    res = {
        'official' : grabWikiValue(wbg_j['entities'][wikidata_id]['claims'], 'P856'),
        'ig' : grabWikiValue(wbg_j['entities'][wikidata_id]['claims'], 'P2003'),
        'tw' : grabWikiValue(wbg_j['entities'][wikidata_id]['claims'], 'P2002'),
        'fb' : grabWikiValue(wbg_j['entities'][wikidata_id]['claims'], 'P2013')
    }

    return res


def grabWikiValue(j_results, wiki_key):
    try:
        res = j_results[wiki_key][0]['mainsnak']['datavalue']['value']
        return res
    except KeyError as e:
        print(f'Error Key for: {str(e)}')
        return None
