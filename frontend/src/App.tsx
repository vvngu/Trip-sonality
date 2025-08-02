// src/App.tsx
import React, { useState, useRef, useEffect } from "react";
import Sidebar from "./components/sidebar";
import { MapView } from "./components/map-view";
import { ChatHeader } from "./components/chat-header";
import Itinerary, {
  placeholderItinerary,
  ItineraryDay,
} from "./components/itinerary";
import Select, { SingleValue } from "react-select";
import { FiShare2, FiCalendar } from "react-icons/fi";
import WelcomePage from "./components/WelcomePage";
import ShareModal from "./components/ShareModal";
import SampleGuides from "./components/sampleGuides";

 function transformBackendData(backendData: any) {
  // Handle backend's nested structure: data.itinerary.itinerary
  const days = backendData?.data?.itinerary || [];
  
  return days.map((day: any) => ({
    day: day.day,
    food: {
      time: "12:00 PM",
      place: "Local Restaurant",
      cost: "$25",
      lat: day.activities[0]?.poi?.lat || 0,
      lng: day.activities[0]?.poi?.lng || 0
    },
    activities: day.activities.map((activity: any) => ({
      time: activity.time,
      place: activity.poi.name,  // poi.name -> place
      cost: activity.poi.price_level ? `$${activity.poi.price_level * 15}` : "$20",
      lat: activity.poi.lat,
      lng: activity.poi.lng
    })),
    summary: `Explore ${backendData.itinerary?.location || locationInput} with amazing ${backendData.itinerary?.theme || themeInput} experiences!`
  }));
}

// Simplified event attributes interface for ics
interface EventAttr {
  start: [number, number, number, number, number];
  duration: { hours: number };
  title: string;
  description?: string;
  location?: string;
  [key: string]: any;
}

// Simple mock implementation for the ics library's createEvents function
const createEvents = (
  events: EventAttr[],
  callback: (error: Error | null, value: string | undefined) => void
): void => {
  // In a real implementation, this would generate ICS content
  console.log("Creating events:", events);

  // For our mock, we'll just create a simple iCalendar file with basic content
  const icsContent = [
    "BEGIN:VCALENDAR",
    "VERSION:2.0",
    "PRODID:-//Trip-sonality//Trip-sonality Calendar//EN",
    ...events.flatMap((event) => [
      "BEGIN:VEVENT",
      `SUMMARY:${event.title}`,
      `DTSTART:${formatDate(event.start)}`,
      `DURATION:PT${event.duration.hours}H`,
      event.description ? `DESCRIPTION:${event.description}` : "",
      event.location ? `LOCATION:${event.location}` : "",
      "END:VEVENT",
    ]),
    "END:VCALENDAR",
  ]
    .filter(Boolean)
    .join("\r\n");

  callback(null, icsContent);
};

// Helper to format date for iCalendar
const formatDate = (
  dateArr: [number, number, number, number, number]
): string => {
  const [year, month, day, hour, minute] = dateArr;
  return `${year}${pad(month)}${pad(day)}T${pad(hour)}${pad(minute)}00Z`;
};

const pad = (num: number): string => {
  return num.toString().padStart(2, "0");
};

// 地点数据类型
interface LocationData {
  name: string;
  position: {
    lat: number;
    lng: number;
  };
}

// 提取位置信息函数
const extractLocationsFromItinerary = (
  itineraryData: any[]
): LocationData[] => {
  const locations: LocationData[] = [];

  if (!Array.isArray(itineraryData)) return locations;

  itineraryData.forEach((dayData) => {
    // 添加食物地点
    if (
      dayData.food &&
      dayData.food.place &&
      dayData.food.lat &&
      dayData.food.lng
    ) {
      locations.push({
        name: dayData.food.place,
        position: {
          lat: dayData.food.lat,
          lng: dayData.food.lng,
        },
      });
    }

    // 添加活动地点
    if (dayData.activities && Array.isArray(dayData.activities)) {
      dayData.activities.forEach((activity: any) => {
        if (activity.place && activity.lat && activity.lng) {
          locations.push({
            name: activity.place,
            position: {
              lat: activity.lat,
              lng: activity.lng,
            },
          });
        }
      });
    }
  });

  return locations;
};

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
  const [itinerary, setItinerary] = useState<ItineraryDay[]>([
    ...placeholderItinerary,
  ]);
  const [detailResult, setDetailResult] = useState<any>(null);
  const [themeInput, setThemeInput] = useState<string>("Movie");
  const [locationInput, setLocationInput] = useState<string>("Los Angeles");
  const [datesInput, setDatesInput] = useState<string>("6");
  const [mbti, setMbti] = useState<MBTI>("INFJ");
  const [budget, setBudget] = useState<string>("1500 USD");
  const [fieldInput, setFieldInput] = useState<string>("");
  const [sidebarWidth, setSidebarWidth] = useState(200);
  const [mapPanelWidth, setMapPanelWidth] = useState(0);
  const [collapsed, setCollapsed] = useState(false);
  const [showWelcome, setShowWelcome] = useState(() => {
    const savedState = localStorage.getItem("showWelcome");
    return savedState ? JSON.parse(savedState) : true;
  });
  const [highlightedPlace, setHighlightedPlace] = useState<string | undefined>(
    undefined
  );
  const [shareModalOpen, setShareModalOpen] = useState(false);
  const [showExplore, setShowExplore] = useState(false);
  const [isLocked, setIsLocked] = useState(false); // New state to track if inputs are locked

  // 新增：加载状态
  const [isLoading, setIsLoading] = useState(false);
  // 新增：地点数据 (用于地图显示)
  const [locations, setLocations] = useState<LocationData[]>([]);
  // 新增：SessionID
  const [sessionId, setSessionId] = useState<string | null>(null);

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
    if (opt && !isLocked) setMbti(opt.value);
  };
  const handleBudgetChange = (opt: SingleValue<BudgetOption>) => {
    if (opt && !isLocked) setBudget(opt.value);
  };

  const handleSend = () => {
    if (!locationInput) {
      alert("Please enter a location before generating an itinerary.");
      return;
    }

    if (!datesInput) {
      alert(
        "Please enter the length of your trip before generating an itinerary."
      );
      return;
    }

    // 设置加载状态为true
    setIsLoading(true);

    const payload = {
      mbti: mbti,
      budget: parseInt(budget.split(" ")[0]),
      query: `Create a ${themeInput} themed trip to ${locationInput} for ${datesInput} days${
        fieldInput ? ". I'm interested in " + fieldInput : ""
      }`,
      current_itinerary: null,
    };

    console.log("Sending payload:", payload);

    fetch("http://localhost:8000/plan", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    })
      .then((res) => {
        if (!res.ok) {
          return res.text().then((text) => {
            console.error("API错误响应:", text);
            throw new Error(`API返回错误: ${res.status} ${text}`);
          });
        }
        return res.json();
      })
      .then((data) => {
        console.log("收到API响应：", data);

        if (data.success && data.itinerary) {                
          // Transform backend data to frontend format
          const transformedData = transformBackendData(data);
          console.log("✅ Original backend data:", data);
          console.log("✅ Transformed data:", transformedData);
          console.log("✅ Number of days:", transformedData.length);

          setItinerary(transformedData);  
          // Extract locations for map from transformed data
          const locationData = extractLocationsFromItinerary(transformedData); // ✅ NEW: Use transformed
          setLocations(locationData);
          console.log("提取的位置数据:", locationData);
          console.log("Backend data transformed successfully");
        } else {
          console.warn("API返回的数据格式不符合预期:", data);
        }
      })
      .catch((err) => {
        console.error("请求错误:", err);
        alert("获取行程失败，请稍后重试");
      })
      .finally(() => {
        // 无论成功失败，都结束加载状态
        setIsLoading(false);
        // 锁定输入
        setIsLocked(true);
        setFieldInput("");
      });
  };

  // Save welcome state to localStorage when it changes
  useEffect(() => {
    localStorage.setItem("showWelcome", JSON.stringify(showWelcome));
  }, [showWelcome]);

  // Handler for "New Chat" button in sidebar
  const handleNewChat = () => {
    setShowWelcome(true);
    setShowExplore(false);
    // Reset locked state when starting a new chat
    setIsLocked(false);
    // 重置为初始状态
    setItinerary([...placeholderItinerary]);
    setSessionId(null);
    setLocations([]);
  };

  // Handler for Explore button
  const handleExploreClick = () => {
    setShowExplore(true);
    setShowWelcome(false);
  };

  // Handler for Share button
  const handleShareClick = () => {
    setShareModalOpen(true);
  };
  const handleExportCalendar = () => {
    const tripStartDate = new Date();

    // Create ICS events array
    const events: EventAttr[] = itinerary.flatMap((day, idx: number) => {
      const dayDate = new Date(tripStartDate);
      dayDate.setDate(tripStartDate.getDate() + idx);

      // Helper to convert time string to [year, month, day, hour, minute] tuple
      const toYMDHM = (
        timeStr: string
      ): [number, number, number, number, number] => {
        const [hm, suffix] = timeStr.split(" ");
        let [h, m] = hm.split(":").map(Number);
        if (suffix === "PM" && h < 12) h += 12;
        if (suffix === "AM" && h === 12) h = 0;
        return [
          dayDate.getFullYear(),
          dayDate.getMonth() + 1,
          dayDate.getDate(),
          h,
          m,
        ];
      };

      // Food event
      const foodStart = toYMDHM(day.food.time);
      const foodEvent: EventAttr = {
        title: `🍴 ${day.food.place}`,
        start: foodStart,
        duration: { hours: 1 },
        description: `Cost: ${day.food.cost}`,
        location: day.food.place,
      };

      // Activity events
      const activityEvents = day.activities.map((act) => {
        // Extract time components
        const timePart = `${act.time.split(" ")[0]} ${act.time.split(" ")[1]}`;
        const [year, month, date, startH, startM] = toYMDHM(timePart);
        const hoursMatch = act.time.match(/\((\d+)h\)/);
        const durHours = hoursMatch ? Number(hoursMatch[1]) : 1;
        return {
          title: `🎬 ${act.place}`,
          start: [year, month, date, startH, startM],
          duration: { hours: durHours },
          description: `Cost: ${act.cost}`,
          location: act.place,
        } as EventAttr;
      });

      return [foodEvent, ...activityEvents];
    });

    // Generate .ics file and trigger download
    createEvents(events, (error: Error | null, value: string | undefined) => {
      if (error) {
        console.error(error);
        return;
      }
      const blob = new Blob([value!], { type: "text/calendar;charset=utf-8" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "trip-itinerary.ics";
      a.click();
      URL.revokeObjectURL(url);
    });
  };

  // Handle welcome page form submission
  const handleWelcomeComplete = (data: {
    prompt: string;
    mbti: string | null;
    budget: string | null;
  }) => {
    // Set field input from prompt
    if (data.prompt) {
      setFieldInput(data.prompt);
    }

    // Set MBTI if provided
    if (data.mbti) {
      setMbti(data.mbti as MBTI);
    }

    // Set budget if provided
    if (data.budget) {
      setBudget(data.budget);
    }

    // Close welcome screen
    setShowWelcome(false);
  };

  return (
    <div className="flex h-screen relative">
      {/* Sidebar - Always visible regardless of welcome page */}
      {!collapsed && (
        <Sidebar
          width={sidebarWidth}
          onToggle={() => setCollapsed(true)}
          onNewChat={handleNewChat}
          onExploreClick={handleExploreClick}
        />
      )}
      {collapsed && (
        <button
          onClick={() => setCollapsed(false)}
          className="fixed top-4 left-4 p-2 bg-white border border-gray-200 rounded z-50"
        >
          ☰
        </button>
      )}
      {!collapsed && (
        <div
          onMouseDown={handleSidebarMouseDown}
          className="cursor-ew-resize bg-transparent fixed top-0 bottom-0"
          style={{
            width: "4px",
            left: `${sidebarWidth}px`,
            zIndex: 20,
          }}
        />
      )}

      {/* Share Modal */}
      <ShareModal
        isOpen={shareModalOpen}
        onClose={() => setShareModalOpen(false)}
      />

      {/* Main Content - Now includes explore page option */}
      <div
        className="flex-1 flex flex-col font-sans bg-white h-screen overflow-auto"
        ref={containerRef}
        style={{
          marginLeft: collapsed ? "0" : `${sidebarWidth + 4}px`, // Add margin to accommodate fixed sidebar
          width: collapsed ? "100%" : `calc(100% - ${sidebarWidth + 4}px)`, // Adjust width to accommodate sidebar
        }}
      >
        {showWelcome ? (
          <div className="flex-1 flex justify-center">
            <WelcomePage onStart={handleWelcomeComplete} />
          </div>
        ) : showExplore ? (
          <SampleGuides />
        ) : (
          <>
            {/* Loading Overlay */}
            {isLoading && (
              <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                <div className="bg-white p-6 rounded-lg shadow-lg flex flex-col items-center">
                  <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-red-500 mb-4"></div>
                  <p className="text-gray-700 font-georgia">
                    Generating your itinerary...
                  </p>
                </div>
              </div>
            )}

            {/* Top Buttons with Divider */}
            <div className="flex flex-col">
              <div className="flex justify-end p-3 gap-2">
                <button
                  onClick={handleShareClick}
                  className="font-georgia p-2 border border-gray-300 rounded-full flex items-center justify-center text-gray-500 hover:bg-gray-100 transition text-xs"
                  title="Share Itinerary"
                >
                  {/* @ts-ignore */}
                  <FiShare2 size={12} />
                </button>

                <button
                  onClick={handleExportCalendar}
                  className="font-georgia px-4 py-2 border border-gray-300 rounded-full flex items-center gap-2 text-gray-500 hover:bg-gray-100 transition"
                >
                  {/* @ts-ignore */}
                  <FiCalendar size={16} />
                  <span>Add to Calendar</span>
                </button>
              </div>
              <div className="border-b border-gray-200 mx-4 mb-1"></div>
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
                  isLocked={isLocked}
                />
                <div className="panel rounded-custom overflow-hidden flex-1 mt-1">
                  <MapView
                    highlightedPlace={highlightedPlace}
                    locations={locations.length > 0 ? locations : undefined}
                  />
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
                <Itinerary
                  itinerary={itinerary}
                  theme={themeInput}
                  location={locationInput}
                  onPlaceHover={setHighlightedPlace}
                />

                {/* Input Section */}
                <div className="panel rounded-custom">
                  <div className="relative">
                    <input
                      type="text"
                      placeholder="Enter your Interests and Dislikes..."
                      value={fieldInput}
                      onChange={(e) => setFieldInput(e.target.value)}
                      className="w-full p-4 pr-10 border border-gray-200 rounded-lg text-sm font-georgia"
                      disabled={isLoading} // 加载时禁用输入
                    />
                    <button
                      onClick={handleSend}
                      className={`absolute right-3 top-1/2 transform -translate-y-1/2 ${
                        isLoading
                          ? "text-gray-300"
                          : "text-gray-400 hover:text-gray-600"
                      }`}
                      disabled={isLoading} // 加载时禁用按钮
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
                    {/* MBTI - Display as text when locked */}
                    <div className="rounded-full border border-gray-300 flex items-center px-3 shadow-sm hover:border-gray-400 transition-colors">
                      <span className="text-xs text-gray-600 font-medium font-georgia">
                        MBTI:
                      </span>
                      {isLocked ? (
                        <span className="text-xs text-red-500 font-georgia ml-1 py-1">
                          {mbti}
                        </span>
                      ) : (
                        <Select<OptionType, false>
                          options={mbtiOptions}
                          value={
                            mbtiOptions.find((o) => o.value === mbti) || null
                          }
                          onChange={handleMbtiChange}
                          isSearchable={false}
                          menuPlacement="auto"
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
                              backgroundColor: state.isFocused
                                ? "#f3f4f6"
                                : "white",
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
                              zIndex: 9999,
                            }),
                          }}
                          className="w-auto text-xs font-georgia"
                        />
                      )}
                    </div>

                    {/* Budget - Display as text when locked */}
                    <div className="rounded-full border border-gray-300 flex items-center px-3 shadow-sm hover:border-gray-400 transition-colors">
                      <span className="text-xs text-gray-600 font-medium font-georgia">
                        Budget:
                      </span>
                      {isLocked ? (
                        <span className="text-xs text-red-500 font-georgia ml-1 py-1">
                          {budget}
                        </span>
                      ) : (
                        <Select<BudgetOption, false>
                          options={budgetOptionsSelect}
                          value={
                            budgetOptionsSelect.find(
                              (o) => o.value === budget
                            ) || null
                          }
                          onChange={handleBudgetChange}
                          isSearchable={false}
                          menuPlacement="auto"
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
                              backgroundColor: state.isFocused
                                ? "#f3f4f6"
                                : "white",
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
                              zIndex: 9999,
                            }),
                          }}
                          className="w-auto text-xs font-georgia"
                        />
                      )}
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Footer */}
            <div className="text-center text-xs text-gray-400 py-1">
              © Tripsonality Team, 2025
            </div>
          </>
        )}
      </div>
    </div>
  );
}
