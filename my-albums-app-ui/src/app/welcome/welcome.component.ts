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
        this.initDate();
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
            },
            (error: HttpErrorResponse)=> {
                if(error.status != 200){
                    this.diag_msg = "Error inserting into database.";
                }
            }
        );
    }

    dismissAlert(){
        this.diag_msg = null;
    }

    resetFormValues(){
        this.record.album = undefined;
        this.record.artist = undefined;
        this.record.rel_year = undefined;
        this.initDate();
    }
    initDate(){
        var today = new Date();
        this.record.month = today.getMonth() + 1;
        this.record.day = today.getDate();
    }
}
