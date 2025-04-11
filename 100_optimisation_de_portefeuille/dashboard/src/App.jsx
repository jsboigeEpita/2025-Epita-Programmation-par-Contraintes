import React, { useEffect, useState } from "react";
import { Pie, Line } from "react-chartjs-2";
import { Chart as ChartJS, ArcElement, Tooltip, Legend, CategoryScale, LinearScale, PointElement, LineElement } from "chart.js";
import ClipLoader from "react-spinners/ClipLoader";
import './App.css'

ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, PointElement, LineElement);

const Dashboard = () => {
  const [data, setData] = useState([]);
  const [tickers, setTickers] = useState([])
  const [sent, setSent] = useState(false)
  const [method, setMethod] = useState("")
  const [tickerName, setTickerName] = useState("")

  const [budget, setBudget] = useState(50);
  const [maxAssets, setMaxAssets] = useState(1);
  const [maxVolatility, setMaxVolatility] = useState(20);
  const [minReturn, setMinReturn] = useState(0);
  const [maxAllocation, setMaxAllocation] = useState(50);
  const [minSharpeRatio, setMinSharpeRatio] = useState(0);

  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if(data.length)
      setSent(true)
  }, [data]);

  const pieData = {
    labels: data.map((item) => item.name),
    datasets: [
      {
        data: data.map((item) => item.percentage * 100),
        backgroundColor: ["#FF6384", "#36A2EB", "#FFCE56", "#4CAF50", "#9966FF"],
      },
    ],
  };

  const inputHandler = (e) => {
    if (e.key != "Enter")
      return;

    setTickers([...tickers, e.target.value])
    setTickerName("")
    e.target.value = ""
  }

  function handleClickCompute() {
    setIsLoading(true);
    if (method === "MaxSharpeRatio") {
      fetch(`http://localhost:5000/?tickers=${tickers.join(",")}`)
        .then((res) => res.json())
        .then((data) => setData(data))
        .finally(() => setIsLoading(false));
    } else if (method === "Quadratic") {
      const max_volatility = maxVolatility / 100;
      console.log("calling quad with max vol", max_volatility)
      fetch(`http://localhost:5000/quad?tickers=${tickers.join(",")}&volatility=${max_volatility}`)
        .then((res) => res.json())
        .then((data) => setData(data))
        .finally(() => setIsLoading(false));

    } else if (["ACO", "PSO", "Annealing"].includes(method)) {
      const constraints = {
        budget: budget / 100,
        max_assets: maxAssets,
        max_volatility: maxVolatility / 100,
        min_yield: minReturn,
        max_alloc_asset: maxAllocation / 100,
        min_sharpe_ratio: minSharpeRatio
      };
  
      const backendMethod = method === "Annealing" ? "SA" : method;
  
      fetch(`http://localhost:5000/gen?tickers=${tickers.join(",")}&method=${backendMethod}&constraints=${encodeURIComponent(JSON.stringify(constraints))}`)
        .then((res) => res.json())
        .then((data) =>{
          console.log(data)
          setData(data)
        })
        .finally(() => setIsLoading(false));
    }
  }

  if (isLoading) {
    return (
      <div>
        <h1>Running optimization, please wait...</h1>
        <ClipLoader color="#36d7b7" size={60} />
      </div>
    )
  }

  return sent ? (
    <div className="flex h-screen">
      <div class="result-header">
        {/* Left Panel - Pie Chart */}
        <h1 className="text-lg font-bold mb-4">Portfolio Distribution</h1>
        <div class="result-chart">
          <Pie data={pieData} />
        </div>
        <div class="result-summary">
          Expected annual returns: {(100 * data.reduce((acc, item) => acc + item.returns * item.percentage, 0)).toFixed(2)}%
        </div>
      </div>

      {/* Right Panel - Line Charts */}
      <div className="w-2/3 ml-1/3 p-4 overflow-y-auto h-full">
        {data.map((item) => (
          <div key={item.name} className="mb-6">
            <h3 className="text-md font-semibold mb-2">{item.name}</h3>
            <Line
              data={{
                labels: ["Day 1", "Day 2", "Day 3", "Day 4", "Day 5"],
                datasets: [
                  {
                    label: item.name,
                    data: item.data,
                    borderColor: "#36A2EB",
                    backgroundColor: "rgba(54, 162, 235, 0.2)",
                  },
                ],
              }}
            />
          </div>
        ))}
      </div>
    </div>
  ) : (
      <>
        <div>
          <div class="main-title">
            <h1>Portfolio Optimization Algorithm Tester</h1>
          </div>

          <div class="opti-div">
            <h2 class="opti-title">Optimization Method</h2>
            <select
              value={method}
              onChange={(e) => setMethod(e.target.value)}
              class="opti-select"
            >
              <option value="">Select Optimization Method</option>
              <option value="Quadratic">Quadratic</option>
              <option value="MaxSharpeRatio">MaxSharpeRatio</option>
              <option value="ACO">ACO</option>
              <option value="PSO">PSO</option>
              <option value="Annealing">Annealing</option>
            </select>
          </div>
          {method === "Quadratic" && (
            <div>
              <h2>Quadratic Optimisation Constraints</h2>
              <div className="constraint-item">
                <label>Given Portfolio Volatility: {maxVolatility}%</label>
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={maxVolatility}
                  onChange={(e) => setMaxVolatility(Number(e.target.value))}
                />
              </div>
            </div>
          )}


          {["PSO", "ACO", "Annealing"].includes(method) && (
            <div className="constraints-div">
              <h2>Portfolio Constraints</h2>

              <div className="constraint-item">
                <label>Budget Allocation: {budget}%</label>
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={budget}
                  onChange={(e) => setBudget(Number(e.target.value))}
                />
              </div>

              <div className="constraint-item">
                <label>Max Number of Assets: {maxAssets}</label>
                <input
                  type="range"
                  min="0"
                  max={tickers.length}
                  value={maxAssets}
                  onChange={(e) => setMaxAssets(Number(e.target.value))}
                />
              </div>

              <div className="constraint-item">
                <label>Max Portfolio Volatility: {maxVolatility}%</label>
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={maxVolatility}
                  onChange={(e) => setMaxVolatility(Number(e.target.value))}
                />
              </div>

              <div className="constraint-item">
                <label>Min Portfolio Return:</label>
                <input
                  type="number"
                  step="0.01"
                  value={minReturn}
                  onChange={(e) => setMinReturn(Number(e.target.value))}
                />
              </div>

              <div className="constraint-item">
                <label>Max Allocation per Asset: {maxAllocation}%</label>
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={maxAllocation}
                  onChange={(e) => setMaxAllocation(Number(e.target.value))}
                />
              </div>

              <div className="constraint-item">
                <label>Min Sharpe Ratio:</label>
                <input
                  type="number"
                  step="0.01"
                  value={minSharpeRatio}
                  onChange={(e) => setMinSharpeRatio(Number(e.target.value))}
                />
              </div>
            </div>
          )}


          <div class="tickers-div">
            <h2 class="tickers-title">Tickers</h2>
            <p class="tickers-desc">Enter Tickers or ISINs that can be picked by the algorithm for your portfolio.</p>
            <input type="text"
              value={tickerName}
              onChange={(e) => setTickerName(e.target.value)} onKeyDown={(e) => inputHandler(e)}
              placeholder="Enter new Ticker or ISIN..."
              class="tickers-input"/>
            <button class="tickers-add" onClick={() => {
              setTickers([...tickers, tickerName])
              setTickerName("")
            }}>Add Ticker</button>
          </div>

          <div>
            <div class="tickers-list">
              {tickers.map(e => (<div class="ticker-item" key={e}>{e}</div>))}
            </div>

            <button class="compute-button" onClick={() => {
              handleClickCompute();
            }}>Compute</button>
          </div>
        </div>
      </>
  )
};

export default Dashboard;