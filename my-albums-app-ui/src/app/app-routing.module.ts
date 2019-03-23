import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { WelcomeComponent } from './welcome/welcome.component';
import { AlbumsComponent } from './albums/albums.component';

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
    }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
