import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

export interface SpotifyDetails {
    Artist_URI: string;
    Genres: string[];
    Image: string
}
export interface WikiDataDetails {
    OfficialSite: string;
    Instagram: string;
}
export interface LastFMDetails {
    Artist_URL: string;
}
export interface ArtistDetails {
    Spotify: SpotifyDetails;
    WikiData: WikiDataDetails;
    LastFM: LastFMDetails;
    albums: string[];
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
