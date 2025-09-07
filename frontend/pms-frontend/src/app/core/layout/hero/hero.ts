import { Component } from '@angular/core';
import { QuickSearch } from '../../components/quick-search/quick-search';

@Component({
  selector: 'app-hero',
  imports: [QuickSearch],
  templateUrl: './hero.html',
  styleUrl: './hero.css',
})
export class Hero {}
