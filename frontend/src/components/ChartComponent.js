import React, { useState, useEffect, useRef } from 'react'; // Added useEffect, useRef
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import annotationPlugin from 'chartjs-plugin-annotation';
import { getMockPriceData } from '../services/priceData';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  annotationPlugin
);

const ChartComponent = ({ latestNft }) => { // Receive latestNft as prop
  const initialMockData = getMockPriceData();
  const [chartData, setChartData] = useState({
    labels: [...initialMockData.labels],
    datasets: [
      {
        ...initialMockData.datasets[0], // Assuming getMockPriceData returns datasets array
        data: [...initialMockData.datasets[0].data],
        yAxisID: 'yBtc',
      },
      {
        ...initialMockData.datasets[1],
        data: [...initialMockData.datasets[1].data],
        yAxisID: 'ySol',
      },
    ],
  });
  const [annotations, setAnnotations] = useState([]);
  const chartRef = useRef(null); // To access chart instance for updates

  useEffect(() => {
    if (latestNft && chartRef.current) {
      const { nft_type, creation_timestamp, minting_price_btc, minting_price_sol } = latestNft;
      
      const newLabel = new Date(creation_timestamp).toLocaleTimeString();
      
      // Update chart data
      const newChartData = {
        labels: [...chartData.labels, newLabel],
        datasets: [
          { ...chartData.datasets[0], data: [...chartData.datasets[0].data, minting_price_btc] },
          { ...chartData.datasets[1], data: [...chartData.datasets[1].data, minting_price_sol] },
        ],
      };
      setChartData(newChartData);

      // Prepare annotation
      let newAnnotation = {};
      if (nft_type === 'long') { // Green arrow for SOL
        newAnnotation = {
          type: 'line',
          scaleID: 'ySol',
          value: minting_price_sol,
          endValue: minting_price_sol - (chartData.datasets[1].data.reduce((a,b)=>Math.max(a,b),0) * 0.1), // Adjusted for dynamic scale
          borderColor: 'green',
          borderWidth: 3,
          xMin: newLabel,
          xMax: newLabel,
          arrowHeads: { end: { display: true, borderColor: 'green', fill: true, backgroundColor: 'green', length: 12, width: 8 }},
          label: { content: 'Long SOL', enabled: true, position: 'start', yAdjust: -10, backgroundColor: 'rgba(0,255,0,0.1)'}
        };
      } else if (nft_type === 'short') { // Red arrow for BTC
        newAnnotation = {
          type: 'line',
          scaleID: 'yBtc',
          value: minting_price_btc,
          endValue: minting_price_btc + (chartData.datasets[0].data.reduce((a,b)=>Math.max(a,b),0) * 0.05), // Adjusted for dynamic scale
          borderColor: 'red',
          borderWidth: 3,
          xMin: newLabel,
          xMax: newLabel,
          arrowHeads: { end: { display: true, borderColor: 'red', fill: true, backgroundColor: 'red', length: 12, width: 8 }},
          label: { content: 'Short BTC', enabled: true, position: 'start', yAdjust: 10, backgroundColor: 'rgba(255,0,0,0.1)'}
        };
      }
      
      setAnnotations(prev => [...prev, newAnnotation]);
      
      // No need to call chartRef.current.update() explicitly for data and annotations state changes if using react-chartjs-2 correctly.
      // The component should re-render with new data and annotations.
    }
  }, [latestNft]); // Effect runs when latestNft changes

  // Modify getMockPriceData to return datasets in a way that's easy to spread
  // This is a local adaptation for the ChartComponent. Ideally, getMockPriceData service would be more flexible.
  const adaptedMockData = getMockPriceData();
  const initialDataForChart = {
    labels: adaptedMockData.labels,
    datasets: [
      {
        label: 'BTC/USD',
        data: adaptedMockData.btcPrices, // Use btcPrices directly
        borderColor: 'rgb(255, 99, 132)',
        backgroundColor: 'rgba(255, 99, 132, 0.5)',
        tension: 0.1,
        yAxisID: 'yBtc',
      },
      {
        label: 'SOL/USD',
        data: adaptedMockData.solPrices, // Use solPrices directly
        borderColor: 'rgb(54, 162, 235)',
        backgroundColor: 'rgba(54, 162, 235, 0.5)',
        tension: 0.1,
        yAxisID: 'ySol',
      },
    ],
  };
  
  // Initialize chartData state with this adapted structure if not already done
  // This useEffect is to ensure chartData is initialized correctly ONCE.
  useEffect(() => {
    setChartData(initialDataForChart);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // Empty dependency array means this runs once on mount


  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { position: 'top' },
      title: { display: true, text: 'Crypto Price Chart with Mint Events' },
      annotation: { annotations: annotations } // Use dynamic annotations state
    },
    scales: {
      yBtc: { type: 'linear', display: true, position: 'left', title: { display: true, text: 'BTC Price (USD)'}, grid: { drawOnChartArea: false }},
      ySol: { type: 'linear', display: true, position: 'right', title: { display: true, text: 'SOL Price (USD)'}, ticks: { callback: value => '$' + value }},
      x: { title: { display: true, text: 'Time/Events' }}
    },
    animation: {
        duration: 0 // Disable animations to prevent issues with dynamic data updates
    }
  };
  
  // Buttons to manually add arrows (from previous task, can be removed or kept for testing)
  const addSolBuyArrow = () => { /* ... from previous implementation or remove ... */ };
  const addBtcSellArrow = () => { /* ... from previous implementation or remove ... */ };
  const clearAnnotationsAndData = () => {
    setAnnotations([]);
    // Reset chartData to initial mock data if needed, or handle reset appropriately
    setChartData(initialDataForChart); 
  };

  return (
    <div>
      {/* <button onClick={addSolBuyArrow}>Add SOL Buy (Manual)</button> */}
      {/* <button onClick={addBtcSellArrow}>Add BTC Sell (Manual)</button> */}
      <button onClick={clearAnnotationsAndData} style={{margin: '5px', padding: '10px', cursor: 'pointer'}}>Reset Chart & Signals</button>
      <div style={{marginTop: '20px', height: '500px'}}>
        <Line ref={chartRef} options={options} data={chartData} />
      </div>
    </div>
  );
};

export default ChartComponent;
