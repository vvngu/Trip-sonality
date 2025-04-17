import React from 'react';

interface MapViewProps {}

export const MapView: React.FC<MapViewProps> = () => {
  return (
    <div className="w-full h-full bg-gray-200 rounded-lg overflow-hidden flex flex-col items-center justify-center p-4">
      <div className="text-lg font-semibold mb-2">Map View</div>
      <div className="text-sm text-gray-600">Los Angeles, CA</div>
      <div className="mt-4 text-xs text-gray-500">
        Map integration temporarily disabled due to compatibility issues
      </div>
    </div>
  );
};