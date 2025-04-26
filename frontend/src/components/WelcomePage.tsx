import React, { useState } from 'react';
import { FiMapPin, FiArrowRight } from 'react-icons/fi';
import Select from 'react-select';

interface WelcomePageProps {
  onStart: (data: { 
    prompt: string; 
    mbti: string | null; 
    budget: string | null 
  }) => void;
}

const WelcomePage: React.FC<WelcomePageProps> = ({ onStart }) => {
  const [promptInput, setPromptInput] = useState('');
  const [mbti, setMbti] = useState<{ value: string; label: string } | null>(null);
  const [budget, setBudget] = useState<{ value: string; label: string } | null>(null);

  const mbtiOptions = [
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

  const budgetOptions = [
    { value: "500 USD", label: "500 USD" },
    { value: "1000 USD", label: "1000 USD" },
    { value: "1500 USD", label: "1500 USD" },
    { value: "2000 USD", label: "2000 USD" },
    { value: "2500+ USD", label: "2500+ USD" },
  ];

  const handleSubmit = () => {
    // Pass the selected MBTI and budget values to the parent
    onStart({
      prompt: promptInput,
      mbti: mbti?.value || null,
      budget: budget?.value || null
    });
  };

  const handleSuggestionClick = (suggestion: string) => {
    setPromptInput(suggestion);
  };

  return (
    <div className="h-full w-full flex items-center justify-center">
      <div className="w-full max-w-3xl flex flex-col items-center">
        {/* Logo */}
        <div className="mb-10 flex justify-center">
          <div className="p-4 bg-gray-50 rounded-full">
            <FiMapPin size={42} className="text-gray-800" />
          </div>
        </div>
        
        {/* Welcome Text */}
        <h1 className="text-5xl font-georgia mb-8 text-gray-800 leading-tight text-center">
          Trip, Trip, Trip<br />where are you going?
        </h1>
        
        {/* Description */}
        <p className="text-xl text-gray-600 mb-10 max-w-lg mx-auto text-center">
          Tell us your interests, personality, and preferences.
          We'll craft a journey that's uniquely yours.
        </p>
        
        {/* Get Started Button */}
        <button 
          onClick={handleSubmit}
          className="px-8 py-4 bg-black text-white rounded-full font-medium flex items-center justify-center mx-auto 
                    hover:bg-gray-800 transition-colors group text-lg mb-12"
        >
          Explore my journey
          <FiArrowRight size={20} className="ml-3 group-hover:translate-x-1 transition-transform" />
        </button>
        
        {/* Example Prompts */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 w-full px-8 mb-12">
          {[
            "Explore LA's movie magic for 6 days",
            "Tour Tokyo's tech districts with my family",
            "Visit Paris for a food adventure"
          ].map((suggestion, i) => (
            <div 
              key={i} 
              onClick={() => handleSuggestionClick(suggestion)}
              className="p-5 bg-gray-50 border border-gray-200 rounded-xl text-center cursor-pointer hover:bg-gray-100 shadow-sm transition-all text-gray-700"
            >
              {suggestion}
            </div>
          ))}
        </div>
        
        {/* Chat Input - Moved to bottom */}
        <div className="w-full px-8 mb-6">
          <div className="bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden">
            <div className="p-4">
              <div className="relative">
                <input
                  type="text"
                  placeholder="Describe your dream trip..."
                  value={promptInput}
                  onChange={(e) => setPromptInput(e.target.value)}
                  className="w-full p-4 pr-10 border border-gray-200 rounded-lg text-sm font-georgia"
                />
                <button
                  onClick={handleSubmit}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                >
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
                  <span className="text-xs text-gray-600 font-medium font-georgia whitespace-nowrap">
                    MBTI:
                  </span>
                  {/* @ts-ignore */}
                  <Select
                    options={mbtiOptions}
                    value={mbti}
                    onChange={setMbti}
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
                        zIndex: 9999,
                      }),
                    }}
                    className="w-auto text-xs font-georgia"
                    placeholder="Select..."
                  />
                </div>

                {/* Budget Select */}
                <div className="rounded-full border border-gray-300 flex items-center px-3 shadow-sm hover:border-gray-400 transition-colors">
                  <span className="text-xs text-gray-600 font-medium font-georgia whitespace-nowrap">
                    Budget:
                  </span>
                  {/* @ts-ignore */}
                  <Select
                    options={budgetOptions}
                    value={budget}
                    onChange={setBudget}
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
                        zIndex: 9999,
                      }),
                    }}
                    className="w-auto text-xs font-georgia"
                    placeholder="Select..."
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default WelcomePage; 