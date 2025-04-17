import React from 'react';

interface SidebarProps {}

export const Sidebar: React.FC<SidebarProps> = () => {
  const menuItems = [
    { icon: '📱', label: 'Chats' },
    { icon: '🧭', label: 'Itinerary' },
    { icon: '🔖', label: 'Saved' },
    { icon: '🔔', label: 'Updates' },
    { icon: '🗺️', label: 'Explore' },
    { icon: '➕', label: 'Create' },
  ];

  return (
    <div className="h-screen w-60 border-r border-gray-200 bg-white flex flex-col">
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center gap-2">
          <span className="text-xl">✈️</span>
          <span className="font-semibold text-lg">Tripsonality</span>
        </div>
      </div>
      <nav className="flex-1 p-2">
        {menuItems.map((item) => (
          <button
            key={item.label}
            className="flex items-center gap-2 w-full text-left p-2 rounded-md hover:bg-gray-100 mb-1"
          >
            <span>{item.icon}</span>
            <span>{item.label}</span>
          </button>
        ))}
      </nav>
      <div className="p-2">
        <button className="w-full bg-blue-600 text-white p-2 rounded-md flex items-center justify-center gap-2">
          <span>+</span>
          <span>New Chat</span>
        </button>
      </div>
    </div>
  );
};