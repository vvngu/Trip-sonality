import React from "react";
import { HiChevronLeft } from "react-icons/hi";

interface SidebarProps {
  width: number;
  onToggle: () => void;
  onNewChat: () => void;
  onExploreClick: () => void;
}

const menuItems = [
  "Chats",
  "Itinerary",
  "Saved",
  "Updates",
  "Create",
];

const Sidebar: React.FC<SidebarProps> = ({ width, onToggle, onNewChat, onExploreClick }) => (
  <div
    style={{
      width,
      display: "flex",
      flexDirection: "column",
      backgroundColor: "white",
      borderRight: "2px solid #d1d5db", // 更粗灰色边框
      height: "100vh",
      boxSizing: "border-box",
      fontFamily: "Georgia, serif",
    }}
  >
    {/* Logo and hide button */}
    <div
      style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        marginBottom: "12px",
        padding: "16px",
      }}
    >
      <div style={{ display: "flex", alignItems: "center" }}>
        <img
          src="/paper-plane.svg"
          alt="Tripsonality"
          style={{ height: "24px", marginRight: "8px" }}
        />
        <span
          style={{
            fontFamily: "Georgia, serif",
            fontWeight: "bold",
            fontSize: "18px",
          }}
        >
          Tripsonality
        </span>
      </div>
      <button
        onClick={onToggle}
        className="pl-3 py-2 bg-transparent border-none hover:opacity-80"
      >
        <HiChevronLeft size={24} />
      </button>
    </div>

    {/* Menu items */}
    <nav
      style={{
        flex: 1,
        display: "flex",
        flexDirection: "column",
        gap: "2px",
      }}
    >
      {menuItems.map((item) => (
        <button
          key={item}
          style={{
            fontFamily: "Georgia, serif",
            fontSize: "16px",
            padding: "12px 8px",
            width: "100%",
            textAlign: "center",
            border: "1px solid #d1d5db",
            // borderRadius: "6px",
            backgroundColor: "white",
            cursor: "pointer",
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.backgroundColor = "#f9fafb"; // hover 浅灰
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.backgroundColor = "white";
          }}
        >
          {item}
        </button>
      ))}
      
      {/* Special handling for Explore */}
      <button
        onClick={onExploreClick}
        style={{
          fontFamily: "Georgia, serif",
          fontSize: "16px",
          padding: "12px 8px",
          width: "100%",
          textAlign: "center",
          border: "1px solid #d1d5db",
          backgroundColor: "white",
          cursor: "pointer",
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.backgroundColor = "#f9fafb";
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.backgroundColor = "white";
        }}
      >
        Explore
      </button>
    </nav>

    {/* New Chat button */}
    <div style={{ marginTop: "2px", padding: "16px" }}>
      <button
        onClick={onNewChat}
        style={{
          fontFamily: "Georgia, serif",
          width: "100%",
          padding: "12px 8px",
          fontSize: "16px",
          backgroundColor: "#f3f4f6", // 灰色背景
          // borderRadius: "6px",
          border: "1px solid #d1d5db",
          cursor: "pointer",
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.backgroundColor = "#e5e7eb";
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.backgroundColor = "#f3f4f6";
        }}
      >
        New Chat
      </button>
    </div>
  </div>
);

export default Sidebar;
