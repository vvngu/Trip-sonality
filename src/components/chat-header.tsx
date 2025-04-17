import React from 'react';

interface ChatHeaderProps {
  theme: string;
  location: string;
  dates: string;
}

export const ChatHeader: React.FC<ChatHeaderProps> = ({ theme, location, dates }) => {
  return (
    <div className="bg-white p-4 rounded-lg mb-4 flex items-center justify-between shadow-sm">
      <div className="flex items-center gap-4">
        <div className="bg-blue-100 p-3 rounded-full">
          <span className="text-blue-600 text-xl">📍</span>
        </div>
        <div>
          <h1 className="text-xl font-bold">{theme}</h1>
          <div className="flex items-center gap-2 text-sm text-gray-500">
            <span>{location}</span>
            <span>•</span>
            <span>{dates}</span>
          </div>
        </div>
      </div>
      <div className="flex gap-2">
        <button
          className="p-2 rounded-full hover:bg-gray-100"
          aria-label="Edit"
        >
          ✏️
        </button>
        <button
          className="p-2 rounded-full hover:bg-gray-100"
          aria-label="Share"
        >
          🔗
        </button>
        <button
          className="p-2 rounded-full hover:bg-gray-100"
          aria-label="Save"
        >
          🔖
        </button>
      </div>
    </div>
  );
};