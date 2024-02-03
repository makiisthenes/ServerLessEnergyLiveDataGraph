import React, { useEffect } from 'react';
import './App.css';
import { Line } from 'react-chartjs-2';
import { useDispatch, useSelector } from "react-redux";
import { getData } from "./actions/interconnectorActions";

function App() {
  const dispatch = useDispatch();
  const state = useSelector(state => state.interconnector);
  const [apiLink, setApiLink] = React.useState('https://zpf175xw2f.execute-api.eu-north-1.amazonaws.com/Learning');

  // Function to dispatch the action to fetch data
  const fetchData = () => {
    dispatch(getData({
      apiLinkUser: apiLink
    }));
  };

  // useEffect hook to start fetching data automatically
  useEffect(() => {
    const intervalId = setInterval(() => {
      fetchData();
    }, 10000);  // after 15 seconds.

    // Cleanup function to clear the interval when the component unmounts
    return () => clearInterval(intervalId);
  }, [apiLink]); // Depend on apiLink to restart the interval if the API link changes

  return (
    <div className="App">
      <h1>Interconnector Serverless Sample Workshop</h1>
      <p>By Michael Peres</p>
      <div className={"btns-wrapper"}>
        {state.loading && <p>Updating...</p>}
      </div>
      <div className={"chart-wrapper"}>
        <Line
          data={state.data}
        />
      </div>
    </div>
  );
}

export default App;

