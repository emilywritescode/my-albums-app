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
    stats: Stats;
    table: string;
    albums: Album[];
    first_listened: Album;
    last_listened: Album;
    total_albums: number;
    total_time: number;
    top_artist: string;

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
                alert('Couldn\'t retrieve list of albums for stats.')
            }
          );
      });
  }

  ngOnInit() {
  }

}
