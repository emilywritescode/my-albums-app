import { Component, OnInit } from '@angular/core';
import { Table, AlbumsService } from '../albums.service';
import { Record } from '../record';
import { ActivatedRoute } from '@angular/router';
import { HttpClient, HttpResponse, HttpErrorResponse, HttpHeaders } from '@angular/common/http';


@Component({
  selector: 'app-welcome',
  templateUrl: './welcome.component.html',
  styleUrls: ['./welcome.component.css']
})
export class WelcomeComponent implements OnInit {
    tables: Table[];
    record = new Record();
    diag_msg: string;

    constructor(
        private albumService: AlbumsService,
        private route: ActivatedRoute,
        private http: HttpClient
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

    insertAlbum(){
        let httpOptions = {
            headers: new HttpHeaders({
                'Content-Type': 'application/json'
            })
        };
        this.http.post('/api/insertrecord', JSON.stringify(this.record), httpOptions).subscribe(
            data => {
                this.diag_msg = JSON.stringify(data);
                alert(this.diag_msg);
            },
            (error: HttpErrorResponse)=> {
                if(error.status != 200){
                    alert(JSON.stringify(error.error));
                }
            }
        );
    }
}
