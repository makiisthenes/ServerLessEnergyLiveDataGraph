import { combineReducers } from "redux";
import interconnectorReducer from "./interconnectorReducer";

const rootReducer = combineReducers({
  interconnector: interconnectorReducer
})

export default rootReducer;