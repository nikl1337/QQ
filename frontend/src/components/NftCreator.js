import React, { useState } from 'react';
import { mintNft } from '../services/api'; // Assuming api.js is in ../services

const NftCreator = ({ onNftMinted }) => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [nftType, setNftType] = useState('long'); // Default to 'long'
  const [isLoading, setIsLoading] = useState(false);
  const [feedback, setFeedback] = useState(null); // For messages like "Minting..." or "NFT Minted!"
  const [mintedNftData, setMintedNftData] = useState(null); // To display the minted NFT details

  const handleFileChange = (event) => {
    setSelectedFile(event.target.files[0]);
    setFeedback(null); // Clear previous feedback
    setMintedNftData(null); // Clear previously minted NFT display
  };

  const handleTypeChange = (event) => {
    setNftType(event.target.value);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!selectedFile) {
      setFeedback({ type: 'error', message: 'Please select an image file.' });
      return;
    }

    setIsLoading(true);
    setFeedback({ type: 'info', message: 'Minting NFT...' });
    setMintedNftData(null);

    try {
      const responseData = await mintNft(selectedFile, nftType);
      setFeedback({ type: 'success', message: 'NFT Minted Successfully!' });
      setMintedNftData(responseData); // Store minted NFT data to display
      if (onNftMinted) {
        onNftMinted(responseData); // Pass the minted NFT data to the parent component (App.js)
      }
    } catch (error) {
      // The error from api.js should be an object with a message or error.message
      setFeedback({ type: 'error', message: error.message || 'Failed to mint NFT. Please try again.' });
      console.error("Minting error in component:", error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{ border: '1px solid #ccc', padding: '20px', margin: '20px 0' }}>
      <h2>Create Your NFT</h2>
      <form onSubmit={handleSubmit}>
        <div>
          <label htmlFor="fileInput">Upload Image: </label>
          <input 
            type="file" 
            id="fileInput"
            accept="image/png, image/jpeg, image/jpg" 
            onChange={handleFileChange} 
            disabled={isLoading}
          />
        </div>
        <div style={{ margin: '10px 0' }}>
          <label>NFT Type: </label>
          <label>
            <input 
              type="radio" 
              value="long" 
              checked={nftType === 'long'} 
              onChange={handleTypeChange} 
              disabled={isLoading}
            /> Long (SOL)
          </label>
          <label style={{ marginLeft: '10px' }}>
            <input 
              type="radio" 
              value="short" 
              checked={nftType === 'short'} 
              onChange={handleTypeChange} 
              disabled={isLoading}
            /> Short (BTC)
          </label>
        </div>
        <button type="submit" disabled={isLoading || !selectedFile}>
          {isLoading ? 'Minting...' : 'Mint NFT'}
        </button>
      </form>
      {feedback && (
        <p style={{ color: feedback.type === 'error' ? 'red' : 'green' }}>
          {feedback.message}
        </p>
      )}
      {mintedNftData && (
        <div style={{ marginTop: '20px', borderTop: '1px solid #eee', paddingTop: '10px' }}>
          <h3>Minted NFT Details:</h3>
          <p><strong>ID:</strong> {mintedNftData.id}</p>
          <p><strong>Type:</strong> {mintedNftData.nft_type}</p>
          <p><strong>Timestamp:</strong> {new Date(mintedNftData.creation_timestamp).toLocaleString()}</p>
          <p><strong>Minting Price (BTC):</strong> {mintedNftData.minting_price_btc} USD</p>
          <p><strong>Minting Price (SOL):</strong> {mintedNftData.minting_price_sol} USD</p>
          {mintedNftData.gif_url && (
            <div>
              <p><strong>Generated GIF:</strong></p>
              {/* Construct full URL if backend returns relative path */}
              <img 
                src={mintedNftData.gif_url.startsWith('http') ? mintedNftData.gif_url : `${window.location.origin}${mintedNftData.gif_url}`} 
                alt="Minted NFT GIF" 
                style={{ maxWidth: '100%', height: 'auto', border: '1px solid grey' }} 
              />
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default NftCreator;
