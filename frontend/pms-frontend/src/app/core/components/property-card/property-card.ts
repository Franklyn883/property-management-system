import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

export interface Property {
  id: string;
  title: string;
  location: string;
  price: number;
  priceUnit: string;
  imageUrl: string;
  type: 'apartment' | 'house' | 'studio' | 'commercial';
}

@Component({
  selector: 'app-property-card',
  imports: [CommonModule],
  templateUrl: './property-card.html',
  styleUrl: './property-card.css'
})
export class PropertyCard {
  @Input() property!: Property;
}
