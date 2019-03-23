import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

export interface Album {
    Album: string;
    Artist: string;
    Month: number;
    Day: number;
    Release_Year: number;
}

@Injectable({
    providedIn: 'root'
})
export class AlbumsService {
    constructor(
        public http: HttpClient
    ) { }

    getAlbums(table: string) {
        return this.http.get<Album[]>('/api/showrecords/' + table);
    }
}
