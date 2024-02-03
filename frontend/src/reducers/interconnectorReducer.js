const initalState = {
  loading: false,
  data: {
    labels: [],
    datasets: [{
      label: "Default",
      data: [],
      borderColor: 'rgba(238,175,0, 0.5)',
      pointBorderColor: 'rgba(238,175,0, 0.7)',
      fill: false
    }]
  }
};

const interconnectorReducer = (state = initalState, action) => {
  const { type, payload } = action;

  switch (type) {
    case "AWAITING_interconnector":
      return {
        ...state,
        loading: true
      }
    case "REJECTED_interconnector":
      return {
        ...state,
        loading: false,
      }
    case "SUCCESS_interconnector":
      return {
        ...state,
        loading: false,
        data: {
          labels: payload.labels,
          datasets: [{
            label: "France",
            data: payload.franceData,
            borderColor: 'rgba(238,175,0, 0.5)',
            pointBorderColor: 'rgba(238,175,0, 0.7)',
            fill: false
          },
          {
            label: "Belgium",
            data: payload.belgiumData,
            borderColor: 'rgba(255,23,23, 0.8)',
            pointBorderColor: 'rgba(255,23,23, 0.8)',
            fill: false
          },
          {
            label: "Netherlands",
            data: payload.netherlandsData,
            borderColor: 'rgba(17,23,255, 0.8)',
            pointBorderColor: 'rgba(17,23,255, 0.8)',
            fill: false
          },
          {
            label: "Norway",
            data: payload.norwayData,
            borderColor: 'rgba(17,255,0, 0.8)',
            pointBorderColor: 'rgba(17,255,0, 0.8)',
            fill: false
          }]
        }
      }
    default:
      return state;
  }
}

export default interconnectorReducer;
