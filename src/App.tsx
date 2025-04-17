import React from 'react';
import { Sidebar } from './components/sidebar';
import { MapView } from './components/map-view';
import { ChatHeader } from './components/chat-header';

export default function App() {
  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar />
      <div className="flex-1 flex flex-col">
        <div className="flex-1 p-4">
          <ChatHeader 
            theme="INFJ Movie Trip"
            location="Los Angeles, CA, U.S."
            dates="05.20.2025 - 05.26.2025"
          />
          <div className="grid grid-cols-[1fr_400px] gap-4 h-[calc(100%-80px)]">
            <div className="relative">
              <MapView />
            </div>
            <div className="bg-white rounded-lg p-4 shadow-sm">
              <h2 className="text-lg font-semibold mb-4">Itinerary Details</h2>
              <div className="space-y-3">
                {[1, 2, 3, 4, 5].map((day) => (
                  <div key={day} className="p-3 border border-gray-200 rounded-md">
                    <div className="font-medium">Day {day}</div>
                    <div className="text-sm text-gray-500">Example activity</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
        <div className="p-4 border-t border-gray-200">
          <div className="relative">
            <input
              type="text"
              placeholder="Enter your destination, interests and dislikes..."
              className="w-full p-3 pr-10 border border-gray-300 rounded-lg"
            />
            <button className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400">
              📤
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}