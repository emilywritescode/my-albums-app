import { Component, OnInit } from '@angular/core';
import { Record } from '../record';
import { HttpClient, HttpResponse, HttpHeaders, HttpErrorResponse} from '@angular/common/http';

@Component({
  selector: 'app-insert-record',
  templateUrl: './insert-record.component.html',
  styleUrls: ['./insert-record.component.css']
})
export class InsertRecordComponent implements OnInit {
    record = new Record();
    diag_msg: string;

  constructor(
      private http: HttpClient
  ) {
      this.initDate();
  }

  ngOnInit() {}

  insertAlbum(){
      let httpOptions = {
          headers: new HttpHeaders({
              'Content-Type': 'application/json'
          })
      };
      this.http.post('/api/insertalbum', JSON.stringify(this.record), httpOptions).subscribe(
          data => {
              this.diag_msg = JSON.stringify(data);
          },
          (error: HttpErrorResponse)=> {
              if(error.status != 200){
                  this.diag_msg = "Error inserting into database: " + error.error;
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
