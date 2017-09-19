import { parse as urlParse } from 'url';

import { createStore } from 'redux';

export const LOCATION_CHANGE = 'LOCATION_CHANGE';
const defaultState = {
  location: { pathname: '', query: {} },
};

export function reducer(state = defaultState, action) {
  switch (action.type) {
    case LOCATION_CHANGE:
      return { ...state, location: urlParse(action.asPath, true) };
    default:
      return state;
  }
}

export function makeStore(initialState) {
  if (false) {
    const { pathname, query } = urlParse(req.url, true);
    const state = Object.assign(
      { location: { pathname, query } },
      initialState || {},
    );
    return createStore(reducer, state);
  }
  return createStore(reducer, initialState);
}
