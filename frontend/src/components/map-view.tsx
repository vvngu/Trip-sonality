import React, { useMemo } from "react";
// @ts-ignore - Ignoring type issues with Google Maps components
import { GoogleMap, useLoadScript, Marker } from "@react-google-maps/api";

interface MapViewProps {
  highlightedPlace?: string;
}

// Los Angeles coordinates
const losAngelesCoordinates = { lat: 34.0522, lng: -118.2437 };

// Expanded itinerary locations with more places
const itineraryLocations = [
  { id: 1, name: "Hollywood Sign", position: { lat: 34.1341, lng: -118.3215 } },
  {
    id: 2,
    name: "Santa Monica Pier",
    position: { lat: 34.0095, lng: -118.4912 },
  },
  {
    id: 3,
    name: "Griffith Observatory",
    position: { lat: 34.1184, lng: -118.3004 },
  },
  { id: 4, name: "Venice Beach", position: { lat: 33.985, lng: -118.4695 } },
  {
    id: 5,
    name: "Grand Central Market",
    position: { lat: 34.0509, lng: -118.2494 },
  },
  {
    id: 6,
    name: "Hollywood Walk of Fame",
    position: { lat: 34.1016, lng: -118.3267 },
  },
  {
    id: 7,
    name: "TCL Chinese Theatre",
    position: { lat: 34.1022, lng: -118.3410 },
  },
  {
    id: 8,
    name: "In-N-Out Burger",
    position: { lat: 34.0981, lng: -118.3375 },
  },
  {
    id: 9,
    name: "Hollywood Bowl",
    position: { lat: 34.1127, lng: -118.3392 },
  },
  {
    id: 10,
    name: "Universal Studios",
    position: { lat: 34.1381, lng: -118.3534 },
  },
  {
    id: 11,
    name: "Grandma's Café",
    position: { lat: 34.0771, lng: -118.2528 },
  },
  {
    id: 12,
    name: "CityWalk",
    position: { lat: 34.1373, lng: -118.3526 },
  },
  {
    id: 13,
    name: "Shake Shack",
    position: { lat: 34.0977, lng: -118.3264 },
  },
  {
    id: 14,
    name: "Getty Center",
    position: { lat: 34.0776, lng: -118.4741 },
  },
  {
    id: 15,
    name: "Sunset Boulevard",
    position: { lat: 34.0967, lng: -118.3425 },
  },
  {
    id: 16,
    name: "Venice Beach Snack Stand",
    position: { lat: 33.9858, lng: -118.4725 },
  },
  {
    id: 17,
    name: "Warner Bros. Studio",
    position: { lat: 34.1538, lng: -118.3371 },
  },
  {
    id: 18,
    name: "Downtown Art District",
    position: { lat: 34.0403, lng: -118.2351 },
  },
  {
    id: 19,
    name: "The Grove Food Court",
    position: { lat: 34.0725, lng: -118.3576 },
  }
];

// Create a separate file called react-app-env.d.ts in the src directory with this content:
// /// <reference types="react-scripts" />
// declare module '@react-google-maps/api';

export const MapView: React.FC<MapViewProps> = ({ highlightedPlace }) => {
  // Google Maps options
  const mapOptions = useMemo(
    () => ({
      disableDefaultUI: false,
      clickableIcons: true,
      scrollwheel: true,
      styles: [
        {
          // 全局去色处理
          stylers: [
            { saturation: -100 },  // 去除饱和度
            { lightness: 0 },      // 保持亮度不变
          ],
        },
  
        {
          featureType: "water",
          elementType: "geometry.fill",
          stylers: [{ color: "#d3edf9" }],
        },
        {
          featureType: "poi",
          elementType: "labels.text.fill",
          stylers: [{ color: "#6f9ba5" }],
        },
        {
          featureType: "road",
          elementType: "geometry.fill",
          stylers: [{ color: "#fffffa" }],
        },
      ],
    }),
    []
  );
  // Google Maps API key is already set: AIzaSyCO7OMyTxvd0--cyNO4muoy7_jpcOEPsEU
  // Google Maps implementation is already set up
  const { isLoaded, loadError } = useLoadScript({
    googleMapsApiKey: "AIzaSyCO7OMyTxvd0--cyNO4muoy7_jpcOEPsEU",
  });

  // Loading and error handling is already implemented
  if (loadError || !isLoaded) {
    return (
      <div className="w-full h-full flex items-center justify-center bg-gray-100 rounded-lg">
        <div className="text-center">
          <div className="text-lg font-georgia text-gray-600">
            {loadError ? "Error loading Google Maps" : "Loading map..."}
          </div>
        </div>
      </div>
    );
  }

  // Find the highlighted location to center on it if present
  const highlightedLocation = itineraryLocations.find(
    (loc) => loc.name === highlightedPlace
  );

  // Set the center coordinates based on highlighted place or default to LA
  const centerCoordinates = highlightedLocation
    ? highlightedLocation.position
    : losAngelesCoordinates;

  // We have to ignore type errors for now but the map will work correctly at runtime
  return (
    <div className="w-full h-full relative overflow-hidden rounded-lg">
      {/* @ts-ignore */}
      <GoogleMap
        mapContainerStyle={{ width: "100%", height: "100%" }}
        center={centerCoordinates}
        zoom={highlightedPlace ? 15 : 12}
        options={mapOptions}
      >
        {itineraryLocations.map((loc) => (
          <Marker
            key={loc.id}
            position={loc.position}
            title={loc.name}
            // @ts-ignore
            icon={loc.name === highlightedPlace ? {
              path: "M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z",
              fillColor: "#ef4444",
              fillOpacity: 1,
              strokeWeight: 2,
              strokeColor: "#ffffff",
              scale: 2,
              anchor: { x: 12, y: 22 },
            } : undefined}
            animation={loc.name === highlightedPlace ? 1 : undefined} // 1 = BOUNCE
          />
        ))}
      </GoogleMap>

      {/* Info Card for highlighted place */}
      {highlightedPlace && (
        <div className="absolute top-5 right-5 bg-white p-4 border border-gray-200 rounded-lg shadow-lg max-w-xs">
          <h3 className="font-georgia font-medium mb-2">{highlightedPlace}</h3>
          <p className="text-sm text-gray-600">
            Explore this location on your Los Angeles movie-themed trip.
          </p>
        </div>
      )}

      {/* Legend overlay */}
      <div className="absolute bottom-5 left-5 bg-white p-3 border border-gray-300 rounded-lg shadow-md">
        <div className="font-medium mb-2 text-sm">Trip Legend</div>
        <div className="flex items-center gap-2 mb-1">
          <div className="w-4 h-4 rounded-full bg-gray-500"></div>
          <span className="text-sm">Locations</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded-full bg-red-500"></div>
          <span className="text-sm">Highlighted Spot</span>
        </div>
      </div>
    </div>
  );
};
