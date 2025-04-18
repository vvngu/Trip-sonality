import React from "react";

interface SidebarProps {
  width: number;
  onToggle: () => void;
}

const menuItems = [
  "Chats",
  "Itinerary",
  "Saved",
  "Updates",
  "Explore",
  "Create",
];

const Sidebar: React.FC<SidebarProps> = ({ width, onToggle }) => (
  <div
    className="flex flex-col bg-white border-r border-gray-200 h-full"
    style={{ width }}
  >
    {/* Logo and hide button */}
    <div className="flex items-center justify-between p-4">
      <div className="flex items-center">
        <img src="/paper-plane.svg" alt="Tripsonality" className="h-6 mr-2" />
        <span className="font-serif font-bold text-lg">Tripsonality</span>
      </div>
      <button onClick={onToggle} className="p-2 focus:outline-none">
        ✕
      </button>
    </div>

    {/* Navigation items */}
    <nav className="flex-1 px-2 space-y-1">
      {menuItems.map((item) => (
        <button
          key={item}
          className="w-full text-center text-sm py-6 rounded hover:bg-gray-100"
        >
          {item}
        </button>
      ))}
    </nav>
    <div className="p-4 space-y-4">
      <div className="text-sm bg-gray-100">text-sm</div>
      <div className="text-lg bg-gray-200">text-lg</div>
      <div className="text-2xl bg-gray-300">text-2xl</div>
      <div className="text-4xl bg-gray-400">text-4xl</div>
      <div className="text-5xl bg-gray-500">text-5xl</div>
    </div>

    {/* New Chat button */}
    <div className="p-4">
      <button className="w-full py-2 bg-gray-100 rounded">New Chat</button>
    </div>
  </div>
);

export default Sidebar;
