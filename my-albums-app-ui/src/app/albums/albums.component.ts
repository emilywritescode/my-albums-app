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
    valid_stats_years: string[] = ['albums_2018', 'albums_2019', 'albums_2020', 'albums_2021', 'albums_2022', 'albums_2023', 'albums_2024']
    valid_stats_year: boolean;

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
                    alert('Couldn\'t retrieve list of albums for displaying: ' + error.error);
                }
            );
        });

       this.valid_stats_year = this.valid_stats_years.includes(this.table);
    }
    ngOnInit() {}
}
