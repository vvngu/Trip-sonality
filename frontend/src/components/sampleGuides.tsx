import React from "react";
import { FiSearch, FiHeart } from "react-icons/fi";

interface GuideProps {
  title: string;
  location: string;
  subLocation: string;
  author: string;
  authorUsername: string;
  days?: number;
  places?: number;
  image: string;
}

const guides: GuideProps[] = [
  {
    title: "2 Days in Austin, TX",
    location: "Austin",
    subLocation: "Texas",
    author: "tripsonality",
    authorUsername: "tripsonality",
    days: 2,
    image: "https://images.unsplash.com/photo-1531218150217-54595bc2b934?w=800&auto=format"
  },
  {
    title: "Museum & History Date in New York City",
    location: "New York",
    subLocation: "New York",
    author: "thatsumsum",
    authorUsername: "thatsumsum",
    places: 8,
    image: "https://images.unsplash.com/photo-1522083165195-3424ed129620?w=800&auto=format"
  },
  {
    title: "Bar Hopping in Night NYC",
    location: "New York",
    subLocation: "New York",
    author: "emilyistraveling",
    authorUsername: "emilyistraveling",
    places: 5,
    image: "https://images.unsplash.com/photo-1534430480872-3498386e7856?w=800&auto=format"
  },
  {
    title: "3 Days Culture trip in Salt Lake City",
    location: "Salt Lake City",
    subLocation: "Utah",
    author: "brandneweats",
    authorUsername: "brandneweats",
    days: 3,
    image: "https://plus.unsplash.com/premium_photo-1697730000221-148468fe7f6b?q=80&w=3271&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"
  },
  {
    title: "5 Days Getaway in Honolulu",
    location: "Honolulu",
    subLocation: "Hawaii",
    author: "seemonterey",
    authorUsername: "seemonterey",
    days: 5,
    image: "https://images.unsplash.com/photo-1507699622108-4be3abd695ad?w=800&auto=format"
  },
  {
    title: "Top 10 Restaurants in San Francisco",
    location: "San Francisco",
    subLocation: "California",
    author: "seemonterey",
    authorUsername: "seemonterey",
    places: 10,
    image: "https://images.unsplash.com/photo-1501594907352-04cda38ebc29?w=800&auto=format"
  }
];

const SampleGuides: React.FC = () => {
  return (
    <div className="p-8 font-sans">
      <h1 className="text-4xl font-bold mb-8">Inspiration</h1>
      
      {/* Tabs */}
      <div className="flex gap-4 mb-8">
        <button className="px-4 py-2 bg-black text-white rounded-full">All</button>
        <button className="px-4 py-2 hover:bg-gray-100 rounded-full">Itineraries</button>
        <button className="px-4 py-2 hover:bg-gray-100 rounded-full">Lists</button>
      </div>
      
      {/* Search */}
      <div className="relative mb-12">
        <input
          type="text"
          placeholder="Search for location or username"
          className="w-full p-4 pl-12 pr-10 border border-gray-200 rounded-full bg-gray-50"
        />
        <FiSearch className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
      </div>
      
      {/* Featured Guides */}
      <h2 className="text-2xl font-bold mb-6">Featured guides</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {guides.map((guide, index) => (
          <div key={index} className="relative rounded-xl overflow-hidden bg-white shadow-sm border border-gray-100">
            {/* Image */}
            <div className="relative h-60 overflow-hidden">
              <img 
                src={guide.image} 
                alt={guide.title} 
                className="w-full h-full object-cover"
              />
              
              {/* Days/Places Badge */}
              <div className="absolute top-3 left-3 bg-white px-2 py-1 rounded-full text-xs font-medium">
                {guide.days ? `${guide.days} days` : `${guide.places} places`}
              </div>
              
              {/* Heart Button */}
              <button className="absolute top-3 right-3 bg-white p-2 rounded-full shadow-sm hover:bg-gray-50">
                <FiHeart size={18} className="text-gray-700" />
              </button>
            </div>
            
            {/* Content */}
            <div className="p-4">
              <h3 className="font-bold text-lg mb-2">{guide.title}</h3>
              
              {/* Location */}
              <div className="flex items-center text-sm text-gray-600 mb-3">
                <span className="mr-1">📍</span>
                <span>{guide.location}{guide.subLocation && `, ${guide.subLocation}`}</span>
              </div>
              
              {/* Author */}
              <div className="flex items-center">
                <div className="w-6 h-6 rounded-full bg-gray-200 overflow-hidden flex items-center justify-center text-xs font-bold">
                  {guide.author.charAt(0).toUpperCase()}
                </div>
                <span className="ml-2 text-sm text-gray-600">{guide.authorUsername}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default SampleGuides; 