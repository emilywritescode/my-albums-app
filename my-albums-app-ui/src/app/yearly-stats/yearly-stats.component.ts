import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { AlbumsService, AlbumDetails, Stats} from '../albums.service';

@Component({
  selector: 'app-yearly-stats',
  templateUrl: './yearly-stats.component.html',
  styleUrls: ['./yearly-stats.component.css']
})
export class YearlyStatsComponent implements OnInit {
    table: string;
    stats: Stats;

  constructor(
      private albumService: AlbumsService,
      private route: ActivatedRoute
  ) {
      route.paramMap.subscribe((paramMap) => {
          this.table = paramMap.get('table');

          albumService.getStats(this.table).subscribe(
            data => {
                this.stats = data;
            },
            error => {
                alert('Couldn\'t retrieve stats for albums table: ' + error.error);
            }
          );
      });
      console.log(this);
  }

  ngOnInit() {}
}
