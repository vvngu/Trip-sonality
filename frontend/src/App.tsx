// src/App.tsx
import React, { useState, useRef, useEffect } from "react";
import Sidebar from "./components/sidebar";
import { MapView } from "./components/map-view";
import { ChatHeader } from "./components/chat-header";
import Itinerary from "./components/itinerary";
import Select, { SingleValue } from "react-select";
import { FiShare2 } from "react-icons/fi";
import { FaSignInAlt } from "react-icons/fa";

//
// ——— Types ———
//
type MBTI =
  | "INTJ"
  | "INTP"
  | "ENTJ"
  | "ENTP"
  | "INFJ"
  | "INFP"
  | "ENFJ"
  | "ENFP"
  | "ISTJ"
  | "ISFJ"
  | "ESTJ"
  | "ESFJ"
  | "ISTP"
  | "ISFP"
  | "ESTP"
  | "ESFP";

interface OptionType {
  value: MBTI;
  label: string;
}

interface BudgetOption {
  value: string;
  label: string;
}

//
// ——— Option Data ———
//
const mbtiOptions: OptionType[] = [
  { value: "INTJ", label: "INTJ" },
  { value: "INTP", label: "INTP" },
  { value: "ENTJ", label: "ENTJ" },
  { value: "ENTP", label: "ENTP" },
  { value: "INFJ", label: "INFJ" },
  { value: "INFP", label: "INFP" },
  { value: "ENFJ", label: "ENFJ" },
  { value: "ENFP", label: "ENFP" },
  { value: "ISTJ", label: "ISTJ" },
  { value: "ISFJ", label: "ISFJ" },
  { value: "ESTJ", label: "ESTJ" },
  { value: "ESFJ", label: "ESFJ" },
  { value: "ISTP", label: "ISTP" },
  { value: "ISFP", label: "ISFP" },
  { value: "ESTP", label: "ESTP" },
  { value: "ESFP", label: "ESFP" },
];

const budgetOptionsSelect: BudgetOption[] = [
  "500 USD",
  "1000 USD",
  "1500 USD",
  "2000 USD",
  "2500+ USD",
].map((b) => ({ value: b, label: b }));

//
// ——— App Component ———
//
export default function App() {
  const [themeInput, setThemeInput] = useState<string>("Movie");
  const [locationInput, setLocationInput] = useState<string>("Los Angeles, CA");
  const [datesInput, setDatesInput] = useState<string>("6 days");
  const [mbti, setMbti] = useState<MBTI>("INFJ");
  const [budget, setBudget] = useState<string>("1500 USD");
  const [fieldInput, setFieldInput] = useState<string>("");
  const [sidebarWidth, setSidebarWidth] = useState(200);
  const [mapPanelWidth, setMapPanelWidth] = useState(0);
  const [collapsed, setCollapsed] = useState(false);

  const sidebarDraggingRef = useRef(false);
  const mapPanelDraggingRef = useRef(false);
  const containerRef = useRef<HTMLDivElement>(null);

  // initialize mapPanelWidth
  useEffect(() => {
    if (containerRef.current) {
      const cw = containerRef.current.clientWidth;
      setMapPanelWidth(cw - 400 - 16);
    }
  }, [collapsed]);

  // dragging logic
  useEffect(() => {
    const onMouseMove = (e: MouseEvent) => {
      if (sidebarDraggingRef.current && !collapsed) {
        setSidebarWidth((prev) =>
          Math.max(175, Math.min(prev + e.movementX, 300))
        );
      }
      if (mapPanelDraggingRef.current) {
        setMapPanelWidth((prev) => {
          const next = prev + e.movementX;
          const cw = containerRef.current?.clientWidth || 0;
          const maxW = cw - 400 - 16;
          return Math.max(300, Math.min(next, maxW));
        });
      }
    };
    const onMouseUp = () => {
      sidebarDraggingRef.current = false;
      mapPanelDraggingRef.current = false;
    };
    window.addEventListener("mousemove", onMouseMove);
    window.addEventListener("mouseup", onMouseUp);
    return () => {
      window.removeEventListener("mousemove", onMouseMove);
      window.removeEventListener("mouseup", onMouseUp);
    };
  }, [collapsed]);

  const handleSidebarMouseDown = () => {
    sidebarDraggingRef.current = true;
  };
  const handleMapPanelMouseDown = () => {
    mapPanelDraggingRef.current = true;
  };

  const handleMbtiChange = (opt: SingleValue<OptionType>) => {
    if (opt) setMbti(opt.value);
  };
  const handleBudgetChange = (opt: SingleValue<BudgetOption>) => {
    if (opt) setBudget(opt.value);
  };

  const handleSend = () => {
    const payload = {
      theme: themeInput,
      location: locationInput,
      dates: datesInput,
      field: fieldInput,
      mbti,
      budget,
    };
    // fetch("/api/trip", {
    //   method: "POST",
    //   headers: { "Content-Type": "application/json" },
    //   body: JSON.stringify(payload),
    // })
    //   .then((res) => res.json())
    //   .then((data) => console.log("Response:", data))
    //   .catch((err) => console.error(err));
    console.log("Payload to send:", payload);
  };

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
      {!collapsed && (
        <div
          onMouseDown={handleSidebarMouseDown}
          className="cursor-ew-resize bg-transparent"
          style={{ width: "4px" }}
        />
      )}

      {/* Main Area */}
      <div
        className="flex-1 flex flex-col font-sans bg-white"
        ref={containerRef}
      >
        {/* Top Buttons */}
        <div className="flex justify-end p-3 gap-2">
          <button className="font-georgia px-4 py-2 border border-gray-300 rounded-full flex items-center gap-2 text-gray-500 hover:bg-gray-100 transition">
            <FiShare2 size={16} />
            <span>Share</span>
          </button>

          <button className="font-georgia px-4 py-2 border border-gray-300 rounded-full flex items-center gap-2 text-gray-500 hover:bg-gray-100 transition">
            <FaSignInAlt size={16} />
            <span>Sign In</span>
          </button>
        </div>
        {/* Content */}
        <div className="flex-1 p-4 flex gap-4">
          {/* Left Panel */}
          <div
            className="flex flex-col"
            style={{ flex: mapPanelWidth ? `0 0 ${mapPanelWidth}px` : "1" }}
          >
            <ChatHeader
              theme={themeInput}
              location={locationInput}
              dates={datesInput}
              onThemeChange={setThemeInput}
              onLocationChange={setLocationInput}
              onDatesChange={setDatesInput}
            />
            <div className="panel rounded-custom overflow-hidden flex-1 mt-1">
              <MapView />
            </div>
          </div>

          {/* Map Resize Divider */}
          <div
            onMouseDown={handleMapPanelMouseDown}
            className="cursor-ew-resize relative"
            style={{ width: "2px" }}
          >
            <div className="absolute top-0 bottom-0 left-1 w-1 hover:bg-gray-300 hover:w-2 transition-all h-full rounded" />
          </div>

          {/* Right Panel */}
          <div className="flex flex-col gap-4 flex-1">
            {/* Itinerary */}
            {/* <div className="panel rounded-custom flex-1 overflow-auto">
              <h2 className="text-center font-georgia font-medium text-xl mb-4">
                6 Days Itinerary
              </h2>
              <div className="space-y-4">
                {[1, 2, 3, 4, 5, 6].map((d) => (
                  <div key={d} className="grid grid-cols-2 gap-2">
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
                    />
                  ))}
                </div>
              </div>
            </div> */}
            <Itinerary />

            {/* Input Section */}
            <div className="panel rounded-custom">
              <div className="relative">
                <input
                  type="text"
                  placeholder="Enter your Interests and Dislikes..."
                  value={fieldInput}
                  onChange={(e) => setFieldInput(e.target.value)}
                  className="w-full p-4 pr-10 border border-gray-200 rounded-lg text-sm"
                />
                <button
                  onClick={handleSend}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400"
                >
                  {/* paper-plane arrow SVG */}
                  <svg
                    width="24"
                    height="24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    viewBox="0 0 24 24"
                  >
                    <path d="M22 2L11 13" />
                    <path d="M22 2L15 22L11 13L2 9L22 2Z" />
                  </svg>
                </button>
              </div>

              <div className="mt-4 flex items-center justify-between space-x-4">
                {/* MBTI Select */}
                <div className="rounded-full border border-gray-300 flex items-center px-3 shadow-sm hover:border-gray-400 transition-colors">
                  <span className="text-xs text-gray-600 font-medium">
                    MBTI:
                  </span>
                  <Select<OptionType, false>
                    options={mbtiOptions}
                    value={mbtiOptions.find((o) => o.value === mbti) || null}
                    onChange={handleMbtiChange}
                    isSearchable={false}
                    menuPlacement="auto" // try "top" if you always want it above
                    menuPortalTarget={document.body}
                    styles={{
                      control: (base) => ({
                        ...base,
                        backgroundColor: "transparent",
                        border: "none",
                        boxShadow: "none",
                        minHeight: "auto",
                        fontSize: "0.65rem", // even smaller
                      }),
                      singleValue: (base) => ({
                        ...base,
                        color: "#ef4444", // only selected = red
                      }),
                      option: (base, state) => ({
                        ...base,
                        color: "black", // dropdown items = black
                        backgroundColor: state.isFocused ? "#f3f4f6" : "white",
                        cursor: "pointer",
                        fontSize: "0.65rem",
                      }),
                      dropdownIndicator: (base) => ({
                        ...base,
                        color: "black",
                        padding: 2,
                      }),
                      indicatorSeparator: () => ({ display: "none" }),
                      menuPortal: (base) => ({
                        ...base,
                        zIndex: 9999, // make sure it floats above everything
                      }),
                    }}
                    className="w-auto text-xs"
                  />
                </div>

                {/* Budget Select */}
                <div className="rounded-full border border-gray-300 flex items-center px-3 shadow-sm hover:border-gray-400 transition-colors">
                  <span className="text-xs text-gray-600 font-medium">
                    Budget:
                  </span>
                  <Select<BudgetOption, false>
                    options={budgetOptionsSelect}
                    value={
                      budgetOptionsSelect.find((o) => o.value === budget) ||
                      null
                    }
                    onChange={handleBudgetChange}
                    isSearchable={false}
                    menuPlacement="auto" // try "top" if you always want it above
                    menuPortalTarget={document.body}
                    styles={{
                      control: (base) => ({
                        ...base,
                        backgroundColor: "transparent",
                        border: "none",
                        boxShadow: "none",
                        minHeight: "auto",
                        fontSize: "0.65rem",
                      }),
                      singleValue: (base) => ({
                        ...base,
                        color: "#ef4444",
                      }),
                      option: (base, state) => ({
                        ...base,
                        color: "black",
                        backgroundColor: state.isFocused ? "#f3f4f6" : "white",
                        cursor: "pointer",
                        fontSize: "0.65rem",
                      }),
                      dropdownIndicator: (base) => ({
                        ...base,
                        color: "black",
                        padding: 2,
                      }),
                      indicatorSeparator: () => ({ display: "none" }),
                      menuPortal: (base) => ({
                        ...base,
                        zIndex: 9999, // make sure it floats above everything
                      }),
                    }}
                    className="w-auto text-xs"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="text-center text-xs text-gray-400 py-1">
          © Tripsonality Team, 2025
        </div>
      </div>
    </div>
  );
}
