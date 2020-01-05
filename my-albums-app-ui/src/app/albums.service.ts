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
    Summary: string;
}
export interface Stats {
    First_Listened: Album;
    Last_Listened: Album;
    Total_Time: number;
    Top_Artist: string;
}

@Injectable({
    providedIn: 'root'
})
export class AlbumsService {
    constructor(
         public http: HttpClient
    ) {}

    getTables(){
        return this.http.get<Table[]>('/api/gettables');
    }
    getAlbums(table: string){
        return this.http.get<Album[]>('/api/getalbums/' + table);
    }
    getAlbumDetails(album: string, artist: string){
        return this.http.get<AlbumDetails>('/api/getalbumdetails/' + album + '/' + artist);
    }
    getStats(table: string){
        return this.http.get<Stats>('/api/getstats/' + table)
    }
}
