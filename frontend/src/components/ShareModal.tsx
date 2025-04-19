import React, { useState, useRef } from 'react';
import { FiLink, FiCheck, FiX } from 'react-icons/fi';

interface ShareModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const ShareModal: React.FC<ShareModalProps> = ({ isOpen, onClose }) => {
  const [copied, setCopied] = useState(false);
  const urlRef = useRef<HTMLInputElement>(null);
  
  // If not open, don't render
  if (!isOpen) return null;
  
  const currentUrl = window.location.href;
  
  const handleCopy = () => {
    if (urlRef.current) {
      urlRef.current.select();
      document.execCommand('copy');
      setCopied(true);
      
      // Reset copied state after 2 seconds
      setTimeout(() => {
        setCopied(false);
      }, 2000);
    }
  };
  
  return (
    <div className="fixed inset-0 backdrop-blur-sm bg-white/30 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl p-6 max-w-md w-full mx-4 border border-gray-200">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-xl font-georgia font-medium text-gray-800">Share Itinerary</h3>
          <button 
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <FiX size={20} />
          </button>
        </div>
        
        <div className="mb-6">
          <p className="text-gray-600 mb-3">Share this unique trip with your friends and family:</p>
          <div className="flex items-center gap-2 border border-gray-300 rounded-lg p-2">
            <FiLink className="text-gray-500" size={16} />
            <input
              ref={urlRef}
              type="text"
              readOnly
              value={currentUrl}
              className="flex-1 bg-transparent outline-none font-mono text-sm text-gray-700"
            />
          </div>
        </div>
        
        <div className="flex gap-3 justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handleCopy}
            className={`px-4 py-2 rounded-lg flex items-center gap-2 text-white transition-colors ${
              copied ? 'bg-green-600' : 'bg-black hover:bg-gray-800'
            }`}
          >
            {copied ? (
              <>
                <FiCheck size={16} />
                Copied!
              </>
            ) : (
              <>
                Copy
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ShareModal; 