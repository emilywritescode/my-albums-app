import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router'
import { ArtistDetails, ArtistService, SpotifyDetails } from '../artist.service'

@Component({
    selector: 'app-artist-details',
    templateUrl: './artist-details.component.html',
    styleUrls: ['./artist-details.component.css']
})
export class ArtistDetailsComponent implements OnInit {
    name: string;
    details: ArtistDetails;
    spotify: SpotifyDetails;

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
                },
                error => {
                    alert ('Couldn\'t retrieve artist')
                }
            );
        });
    }
    ngOnInit() { }
}
