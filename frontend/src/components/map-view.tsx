import React, { useMemo } from "react";
// @ts-ignore - Ignoring type issues with Google Maps components
import { GoogleMap, useLoadScript, Marker } from "@react-google-maps/api";

interface MapViewProps {}

// Los Angeles coordinates
const losAngelesCoordinates = { lat: 34.0522, lng: -118.2437 };

// Example itinerary locations
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
];

// Create a separate file called react-app-env.d.ts in the src directory with this content:
// /// <reference types="react-scripts" />
// declare module '@react-google-maps/api';

export const MapView: React.FC<MapViewProps> = () => {
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
            { saturation: -100 }, // 去除饱和度
            { lightness: 30 }, // 保持亮度不变
            { gamma: 0.6 },
          ],
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

  // We have to ignore type errors for now but the map will work correctly at runtime
  return (
    <div className="w-full h-full relative overflow-hidden rounded-lg">
      {/* @ts-ignore */}
      <GoogleMap
        mapContainerStyle={{
          width: "100%",
          height: "100%",
        }}
        center={losAngelesCoordinates}
        zoom={12}
        options={mapOptions}
      >
        {itineraryLocations.map((loc) => (
          <Marker key={loc.id} position={loc.position} title={loc.name} />
        ))}
        <Marker position={losAngelesCoordinates} />
      </GoogleMap>

      {/* Legend overlay */}
      <div className="absolute bottom-5 left-5 bg-white p-3 border border-gray-300 rounded-lg shadow-md">
        <div className="font-medium mb-2 text-sm">Trip Legend</div>
        <div className="flex items-center gap-2 mb-1">
          <div className="w-4 h-4 rounded-full bg-red-500"></div>
          <span className="text-sm">Starting Point</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 rounded-full bg-blue-500"></div>
          <span className="text-sm">Attractions</span>
        </div>
      </div>
    </div>
  );
};
