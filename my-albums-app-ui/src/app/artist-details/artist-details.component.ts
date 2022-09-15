import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router'
import { DomSanitizer, SafeResourceUrl } from '@angular/platform-browser';
import { ArtistDetails, ArtistService, SpotifyDetails, WikiDataDetails, LastFMDetails } from '../artist.service';
import { faLink, faHeadphonesAlt } from '@fortawesome/free-solid-svg-icons';
import { faInstagram, faTwitterSquare, faFacebook, faLastfmSquare, faSpotify } from '@fortawesome/free-brands-svg-icons';

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
    albums: string[];
    faLink = faLink;
    faInstagram = faInstagram;
    faTwitterSquare = faTwitterSquare;
    faFacebook = faFacebook;
    faLastfmSquare = faLastfmSquare;
    faSpotify = faSpotify;
    faHeadphonesAlt = faHeadphonesAlt;

    constructor(
        private artistService : ArtistService,
        private route : ActivatedRoute,
        private sanitizer: DomSanitizer
    ) {
        route.paramMap.subscribe((paramMap) => {
            this.name = paramMap.get("name");

            artistService.getArtist(this.name).subscribe(
                data => {
                    this.details = data;
                    this.spotify = this.details.Spotify;
                    this.wikidata = this.details.WikiData;
                    this.lastfm = this.details.LastFM;
                    this.albums = this.details.albums;
                },
                error => {
                    alert ('Couldn\'t retrieve artist: ' + error.error)
                }
            );
        });
    }
    ngOnInit() { }
}
