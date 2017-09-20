import withRedux from 'next-redux-wrapper';
import PropTypes from 'prop-types';
import React from 'react';
import { connect } from 'react-redux';

import client from '../client';
import { changeLocation, makeStore, setDocFRBR } from '../store';
import { RenderStruct } from '../containers/render';
import { UnknownInline, UnknownStruct } from '../renderers/unknown';
import { NextLink, ParentLink, PrevLink } from '../views/nav-links';

const withFRBR = connect(({ docFRBR }) => ({ docFRBR }));
const NextLinkContainer = withFRBR(NextLink);
const ParentLinkContainer = withFRBR(ParentLink);
const PrevLinkContainer = withFRBR(PrevLink);

const inlineRenderers = {
  default: UnknownInline,
};
const structRenderers = {
  default: UnknownStruct,
};

export function View({ struct }) {
  return (
    <div>
      <div style={{ border: 'solid 1px black' }}>
        <ParentLinkContainer doc={struct.meta.parent_doc} />
        <PrevLinkContainer doc={struct.meta.prev_doc} />
        <NextLinkContainer doc={struct.meta.next_doc} />
      </div>
      <RenderStruct {...{ inlineRenderers, struct, structRenderers }} />
    </div>);
}
View.propTypes = {
  struct: PropTypes.shape({
    meta: PropTypes.shape({
      next_doc: PropTypes.object,
      parent_doc: PropTypes.object,
      prev_doc: PropTypes.object,
    }).isRequired,
  }).isRequired,
};
View.getInitialProps = async ({ asPath, query, store }) => {
  store.dispatch(changeLocation(asPath));
  const { docType, docSubtype, workId, expressionId, author, label } = query;
  let url = docType;
  if (docSubtype) {
    url += `/${docSubtype}`;
  }
  url += `/${workId}/@${expressionId}`;
  if (author) {
    url += `/${author}`;
  }
  url += `/~${label}.json`;
  const { data } = await client.get(url);
  store.dispatch(setDocFRBR(data.meta.frbr));

  return { struct: data };
};

export default withRedux(makeStore)(View);
