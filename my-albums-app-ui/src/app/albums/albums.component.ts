import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { AlbumsService, Album } from '../albums.service';

@Component({
    selector: 'app-albums',
    templateUrl: './albums.component.html',
    styleUrls: ['./albums.component.css']
})
export class AlbumsComponent implements OnInit {
    table: string;
    albums: Album[];

    constructor(
        private albumService: AlbumsService,
        private route: ActivatedRoute
    ) {
        route.paramMap.subscribe((paramMap) => {
            this.table = paramMap.get('year');

            albumService.getAlbums(this.table).subscribe(
                data => {
                    this.albums = data;
                },
                error => {
                    alert('Couldn\'t retrieve list of albums for displaying.');
                }
            );
        });
    }
    ngOnInit() {}
}
