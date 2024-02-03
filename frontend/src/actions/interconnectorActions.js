import axios from "axios";
import moment from "moment";

export const getData = ({ apiLinkUser }) => async dispatch => {
  try {
    dispatch({
      type: "AWAITING_interconnector"
    })

    const response = await axios.get(apiLinkUser)
    const labels = [];
    const franceData = [];
    const belgiumData = [];
    const netherlandsData = [];
    const norwayData = [];
    for (let i = 0; i < response.data.body.Responses["electric_data"].length; i++) {
      franceData.push(response.data.body.Responses["electric_data"][i].France)
      belgiumData.push(response.data.body.Responses["electric_data"][i].Belgium)
      netherlandsData.push(response.data.body.Responses["electric_data"][i].Netherlands)
      norwayData.push(response.data.body.Responses["electric_data"][i].Norway)
      labels.push(moment(response.data.body.Responses["electric_data"][i].datetime * 1000).format("LT"))

    }

    dispatch({
      type: "SUCCESS_interconnector",
      payload: {
        franceData,
        belgiumData,
        netherlandsData,
        norwayData,
        labels
      }
    })
  } catch (e) {
    dispatch({
      type: "REJECTED_interconnector",
    })
  }
}
