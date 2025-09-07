import { Component, signal } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { Header } from "./core/layout/header/header";
import { Hero } from './core/layout/hero/hero';


@Component({
  selector: 'app-root',
  imports: [RouterOutlet, Header,Hero],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App {
  protected readonly title = signal('pms-frontend');
}
