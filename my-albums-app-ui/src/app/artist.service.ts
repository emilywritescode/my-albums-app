import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

export interface SpotifyDetails {
    Artist_URI: string;
    Followers: number;
    Genres: string[];
    Image: string
}
export interface WikiDataDetails {
    OfficialSite: string;
    Facebook: string;
    Instagram: string;
    Twitter: string;
}
export interface ArtistDetails {
    Spotify: SpotifyDetails;
    WikiData: WikiDataDetails;
}

@Injectable({
  providedIn: 'root'
})

export class ArtistService {

  constructor(
      public http: HttpClient
  ) { }

  getArtist(name: string) {
      return this.http.get<ArtistDetails>('/api/getartist/' + name);
  }
}
