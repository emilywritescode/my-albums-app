import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

export interface Album {
    Album: string;
    Artist: string;
    Month: number;
    Day: number;
    Release_Year: number;
}

export interface Table {
    Name: string;
    NumAlbums: number;
    Year: number;
}

export interface AlbumDetails {
    CoverArt: string;
    SpotifyPlayer: string;
}

@Injectable({
    providedIn: 'root'
})
export class AlbumsService {
    constructor(
        public http: HttpClient
    ) { }

    showTables() {
        return this.http.get<Table[]>('/api/showtables');
    }
    getAlbums(table: string) {
        return this.http.get<Album[]>('/api/showrecords/' + table);
    }
    getAlbum(album: string, artist: string){
        return this.http.get<AlbumDetails>('/api/getalbum/' + album + '/' + artist);
    }
}
