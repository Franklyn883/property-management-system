import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { PropertyCard, Property } from '../../components/property-card/property-card';

@Component({
  selector: 'app-features-section',
  imports: [CommonModule, PropertyCard],
  templateUrl: './features-section.html',
  styleUrl: './features-section.css'
})
export class FeaturesSection {
  featuredProperties: Property[] = [
    {
      id: '1',
      title: 'Luxury Downtown Apartment',
      location: 'Downtown, New York',
      price: 2500,
      priceUnit: 'month',
      imageUrl: 'https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
      type: 'apartment'
    },
    {
      id: '2',
      title: 'Spacious Family Home',
      location: 'Suburbs, California',
      price: 3200,
      priceUnit: 'month',
      imageUrl: 'https://images.unsplash.com/photo-1564013799919-ab600027ffc6?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
      type: 'house'
    },
    {
      id: '3',
      title: 'Cozy Studio Apartment',
      location: 'Midtown, Texas',
      price: 1800,
      priceUnit: 'month',
      imageUrl: 'https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80',
      type: 'studio'
    }
  ];
}
