import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { WelcomeComponent } from './welcome/welcome.component';
import { InsertRecordComponent } from './insert-record/insert-record.component';
import { AlbumsComponent } from './albums/albums.component';
import { AlbumDetailsComponent } from './album-details/album-details.component';
import { ArtistDetailsComponent } from './artist-details/artist-details.component';
import { YearlyStatsComponent } from './yearly-stats/yearly-stats.component';


const routes: Routes = [
    { // landing page is the WelcomeComponent
        path: '',
        pathMatch: 'full',
        component: WelcomeComponent
    },
    {
        path: 'insert',
        pathMatch: 'full',
        component: InsertRecordComponent
    },
    {
        path: "albums/:year",
        pathMatch: 'full',
        component: AlbumsComponent
    },
    {
        path: "album/:title/:artist",
        pathMatch: 'full',
        component: AlbumDetailsComponent
    },
    {
        path: "artist/:name",
        pathMatch: 'full',
        component: ArtistDetailsComponent
    },
    {
        path: "stats/:table",
        pathMatch: 'full',
        component: YearlyStatsComponent
    }
];


@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
