import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { WelcomeComponent } from './welcome/welcome.component';
import { AlbumsComponent } from './albums/albums.component';
import { AlbumDetailsComponent } from './album-details/album-details.component';

const routes: Routes = [
    { // landing page is the WelcomeComponent
        path: '',
        pathMatch: 'full',
        component: WelcomeComponent
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
    }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
