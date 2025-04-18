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
    style={{
      width,
      display: "flex",
      flexDirection: "column",
      backgroundColor: "white",
      borderRight: "2px solid #d1d5db", // 更粗灰色边框
      height: "100vh",
      boxSizing: "border-box",
      // padding: "16px",
    }}
  >
    {/* Logo and hide button */}
    <div
      style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        marginBottom: "24px",
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
            fontFamily: "serif",
            fontWeight: "bold",
            fontSize: "18px",
          }}
        >
          Tripsonality
        </span>
      </div>
      <button
        onClick={onToggle}
        style={{ padding: "8px", border: "none", background: "none" }}
      >
        ✕
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
    </nav>

    {/* New Chat button */}
    <div style={{ marginTop: "24px", padding: "16px" }}>
      <button
        style={{
          width: "100%",
          padding: "12px 8px",
          fontSize: "16px",
          backgroundColor: "#f3f4f6", // 灰色背景
          borderRadius: "6px",
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
    <div className="p-4 space-y-4">
    <div className="text-sm bg-gray-100">text-sm</div>
      <div className="text-lg bg-gray-200">text-lg</div>
      <div className="text-2xl bg-gray-300">text-2xl</div>
      <div className="text-4xl bg-gray-400">text-4xl</div>
      <div className="text-5xl bg-gray-500">text-5xl</div>
    </div>
  </div>
);

export default Sidebar;
