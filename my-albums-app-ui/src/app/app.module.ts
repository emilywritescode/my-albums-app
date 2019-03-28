import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { HttpClientModule, HttpClient } from '@angular/common/http';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { WelcomeComponent } from './welcome/welcome.component';
import { AlbumsComponent } from './albums/albums.component';
import { AlbumDetailsComponent } from './album-details/album-details.component';
import { ArtistDetailsComponent } from './artist-details/artist-details.component';

@NgModule({
  declarations: [
    AppComponent,
    WelcomeComponent,
    AlbumsComponent,
    AlbumDetailsComponent,
    ArtistDetailsComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    HttpClientModule
  ],
  providers: [HttpClient],
  bootstrap: [AppComponent]
})
export class AppModule { }
