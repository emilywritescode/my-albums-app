import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { AlbumsService, Album, Stats} from '../albums.service';
import { ChartsModule } from 'ng2-charts';

@Component({
  selector: 'app-yearly-stats',
  templateUrl: './yearly-stats.component.html',
  styleUrls: ['./yearly-stats.component.css']
})
export class YearlyStatsComponent implements OnInit {
    table: string;
    albums: Album[];
    stats: Stats;
    total_time: string;

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
                alert('Couldn\'t retrieve list of albums for stats: ' + error.error);
            }
          );

          albumService.getStats(this.table).subscribe(
            data => {
                this.stats = data;
            },
            error => {
                alert('Couldn\'t retrieve stats for albums table: ' + error.error);
            }
          );
      });
  }

  ngOnInit() {}
}
