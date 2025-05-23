import React, { useState, useEffect } from 'react';
import { getAllNfts } from '../services/api'; // Assuming api.js is in ../services

const Marketplace = ({ latestNft }) => {
  const [nfts, setNfts] = useState([]);
  const [statusMessages, setStatusMessages] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchNfts = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await getAllNfts();
      // Sort NFTs by creation_timestamp in descending order (newest first)
      const sortedData = data.sort((a, b) => new Date(b.creation_timestamp) - new Date(a.creation_timestamp));
      setNfts(sortedData);
    } catch (err) {
      setError(err.message || 'Failed to fetch NFTs.');
      console.error("Error fetching NFTs for marketplace:", err);
    } finally {
      setIsLoading(false);
    }
  };

  // Fetch NFTs on component mount and when latestNft changes
  useEffect(() => {
    fetchNfts();
  }, [latestNft]); // Re-fetch when a new NFT is minted

  const handleBuy = (nftId) => {
    setStatusMessages(prev => ({ ...prev, [nftId]: "Owned by you (Simulated)" }));
  };

  const handleSell = (nftId) => {
    setStatusMessages(prev => ({ ...prev, [nftId]: "For Sale (Simulated)" }));
  };

  const handleClearStatus = (nftId) => {
    setStatusMessages(prev => {
      const newStatus = { ...prev };
      delete newStatus[nftId];
      return newStatus;
    });
  };

  const styles = {
    marketplaceContainer: {
      padding: '20px',
      border: '1px solid #eee',
      marginTop: '20px',
    },
    nftGrid: {
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', // Responsive grid
      gap: '20px',
    },
    nftCard: {
      border: '1px solid #ddd',
      borderRadius: '8px',
      padding: '15px',
      backgroundColor: '#f9f9f9',
    },
    nftImage: {
      width: '100%', // Make image responsive within card
      maxHeight: '200px', // Prevent very tall images from breaking layout
      objectFit: 'contain', // Show whole image, possibly with letterboxing
      borderBottom: '1px solid #eee',
      marginBottom: '10px',
    },
    buttonGroup: {
      marginTop: '10px',
      display: 'flex',
      gap: '5px', // spacing between buttons
    },
    button: {
      padding: '8px 12px',
      border: 'none',
      borderRadius: '4px',
      cursor: 'pointer',
    },
    buyButton: {
      backgroundColor: '#4CAF50', // Green
      color: 'white',
    },
    sellButton: {
      backgroundColor: '#f44336', // Red
      color: 'white',
    },
    clearButton: {
      backgroundColor: '#e0e0e0', // Light grey
      color: 'black',
    },
    statusMessage: {
      marginTop: '8px',
      fontWeight: 'bold',
      fontSize: '0.9em',
    },
    nftDetails: {
      fontSize: '0.85em',
      color: '#555',
    }
  };

  if (isLoading) return <div style={styles.marketplaceContainer}><p>Loading NFTs...</p></div>;
  if (error) return <div style={styles.marketplaceContainer}><p style={{color: 'red'}}>Error: {error}</p></div>;

  return (
    <div style={styles.marketplaceContainer}>
      <h2>NFT Marketplace (Simulated)</h2>
      {nfts.length === 0 && !isLoading && <p>No NFTs available in the marketplace yet.</p>}
      <div style={styles.nftGrid}>
        {nfts.map(nft => (
          <div key={nft.id} style={styles.nftCard}>
            <img 
              src={nft.gif_url} // Backend ensures this is a usable path like /api/nft/generated_gifs/...
              alt={`NFT ${nft.id}`} 
              style={styles.nftImage} 
            />
            <h4>NFT ID: {nft.id.substring(0, 8)}...</h4>
            <div style={styles.nftDetails}>
              <p><strong>Type:</strong> {nft.nft_type}</p>
              <p><strong>Minted:</strong> {new Date(nft.creation_timestamp).toLocaleString()}</p>
              <p><strong>Price (BTC):</strong> {nft.minting_price_btc} USD</p>
              <p><strong>Price (SOL):</strong> {nft.minting_price_sol} USD</p>
            </div>
            {statusMessages[nft.id] && (
              <p style={{...styles.statusMessage, color: statusMessages[nft.id].includes("Owned") ? 'green' : 'orange' }}>
                Status: {statusMessages[nft.id]}
              </p>
            )}
            <div style={styles.buttonGroup}>
              <button onClick={() => handleBuy(nft.id)} style={{...styles.button, ...styles.buyButton}}>Buy</button>
              <button onClick={() => handleSell(nft.id)} style={{...styles.button, ...styles.sellButton}}>Sell</button>
              {statusMessages[nft.id] && (
                <button onClick={() => handleClearStatus(nft.id)} style={{...styles.button, ...styles.clearButton}}>Clear Status</button>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Marketplace;
