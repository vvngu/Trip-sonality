// src/components/chat-header.tsx
import React from "react";

interface ChatHeaderProps {
  theme: string;
  location: string;
  dates: string;
  onThemeChange: (value: string) => void;
  onLocationChange: (value: string) => void;
  onDatesChange: (value: string) => void;
}

export const ChatHeader: React.FC<ChatHeaderProps> = ({
  theme,
  location,
  dates,
  onThemeChange,
  onLocationChange,
  onDatesChange,
}) => (
  <div className="grid grid-cols-3 gap-2 mb-4 border border-gray-200 rounded-lg overflow-hidden">
    <div className="p-3 border-r border-gray-200">
      <div className="text-gray-500 text-sm">Theme:</div>
      <input
        type="text"
        placeholder="Enter theme"
        className="w-full mt-1 bg-transparent focus:outline-none font-georgia font-medium text-lg"
        value={theme}
        onChange={(e) => onThemeChange(e.target.value)}
      />
    </div>
    <div className="p-3 border-r border-gray-200">
      <div className="text-gray-500 text-sm">Location:</div>
      <input
        type="text"
        placeholder="Enter location"
        className="w-full mt-1 bg-transparent focus:outline-none font-georgia font-medium text-lg"
        value={location}
        onChange={(e) => onLocationChange(e.target.value)}
      />
    </div>
    <div className="p-3">
      <div className="text-gray-500 text-sm">Length:</div>
      <input
        type="text"
        placeholder="Enter dates"
        className="w-full mt-1 bg-transparent focus:outline-none font-georgia font-medium text-lg"
        value={dates}
        onChange={(e) => onDatesChange(e.target.value)}
      />
    </div>
  </div>
);
