import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { DomSanitizer, SafeResourceUrl } from '@angular/platform-browser';
import { AlbumsService, AlbumDetails } from '../albums.service';

@Component({
    selector: 'app-album-details',
    templateUrl: './album-details.component.html',
    styleUrls: ['./album-details.component.css']
})
export class AlbumDetailsComponent implements OnInit {
    artist: string;
    title: string;
    details: AlbumDetails;
    spotifyURL: SafeResourceUrl

    constructor(
        private albumService: AlbumsService,
        private route: ActivatedRoute,
        private sanitizer: DomSanitizer
    ) {
        route.paramMap.subscribe((paramMap) => {
            this.artist = paramMap.get("artist");
            this.title = paramMap.get("title");

            albumService.getAlbumDetails(this.title, this.artist).subscribe(
                data => {
                    this.details = data;
                    this.spotifyURL = sanitizer.bypassSecurityTrustResourceUrl(this.details.SpotifyPlayer);
                },
                error => {
                    alert('Couldn\'t retrieve album: ' + error.error);
                }
            );
        });
    }

    ngOnInit() { }
}
