import { Component } from '@angular/core';
import { Header } from '../layout/header/header';
import { Hero } from "../layout/hero/hero";
import { FeaturesSection } from "../layout/features-section/features-section";

@Component({
  selector: 'app-home',
  imports: [Header, Hero, FeaturesSection],
  templateUrl: './home.html',
  styleUrl: './home.css'
})
export class Home { 

}
