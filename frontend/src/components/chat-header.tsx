import React from "react";

interface ChatHeaderProps {
  theme: string;
  location: string;
  dates: string;
  onThemeChange: (value: string) => void;
  onLocationChange: (value: string) => void;
  onDatesChange: (value: string) => void;
  isLocked?: boolean; // New prop to determine if fields are locked
}

export const ChatHeader: React.FC<ChatHeaderProps> = ({
  theme,
  location,
  dates,
  onThemeChange,
  onLocationChange,
  onDatesChange,
  isLocked = false, // Default to false if not provided
}) => (
  <div className="grid grid-cols-3 gap-2 mb-4 border border-gray-200 rounded-lg overflow-hidden">
    <div className="p-3 border-r border-gray-200 flex items-center space-x-2">
      <label className="text-gray-600 text-base font-georgia font-medium whitespace-nowrap">
        Theme:
      </label>
      {isLocked ? (
        <span className="flex-1 font-georgia font-medium text-sm text-gray-800">
          {theme}
        </span>
      ) : (
        <input
          type="text"
          placeholder="Enter theme"
          className="flex-1 bg-transparent focus:outline-none font-georgia font-medium text-sm"
          value={theme}
          onChange={(e) => onThemeChange(e.target.value)}
        />
      )}
    </div>
    <div className="p-3 border-r border-gray-200 flex items-center space-x-2">
      <label className="text-gray-600 text-base font-georgia font-medium whitespace-nowrap">
        Location:
      </label>
      {isLocked ? (
        <span className="flex-1 font-georgia font-medium text-sm text-gray-800">
          {location}
        </span>
      ) : (
        <input
          type="text"
          placeholder="Enter location"
          className="flex-1 bg-transparent focus:outline-none font-georgia font-medium text-sm"
          value={location}
          onChange={(e) => onLocationChange(e.target.value)}
          required={true}
        />
      )}
    </div>
    <div className="p-3 flex items-center space-x-2">
      <label className="text-gray-600 text-base font-georgia font-medium whitespace-nowrap">
        Length:
      </label>
      {isLocked ? (
        <span className="flex-1 font-georgia font-medium text-sm text-gray-800">
          {dates}
        </span>
      ) : (
        <input
          type="text"
          placeholder="Enter dates"
          className="flex-1 bg-transparent focus:outline-none font-georgia font-medium text-sm"
          value={dates}
          onChange={(e) => onDatesChange(e.target.value)}
          required={true}
        />
      )}
    </div>
  </div>
);
