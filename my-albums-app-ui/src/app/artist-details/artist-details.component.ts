import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router'
import { ArtistDetails, ArtistService, SpotifyDetails, WikiDataDetails, LastFMDetails } from '../artist.service'
import { faLink } from '@fortawesome/free-solid-svg-icons'
import { faInstagram, faTwitterSquare, faFacebook, faSpotify, faLastfmSquare } from '@fortawesome/free-brands-svg-icons'

@Component({
    selector: 'app-artist-details',
    templateUrl: './artist-details.component.html',
    styleUrls: ['./artist-details.component.css']
})
export class ArtistDetailsComponent implements OnInit {
    name: string;
    details: ArtistDetails;
    spotify: SpotifyDetails;
    wikidata: WikiDataDetails;
    lastfm: LastFMDetails;
    faLink = faLink;
    faInstagram = faInstagram;
    faTwitterSquare = faTwitterSquare;
    faFacebook = faFacebook;
    faSpotify = faSpotify;
    faLastfmSquare = faLastfmSquare;

    constructor(
        private artistService : ArtistService,
        private route : ActivatedRoute
    ) {
        route.paramMap.subscribe((paramMap) => {
            this.name = paramMap.get("name");

            artistService.getArtist(this.name).subscribe(
                data => {
                    this.details = data;
                    this.spotify = this.details.Spotify;
                    this.wikidata = this.details.WikiData;
                    this.lastfm = this.details.LastFM;
                },
                error => {
                    alert ('Couldn\'t retrieve artist: ' + error.error)
                }
            );
        });
    }
    ngOnInit() { }
}
