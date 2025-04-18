import React from 'react';

interface ChatHeaderProps {
  theme: string;
  location: string;
  dates: string;
}

export const ChatHeader: React.FC<ChatHeaderProps> = ({ theme, location, dates }) => {
  return (
    <div className="grid grid-cols-3 gap-2 mb-4 border border-gray-200 rounded-lg overflow-hidden">
      <div className="p-3 border-r border-gray-200">
        <div className="text-gray-500 text-sm">Theme:</div>
        <div className="font-georgia font-medium text-lg">{theme}</div>
      </div>
      <div className="p-3 border-r border-gray-200">
        <div className="text-gray-500 text-sm">Location:</div>
        <div className="font-georgia font-medium text-lg">{location}</div>
      </div>
      <div className="p-3">
        <div className="text-gray-500 text-sm">Dates:</div>
        <div className="font-georgia font-medium text-lg">{dates}</div>
      </div>
    </div>
  );
};