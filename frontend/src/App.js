import React, { useState } from 'react';
import ChartComponent from './components/ChartComponent';
import NftCreator from './components/NftCreator';
import Marketplace from './components/Marketplace'; // Import Marketplace
import './App.css';

function App() {
  const [latestNft, setLatestNft] = useState(null);

  const handleNftMinted = (nftData) => {
    console.log("New NFT Minted in App.js:", nftData);
    setLatestNft(nftData);
  };

  // Basic layout styling (can be moved to App.css)
  const appLayoutStyles = {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center', // Center content horizontally
    gap: '20px', // Space between main sections
  };

  const sectionStyles = {
    width: '90%', // Make sections take up most of the width
    maxWidth: '1200px', // But not too wide on large screens
    padding: '10px',
    // border: '1px dashed #ccc', // Optional: to see section boundaries
  };


  return (
    <div className="App">
      <header className="App-header">
        <h1>PumpFun777 Crypto Dashboard & NFT Marketplace</h1>
      </header>
      <div style={appLayoutStyles}> {/* Apply layout styles */}
        <div style={sectionStyles} className="nft-creator-section">
          <NftCreator onNftMinted={handleNftMinted} />
        </div>
        
        <div style={sectionStyles} className="chart-section">
          <ChartComponent latestNft={latestNft} />
        </div>

        <div style={sectionStyles} className="marketplace-section">
          <Marketplace latestNft={latestNft} /> {/* Pass latestNft to Marketplace */}
        </div>
      </main>
    </div>
  );
}

export default App;
