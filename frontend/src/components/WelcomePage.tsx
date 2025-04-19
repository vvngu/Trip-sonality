import React from 'react';
import { FiMapPin, FiArrowRight } from 'react-icons/fi';

interface WelcomePageProps {
  onStart: () => void;
}

const WelcomePage: React.FC<WelcomePageProps> = ({ onStart }) => {
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
        <p className="text-xl text-gray-600 mb-14 max-w-lg mx-auto text-center">
          Tell us your interests, personality, and preferences.
          We'll craft a journey that's uniquely yours.
        </p>
        
        {/* Get Started Button */}
        <button 
          onClick={onStart}
          className="px-8 py-4 bg-black text-white rounded-full font-medium flex items-center justify-center mx-auto 
                    hover:bg-gray-800 transition-colors group text-lg mb-20"
        >
          Explore my journey
          <FiArrowRight size={20} className="ml-3 group-hover:translate-x-1 transition-transform" />
        </button>
        
        {/* Example Prompts */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 w-full px-8">
          {[
            "Explore LA's movie magic for 6 days",
            "Tour Tokyo's tech districts with my family",
            "Visit Paris for a food adventure"
          ].map((suggestion, i) => (
            <div 
              key={i} 
              onClick={onStart}
              className="p-5 bg-gray-50 border border-gray-200 rounded-xl text-center cursor-pointer hover:bg-gray-100 shadow-sm transition-all text-gray-700"
            >
              {suggestion}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default WelcomePage; 