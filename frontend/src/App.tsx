import React, { useState, useRef, useEffect } from "react";
import Sidebar from "./components/sidebar";
import { MapView } from "./components/map-view";
import { ChatHeader } from "./components/chat-header";

export default function App() {
  const [mbti, setMbti] = useState("INFJ");
  const [budget, setBudget] = useState("1500 USD");
  const [sidebarWidth, setSidebarWidth] = useState(200);
  const [collapsed, setCollapsed] = useState(false);
  const isDragging = useRef(false);

  // Handle dragging to resize sidebar
  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (isDragging.current && !collapsed) {
        setSidebarWidth((prev) => {
          const next = prev + e.movementX;
          return Math.max(100, Math.min(next, 400)); // clamp between 100 and 400px
        });
      }
    };
    const handleMouseUp = () => {
      isDragging.current = false;
    };
    window.addEventListener("mousemove", handleMouseMove);
    window.addEventListener("mouseup", handleMouseUp);
    return () => {
      window.removeEventListener("mousemove", handleMouseMove);
      window.removeEventListener("mouseup", handleMouseUp);
    };
  }, [collapsed]);

  const handleMouseDown = () => {
    isDragging.current = true;
  };

  const mbtiOptions = [
    "INTJ",
    "INTP",
    "ENTJ",
    "ENTP",
    "INFJ",
    "INFP",
    "ENFJ",
    "ENFP",
    "ISTJ",
    "ISFJ",
    "ESTJ",
    "ESFJ",
    "ISTP",
    "ISFP",
    "ESTP",
    "ESFP",
  ];
  const budgetOptions = [
    "500 USD",
    "1000 USD",
    "1500 USD",
    "2000 USD",
    "2500+ USD",
  ];

  return (
    <div className="flex h-screen relative">
      {/* Sidebar & Toggle */}
      {!collapsed && (
        <Sidebar width={sidebarWidth} onToggle={() => setCollapsed(true)} />
      )}
      {collapsed && (
        <button
          onClick={() => setCollapsed(false)}
          className="absolute top-4 left-4 p-2 bg-white border border-gray-200 rounded"
        >
          ☰
        </button>
      )}
      {/* Divider for resizing */}
      {!collapsed && (
        <div
          onMouseDown={handleMouseDown}
          className="cursor-ew-resize bg-transparent"
          style={{ width: "4px" }}
        />
      )}

      {/* Main content area */}
      <div className="flex-1 flex flex-col font-sans bg-white">
        {/* Top buttons */}
        <div className="flex justify-end p-3 gap-2">
          <button className="px-6 py-2 border border-gray-200 rounded-full text-lg">
            Button 1
          </button>
          <button className="px-6 py-2 border border-gray-200 rounded-full text-lg">
            Button 2
          </button>
        </div>

        {/* Chat & Itinerary grid */}
        <div className="flex-1 p-4">
          <ChatHeader
            theme="INFJ Movie Trip"
            location="Los Angeles, CA, U.S."
            dates="05.20.2025 - 05.26.2025"
          />
          <div className="grid grid-cols-[1fr_350px] gap-4 h-[calc(100%-80px)]">
            {/* Map panel */}
            <div className="panel rounded-custom overflow-hidden">
              <MapView />
            </div>

            {/* Itinerary and input panel */}
            <div className="flex flex-col gap-4">
              {/* Itinerary */}
              <div className="panel rounded-custom">
                <h2 className="text-center font-georgia font-medium text-xl mb-4">
                  6 Days Itinerary
                </h2>
                <div className="space-y-4">
                  {[1, 2, 3, 4, 5, 6].map((day) => (
                    <div key={day} className="grid grid-cols-2 gap-2">
                      <div className="border border-gray-200 p-3 rounded-lg">
                        <div className="text-md font-medium">Morning</div>
                      </div>
                      <div className="border border-gray-200 p-3 rounded-lg">
                        <div className="text-md font-medium">Afternoon</div>
                      </div>
                    </div>
                  ))}
                </div>
                <div className="flex justify-center mt-6">
                  <div className="flex gap-1">
                    {[1, 2, 3, 4, 5, 6, 7, 8, 9].map((i) => (
                      <span
                        key={i}
                        className={`w-2 h-2 rounded-full ${
                          i === 1 ? "bg-black" : "bg-gray-300"
                        }`}
                      ></span>
                    ))}
                  </div>
                </div>
              </div>

              {/* Input section */}
              <div className="panel rounded-custom">
                <div className="relative">
                  <input
                    type="text"
                    placeholder="Enter your Destination, Interests and Dislikes..."
                    className="w-full p-4 pr-10 border border-gray-200 rounded-lg text-lg"
                  />
                  <button className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400">
                    <svg
                      width="24"
                      height="24"
                      viewBox="0 0 24 24"
                      fill="none"
                      xmlns="http://www.w3.org/2000/svg"
                    >
                      <path
                        d="M22 2L11 13"
                        stroke="currentColor"
                        strokeWidth="2"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      />
                      <path
                        d="M22 2L15 22L11 13L2 9L22 2Z"
                        stroke="currentColor"
                        strokeWidth="2"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      />
                    </svg>
                  </button>
                </div>
                <div className="mt-4 flex flex-wrap items-center gap-3">
                  {/* MBTI Select */}
                  <div className="flex flex-col gap-1">
                    <label
                      htmlFor="mbti-select"
                      className="text-sm text-gray-500"
                    >
                      MBTI:
                    </label>
                    <select
                      id="mbti-select"
                      className="bg-gray-100 px-4 py-2 rounded-lg border border-gray-200 text-lg"
                      value={mbti}
                      onChange={(e) => setMbti(e.target.value)}
                    >
                      {mbtiOptions.map((opt) => (
                        <option key={opt} value={opt}>
                          {opt}
                        </option>
                      ))}
                    </select>
                  </div>
                  {/* Budget Select */}
                  <div className="flex flex-col gap-1">
                    <label
                      htmlFor="budget-select"
                      className="text-sm text-gray-500"
                    >
                      Budget:
                    </label>
                    <select
                      id="budget-select"
                      className="bg-gray-100 px-4 py-2 rounded-lg border border-gray-200 text-lg"
                      value={budget}
                      onChange={(e) => setBudget(e.target.value)}
                    >
                      {budgetOptions.map((opt) => (
                        <option key={opt} value={opt}>
                          {opt}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="text-center text-xs text-gray-400 py-1">
          ©Copyright: Tripsonality Team, 2025
        </div>
      </div>
    </div>
  );
}
