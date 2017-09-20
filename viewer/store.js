import { parse as urlParse } from 'url';

import { createStore } from 'redux';

const CHANGE_LOCATION = 'CHANGE_LOCATION';
export function changeLocation(asPath) {
  return { type: CHANGE_LOCATION, location: urlParse(asPath, true) };
}

const SET_DOC_FRBR = 'SET_DOC_FRBR';
export function setDocFRBR(metaFRBR) {
  const docFRBR = {
    docType: metaFRBR.work.doc_type,
    workId: metaFRBR.work.work_id,
    expressionId: metaFRBR.expression.expression_id,
  };
  if (metaFRBR.work.doc_subtype.length) {
    docFRBR.docSubtype = metaFRBR.work.doc_subtype;
  }
  if (metaFRBR.expression.author.length) {
    docFRBR.author = metaFRBR.expression.author;
  }
  return { type: SET_DOC_FRBR, docFRBR };
}

const defaultState = {
  docFRBR: { docType: '', workId: '', expressionId: '' },
  location: { pathname: '', query: {} },
};

export function reducer(state = defaultState, action) {
  switch (action.type) {
    case CHANGE_LOCATION:
    case SET_DOC_FRBR: {
      const actionCopy = { ...action };
      delete actionCopy.type;
      return { ...state, ...actionCopy };
    }
    default:
      return state;
  }
}

export function makeStore(initialState) {
  return createStore(reducer, initialState);
}
