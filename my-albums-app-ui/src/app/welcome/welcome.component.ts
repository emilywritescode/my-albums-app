import { Component, OnInit } from '@angular/core';
import { Table, AlbumsService } from '../albums.service';
import { ActivatedRoute } from '@angular/router';



@Component({
  selector: 'app-welcome',
  templateUrl: './welcome.component.html',
  styleUrls: ['./welcome.component.css']
})
export class WelcomeComponent implements OnInit {
    tables: Table[];

    constructor(
        private albumService: AlbumsService,
        private route: ActivatedRoute,
    ) {
        route.paramMap.subscribe((paramMap) => {
            albumService.showTables().subscribe(
                data => {
                    this.tables = data;
                },
                error => {
                    alert('Couldn\'t retrieve database tables');
                }
            );
        });
    }
    ngOnInit() {}
}
