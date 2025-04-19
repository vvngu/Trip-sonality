import React, { useState } from "react";

// 6-day placeholder itinerary for a Los Angeles movie-themed trip
const placeholderItinerary = [
  {
    day: "Day 1",
    food: { time: "12:00 PM", place: "Grand Central Market", cost: "$25" },
    activities: [
      {
        time: "2:00 PM (2h)",
        place: "Hollywood Walk of Fame",
        cost: "$0",
      },
      { time: "5:00 PM (2h)", place: "TCL Chinese Theatre", cost: "$20" },
    ],
    summary:
      "Kick off your LA movie-themed trip with tasty street food and a stroll among the stars.",
  },
  {
    day: "Day 2",
    food: { time: "1:00 PM", place: "In-N-Out Burger", cost: "$15" },
    activities: [
      { time: "2:30 PM (2h)", place: "Griffith Observatory", cost: "$15" },
      { time: "6:00 PM (2h)", place: "Hollywood Bowl Tour", cost: "$30" },
    ],
    summary:
      "Enjoy a classic California burger, then catch panoramic city views and a behind-the-scenes music venue tour.",
  },
  {
    day: "Day 3",
    food: { time: "11:30 AM", place: "Grandma's Café", cost: "$20" },
    activities: [
      {
        time: "1:00 PM (2h)",
        place: "Universal Studios Backlot Tour",
        cost: "$30",
      },
      { time: "4:00 PM (2h)", place: "CityWalk Exploration", cost: "$0" },
    ],
    summary:
      "Taste homey brunch fare before exploring iconic movie sets and entertainment district vibes.",
  },
  {
    day: "Day 4",
    food: { time: "12:00 PM", place: "Shake Shack", cost: "$18" },
    activities: [
      { time: "1:30 PM (2h)", place: "Getty Center Tour", cost: "$20" },
      {
        time: "5:00 PM (2h)",
        place: "Sunset Boulevard Drive",
        cost: "$0",
      },
    ],
    summary:
      "Grab a casual shake, then enjoy art, architecture, and a scenic drive into movie history.",
  },
  {
    day: "Day 5",
    food: { time: "1:00 PM", place: "Venice Beach Snack Stand", cost: "$12" },
    activities: [
      {
        time: "2:00 PM (2h)",
        place: "Venice Beach Skateboarders",
        cost: "$0",
      },
      { time: "5:00 PM (2h)", place: "Santa Monica Pier", cost: "$10" },
    ],
    summary:
      "Soak up beach culture with tasty snacks, street performances, and a seaside amusement experience.",
  },
  {
    day: "Day 6",
    food: { time: "1:00 PM", place: "The Grove Food Court", cost: "$20" },
    activities: [
      {
        time: "2:30 PM (2h)",
        place: "Warner Bros. Studio Tour",
        cost: "$50",
      },
      { time: "5:00 PM (2h)", place: "Downtown Art District", cost: "$0" },
    ],
    summary:
      "End with a gourmet food hall meal and an immersive peek behind your favorite films, capped by local art browsing.",
  },
];

export default function Itinerary() {
  const [currentIndex, setCurrentIndex] = useState(0);
  const day = placeholderItinerary[currentIndex];

  return (
    <div className="panel rounded-custom flex-1 overflow-auto p-4">
      {/* Header */}
      <h2 className="text-center font-georgia font-medium text-xl mb-1">
        {placeholderItinerary.length} Days Itinerary – Los Angeles Movie Trip
      </h2>
      <div className="text-center font-medium mb-4">{day.day}</div>

      {/* Sections */}
      <div className="space-y-4">
        {/* Food */}
        <div className="border border-gray-200 p-4 rounded-lg">
          <div className="font-medium text-lg mb-2">Food</div>
          <div className="flex items-center">
            <div className="w-24 text-sm">{day.food.time}</div>
            <div className="flex-1 text-sm">{day.food.place}</div>
            <div className="w-5 text-sm text-right">{day.food.cost}</div>
          </div>
        </div>

        {/* Activities */}
        <div className="border border-gray-200 p-4 rounded-lg">
          <div className="font-medium text-lg mb-2">Activities</div>
          <div className="space-y-2">
            {day.activities.map((act) => (
              <div key={act.place} className="flex items-center">
                <div className="w-24 text-sm">{act.time}</div>
                <div className="flex-1 text-sm">{act.place}</div>
                <div className="w-5 text-sm text-right">{act.cost}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Summary */}
        <div className="border border-gray-200 p-4 rounded-lg">
          <div className="font-medium text-lg mb-2">Summary of the Day</div>
          <p className="text-sm">{day.summary}</p>
        </div>
      </div>

      {/* Pagination */}
      <div className="flex justify-center mt-6">
        {placeholderItinerary.map((_, idx) => (
          <span
            key={idx}
            className={`w-2 h-2 rounded-full mx-1 cursor-pointer ${
              idx === currentIndex ? "bg-black" : "bg-gray-300"
            }`}
            onClick={() => setCurrentIndex(idx)}
          />
        ))}
      </div>
    </div>
  );
}
