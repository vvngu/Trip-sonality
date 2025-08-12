import React from "react";
import Select from "react-select";

interface ChatHeaderProps {
  theme: string;
  location: string;
  dates: string;
  onThemeChange: (value: string) => void;
  onLocationChange: (value: string) => void;
  onDatesChange: (value: string) => void;
  isLocked?: boolean; // New prop to determine if fields are locked
}
const themeOptions = [{ value: "Movie", label: "Movie" }];

const customSelectStyles = {
  control: (base: any) => ({
    ...base,
    border: "none",
    boxShadow: "none",
    background: "transparent",
    minHeight: "unset",
    cursor: "pointer",
    width: "100%",
    height: "100%",
  }),
  valueContainer: (base: any) => ({
    ...base,
    padding: "0",
    height: "100%",
  }),
  singleValue: (base: any) => ({
    ...base,
    fontFamily: "georgia",
    fontWeight: "500",
    fontSize: "0.875rem",
    color: "rgb(31, 41, 55)",
  }),
  placeholder: (base: any) => ({
    ...base,
    fontFamily: "georgia",
    fontWeight: "500",
    fontSize: "0.875rem",
  }),
  indicatorsContainer: (base: any) => ({
    ...base,
    padding: "0",
  }),
  dropdownIndicator: (base: any) => ({
    ...base,
    padding: "0 8px",
  }),
  menu: (base: any) => ({
    ...base,
    fontFamily: "georgia",
    fontWeight: "500",
    fontSize: "0.875rem",
    width: "100%",
    zIndex: 9999,
  }),
  menuList: (base: any) => ({
    ...base,
    fontFamily: "georgia",
    fontWeight: "500",
    fontSize: "0.875rem",
  }),
  option: (base: any, state: any) => ({
    ...base,
    fontFamily: "georgia",
    fontWeight: "500",
    fontSize: "0.875rem",
    backgroundColor: state.isSelected ? "rgb(243, 244, 246)" : "white",
    color: "rgb(31, 41, 55)",
    "&:hover": {
      backgroundColor: "rgb(243, 244, 246)",
    },
  }),
};

export const ChatHeader: React.FC<ChatHeaderProps> = ({
  theme,
  location,
  dates,
  onThemeChange,
  onLocationChange,
  onDatesChange,
  isLocked = false,
}) => (
  <div className="grid grid-cols-3 gap-2 mb-4 border border-gray-200 rounded-lg overflow-hidden">
    <div className="p-3 border-r border-gray-200 flex items-center space-x-2">
      <label className="text-gray-600 text-base font-georgia font-medium whitespace-nowrap">
        Theme:
      </label>
      {isLocked ? (
        <span className="flex-1 font-georgia font-medium text-sm text-gray-800">
          {theme}
        </span>
      ) : (
        <div className="flex-1" style={{ height: "24px" }}>
          <Select
            options={themeOptions}
            value={
              themeOptions.find((option) => option.value === theme) ||
              themeOptions[0]
            }
            onChange={(selectedOption) =>
              onThemeChange(selectedOption ? selectedOption.value : "Movie")
            }
            styles={customSelectStyles}
            isSearchable={false}
            placeholder="Select theme"
            menuPortalTarget={document.body}
            classNamePrefix="theme-select"
          />
        </div>
      )}
    </div>
    <div className="p-3 border-r border-gray-200 flex items-center space-x-2">
      <label className="text-gray-600 text-base font-georgia font-medium whitespace-nowrap">
        Location:
      </label>
      {isLocked ? (
        <span className="flex-1 font-georgia font-medium text-sm text-gray-800">
          {location}
        </span>
      ) : (
        <input
          type="text"
          placeholder="Enter location"
          className="flex-1 bg-transparent focus:outline-none font-georgia font-medium text-sm"
          value={location}
          onChange={(e) => onLocationChange(e.target.value)}
          required={true}
        />
      )}
    </div>
    <div className="p-3 flex items-center space-x-2">
      <label className="text-gray-600 text-base font-georgia font-medium whitespace-nowrap">
        Length:
      </label>
      {isLocked ? (
        <span className="flex-1 font-georgia font-medium text-sm text-gray-800">
          {dates}
        </span>
      ) : (
        <input
          type="text"
          placeholder="Enter dates"
          className="flex-1 bg-transparent focus:outline-none font-georgia font-medium text-sm"
          value={dates}
          onChange={(e) => onDatesChange(e.target.value)}
          required={true}
        />
      )}
    </div>
  </div>
);
