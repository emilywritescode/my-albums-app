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
    LFM_Summary: string;
    LFM_URL: string;
}
export interface Stats {
    Table_Year: number;
    First_Listened_Album: string[];
    First_Listened_Artist: string[];
    First_Listened_Cover: string[];
    First_Listened_Month: string;
    First_Listened_Day: number;
    Last_Listened_Album: string[];
    Last_Listened_Artist: string[];
    Last_Listened_Cover: string[];
    Last_Listened_Month: string;
    Last_Listened_Day: number;
    Top_Artist: string[];
    Top_Num: number;
    Total_Albums: number;
    Total_Time: string;
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
        var album_encoded = encodeURIComponent(album)
        return this.http.get<AlbumDetails>('/api/getalbumdetails/' + album_encoded + '/' + artist);
    }
    getStats(table: string){
        return this.http.get<Stats>('/api/getstats/' + table);
    }
}
