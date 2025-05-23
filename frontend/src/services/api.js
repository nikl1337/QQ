// Placeholder for api.js services (e.g., fetching data from backend)
import axios from 'axios';

const API_BASE_URL = '/api'; // Adjust if your backend is on a different port/host during development

export const mintNft = async (imageData, nftType) => {
  const formData = new FormData();
  formData.append('file', imageData);
  formData.append('nft_type', nftType);

  try {
    // The backend's nft_routes.py uses '/api/nft/mint'
    // The Blueprint prefix is '/api/nft', and the route is '/mint'
    const response = await axios.post(`${API_BASE_URL}/nft/mint`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data; // This will be the nft_data from the backend
  } catch (error) {
    console.error("Error minting NFT:", error.response ? error.response.data : error.message);
    throw error.response ? error.response.data : new Error('Network error or server issue');
  }
};

export const getAllNfts = async () => {
  try {
    // The backend endpoint is /api/nft/all
    const response = await axios.get(`${API_BASE_URL}/nft/all`); 
    return response.data;
  } catch (error) {
    console.error("Error fetching all NFTs:", error.response ? error.response.data : error.message);
    throw error.response ? error.response.data : new Error('Network error or server issue');
  }
};
