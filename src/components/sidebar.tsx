import React from 'react';

interface SidebarProps {}

export const Sidebar: React.FC<SidebarProps> = () => {
  const menuItems = [
    { label: 'Chats' },
    { label: 'Itenairy' },
    { label: 'Saved' },
    { label: 'Updates' },
    { label: 'Explore' },
    { label: 'Create' },
  ];

  return (
    <div className="h-screen border-r border-gray-200 bg-white flex flex-col w-[207px]">
      <div className="p-4 flex items-center gap-2 border-b border-gray-200">
        <img src="/paper-plane.svg" alt="Logo" className="w-6 h-6" />
        <span className="font-academy font-semibold text-xl">Tripsonality</span>
      </div>
      <nav className="flex-1">
        {menuItems.map((item) => (
          <button
            key={item.label}
            className="flex items-center w-full text-left py-3 px-6 hover:bg-gray-100 border-b border-gray-200 text-lg"
          >
            <span className="text-gray-700">{item.label}</span>
          </button>
        ))}
      </nav>
      <div className="p-3">
        <button className="w-full bg-gray-100 text-gray-700 py-3 rounded-lg flex items-center justify-center text-lg">
          New Chat
        </button>
      </div>
    </div>
  );
};