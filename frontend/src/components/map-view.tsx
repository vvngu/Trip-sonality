import React, { useState, useMemo } from "react";
// @ts-ignore
import {
  GoogleMap,
  useLoadScript,
  Marker,
  InfoWindow,
} from "@react-google-maps/api";

// add personalized location data api
interface LocationData {
  name: string;
  position: {
    lat: number;
    lng: number;
  };
}

interface ItineraryLocation {
  id: number;
  name: string;
  position: google.maps.LatLngLiteral;
}

interface MapViewProps {
  highlightedPlace?: string;
  // add optional location params
  locations?: LocationData[];
}

// Default center coordinates (world center) - used only as absolute fallback
const defaultCenterCoordinates = { lat: 0, lng: 0 };

// Helper function to calculate geographic center from locations
const calculateCenter = (locations: LocationData[]): { lat: number; lng: number } => {
  if (!locations || locations.length === 0) {
    return defaultCenterCoordinates;
  }

  const sum = locations.reduce(
    (acc, loc) => ({
      lat: acc.lat + loc.position.lat,
      lng: acc.lng + loc.position.lng,
    }),
    { lat: 0, lng: 0 }
  );

  return {
    lat: sum.lat / locations.length,
    lng: sum.lng / locations.length,
  };
};

// Create a separate file called react-app-env.d.ts in the src directory with this content:
export const MapView: React.FC<MapViewProps> = ({ highlightedPlace, locations }) => {
  const [mapRef, setMapRef] = useState<google.maps.Map | null>(null);
  const [selectedLoc, setSelectedLoc] = useState<ItineraryLocation | null>(
    null
  );
  const [placeDetails, setPlaceDetails] =
    useState<google.maps.places.PlaceResult | null>(null);
  const [currentPhotoIndex, setCurrentPhotoIndex] = useState(0);

  const { isLoaded, loadError } = useLoadScript({
    googleMapsApiKey: "AIzaSyCO7OMyTxvd0--cyNO4muoy7_jpcOEPsEU",
    libraries: ["places"],
  });

  // Convert API locations to map marker data
  const mapLocations = useMemo(() => {
    if (locations && locations.length > 0) {
      // Use API response locations data
      return locations.map((loc, index) => ({
        id: index + 1,
        name: loc.name,
        position: loc.position
      }));
    } else {
      // Return empty array if no locations available
      return [];
    }
  }, [locations]);

  // Move useMemo before any conditional returns to maintain hook order
  const mapOptions = useMemo<google.maps.MapOptions>(
    () => ({
      disableDefaultUI: false,
      clickableIcons: true,
      scrollwheel: true,
      styles: [
        { stylers: [{ saturation: -100 }, { lightness: 0 }] },
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

  // Determine center: prioritize selectedLoc, then highlightedPlace, then calculated center, else default
  const center = useMemo(() => {
    // First, check for currently selected location
    if (selectedLoc?.position) {
      return selectedLoc.position;
    }
    
    // Then check for highlighted place
    const highlightedLoc = mapLocations.find(loc => loc.name === highlightedPlace);
    if (highlightedLoc) {
      return highlightedLoc.position;
    }
    
    // Calculate center from available locations
    if (mapLocations.length > 0) {
      return calculateCenter(locations || []);
    }
    
    // Absolute fallback to default coordinates
    return defaultCenterCoordinates;
  }, [selectedLoc, highlightedPlace, mapLocations, locations]);

  // Now we can safely do conditional returns after all hooks are called
  if (loadError) return <div>Error loading map</div>;
  if (!isLoaded) return <div>Loading map...</div>;

  const onMapLoad = (map: google.maps.Map) => {
    setMapRef(map);
  };

  const handleMarkerClick = (loc: ItineraryLocation) => {
    setSelectedLoc(loc);
    setPlaceDetails(null);
    setCurrentPhotoIndex(0); // Reset photo index when selecting a new place
    if (!mapRef) return;
    const service = new window.google.maps.places.PlacesService(mapRef);
    service.findPlaceFromQuery(
      { query: loc.name, fields: ["place_id"], locationBias: loc.position },
      (results, status) => {
        if (
          status === window.google.maps.places.PlacesServiceStatus.OK &&
          results &&
          results.length
        ) {
          const placeId = results[0].place_id!;
          service.getDetails(
            {
              placeId,
              fields: [
                "name",
                "formatted_address",
                "rating",
                "reviews",
                "opening_hours",
                "formatted_phone_number",
                "photos",
                "types",
                "price_level",
              ],
            },
            (detail, stat) => {
              if (
                stat === window.google.maps.places.PlacesServiceStatus.OK &&
                detail
              ) {
                setPlaceDetails(detail);
              }
            }
          );
        }
      }
    );
  };

  const nextPhoto = () => {
    if (placeDetails?.photos) {
      setCurrentPhotoIndex((prevIndex) =>
        prevIndex === placeDetails.photos!.length - 1 ? 0 : prevIndex + 1
      );
    }
  };

  const prevPhoto = () => {
    if (placeDetails?.photos) {
      setCurrentPhotoIndex((prevIndex) =>
        prevIndex === 0 ? placeDetails.photos!.length - 1 : prevIndex - 1
      );
    }
  };

  const zoom = highlightedPlace || selectedLoc ? 15 : 12;

  return (
    <div className="w-full h-full relative overflow-hidden rounded-lg">
      {/* @ts-ignore */}
      <GoogleMap
        mapContainerStyle={{ width: "100%", height: "100%" }}
        center={center}
        zoom={zoom}
        options={mapOptions}
        onLoad={onMapLoad}
      >
        {mapLocations.map((loc) => (
          <Marker
            key={loc.id}
            position={loc.position}
            title={loc.name}
            onClick={() => handleMarkerClick(loc)}
            // @ts-ignore
            icon={
              loc.name === (highlightedPlace || selectedLoc?.name)
                ? {
                    path: "M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z",
                    fillColor: "#ef4444",
                    fillOpacity: 1,
                    strokeWeight: 2,
                    strokeColor: "#ffffff",
                    scale: 2,
                    anchor: { x: 12, y: 22 },
                  }
                : undefined
            }
          />
        ))}
        {selectedLoc && (
          <InfoWindow
            position={selectedLoc.position}
            onCloseClick={() => setSelectedLoc(null)}
          >
            <div className="max-w-xs font-sans">
              {placeDetails ? (
                <>
                  <h3 className="font-georgia font-semibold mb-1 text-lg">
                    {placeDetails.name}
                  </h3>

                  {/* Photo Gallery */}
                  {placeDetails.photos && placeDetails.photos.length > 0 && (
                    <div className="mt-2 mb-3 relative">
                      <div className="w-full h-36 rounded-md overflow-hidden bg-gray-100">
                        {/* Add try-catch and onError handling*/}
                        {(() => {
                          try {
                            const photoUrl = placeDetails.photos[
                              currentPhotoIndex
                            ].getUrl({
                              maxWidth: 600,
                              maxHeight: 400,
                            });
                            return (
                              <img
                                src={photoUrl}
                                alt={`${
                                  placeDetails.name || "Location"
                                } - Photo ${currentPhotoIndex + 1}`}
                                className="w-full h-36 object-cover rounded-md"
                                onError={(e) => {
                                  console.error("Photo failed to load:", e);
                                  e.currentTarget.src =
                                    "https://via.placeholder.com/600x400?text=No+Image+Available";
                                }}
                              />
                            );
                          } catch (error) {
                            console.error("Error getting photo URL:", error);
                            return (
                              <div className="w-full h-36 flex items-center justify-center bg-gray-200 text-gray-500">
                                <span>Photo unavailable</span>
                              </div>
                            );
                          }
                        })()}
                      </div>

                      {/* Photo Navigation */}
                      {placeDetails.photos &&
                        placeDetails.photos.length > 1 && (
                          <>
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                prevPhoto();
                              }}
                              className="absolute left-1 top-1/2 transform -translate-y-1/2 bg-white/70 hover:bg-white/90 p-1 rounded-full"
                              aria-label="Previous photo"
                            >
                              ◀
                            </button>
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                nextPhoto();
                              }}
                              className="absolute right-1 top-1/2 transform -translate-y-1/2 bg-white/70 hover:bg-white/90 p-1 rounded-full"
                              aria-label="Next photo"
                            >
                              ▶
                            </button>
                            <div className="absolute bottom-1 left-0 right-0 flex justify-center">
                              <div className="bg-black/50 px-2 py-0.5 rounded-full text-white text-xs">
                                {currentPhotoIndex + 1} /{" "}
                                {placeDetails.photos.length}
                              </div>
                            </div>
                          </>
                        )}
                    </div>
                  )}
                  {/* Location Info */}
                  <div className="mb-3">
                    <p className="text-sm">{placeDetails.formatted_address}</p>
                    {placeDetails.types && placeDetails.types.length > 0 && (
                      <p className="text-sm mt-1">
                        <span className="font-semibold">Category:</span>{" "}
                        {placeDetails.types[0].replace(/_/g, " ")}
                      </p>
                    )}
                    {placeDetails.rating && (
                      <div className="flex items-center mt-1">
                        <span className="font-semibold text-sm mr-1">
                          Rated:
                        </span>
                        <span className="text-sm">{placeDetails.rating}⭐</span>
                      </div>
                    )}
                    {placeDetails.formatted_phone_number && (
                      <p className="text-sm mt-1">
                        <span className="font-semibold">Call:</span>{" "}
                        {placeDetails.formatted_phone_number}
                      </p>
                    )}
                  </div>

                  {/* Opening Hours */}
                  {placeDetails.opening_hours?.weekday_text && (
                    <div className="mt-2 border-t pt-2">
                      <h4 className="font-semibold text-sm mb-1">
                        When To Visit:
                      </h4>
                      <ul className="text-xs space-y-1">
                        {placeDetails.opening_hours.weekday_text.map((line) => (
                          <li key={line}>{line}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </>
              ) : (
                <p className="text-sm font-georgia">Loading place details...</p>
              )}
            </div>
          </InfoWindow>
        )}
      </GoogleMap>
    </div>
  );
};