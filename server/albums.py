# -*- coding: utf-8 -*-
import requests
import urllib
import calendar
import config

from flask import render_template, request, json, make_response, jsonify

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

import pylast

import mysql.connector


def insert_album(req):
    try:
        conn = mysql.connector.connect(user=config.mysqluser, password=config.mysqlpass, host=config.mysqlhost, database=config.mysqldb)
        cursor = conn.cursor(buffered=True)
    except Exception as e:
        print(f'Error with connecting to db: {str(e)}')
        return jsonify("Issue connecting to database")

    _tab = config.latest_year
    _m = req['month']
    _d = req['day']
    _a = req['album']
    _r = req['artist']
    _y = req['rel_year']

    if _tab and _m and _d and _a and _r and _y:
        try:
            args = (_tab,
                    _m,
                    _d,
                    _a,
                    _r,
                    _y
                    )
            cursor.callproc('insertAlbum', (args))
        except Exception as e:
            print(f'mysql insertAlbum error: {str(e)}')
            return jsonify("Error with inserting into database.")

        conn.commit()
        conn.close()
        return jsonify(f'{_a} by {_r} successfully inserted into database')

    else:
        return jsonify("Some input fields were missing")


#  Fetch album from the database given listen year, title, artist
def get_single_album(table, title, artist):
    try:
        conn = mysql.connector.connect(user=config.mysqluser, password=config.mysqlpass, host=config.mysqlhost, database=config.mysqldb)
        cursor = conn.cursor(buffered=True)
    except Exception as e:
        print(f'Error with connecting to db: {str(e)}')
        return jsonify("Issue connecting to database")

    try:
        cursor.callproc('getAlbum', (table, title, artist))
    except Exception as e:
        return make_response(f'mysql getSingleAlbum error: {str(e)}', 404)

    data = cursor.fetchall()

    for row in data:
        res_dict = {
            'Month' : calendar.month_name[row[0]],
            'Day' : row[1],
            'Album' : row[2],
            'Artist' : row[3],
            'Release_Year' : row[4]
        }

    return res_dict


def get_album_details(album, artist, api_call=True):
    # try Spotify search
    sp_search_results = spotify_search_album(album, artist)

    if sp_search_results['albums']['total'] == 0:
        # splice album title and try Spotify search again
        print('could not find album in Spotify, trying again...')
        try:
            sp_search_results = spotify_search_album(album_slice(album), artist)
        except Exception as e:
            return make_response(f'Error occurred trying to query Spotify for {album}: {str(e)}.', 404)

    # find the album -- some artists have singles with same name as album
    for album_result in sp_search_results['albums']['items']:
        if album_result['album_type'] == 'album':
            sp_album = album_result
            break

    # get album cover
    sp_album_cover = album_result['images'][0]['url']

    #get album Spotify URL for play embed
    sp_album_uri = album_result['uri']
    sp_album_embed = "https://open.spotify.com/embed/album/" + sp_album_uri[sp_album_uri.rfind(':')+1:]

    # try Last.fm search
    lfm_summary = lfm_search_album(album, artist)

    # try Wikipedia search
   # wp_summary = wp_search_album(album, artist)

    res_dict = {
        'CoverArt' : sp_album_cover,
        'SpotifyPlayer' : sp_album_embed,
        'LFM_Summary': lfm_summary,
        #'WP_Summary': wp_summary
    }
    if(api_call):
        return jsonify(res_dict)
    else:
        return res_dict


#  Search for album on Spotify
def spotify_search_album(album, artist):
    album_dec = urllib.parse.unquote(album)
    client_credentials_manager = SpotifyClientCredentials(client_id=config.SPOTIFY_CLIENT_ID, client_secret=config.SPOTIFY_CLIENT_SECRET)
    sp = spotipy.Spotify(client_credentials_manager = client_credentials_manager)
    res = sp.search(q = 'album:' + album_dec + ' artist:' + artist, type = 'album', market = 'US')

    return res


#  Get all tracks in an album on Spotify
def spotify_get_album_tracks(spotify_album_id):
    client_credentials_manager = SpotifyClientCredentials(client_id=config.SPOTIFY_CLIENT_ID, client_secret=config.SPOTIFY_CLIENT_SECRET)
    sp = spotipy.Spotify(client_credentials_manager = client_credentials_manager)
    tracks = sp.album_tracks(spotify_album_id)
    res = []
    for track in tracks['items']:
        res.append(track)
    return res


#  Search for album on LastFM
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
