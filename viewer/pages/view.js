import axios from 'axios';
import withRedux from 'next-redux-wrapper';
import PropTypes from 'prop-types';
import React from 'react';

import { makeStore, LOCATION_CHANGE } from '../store';
import { structRenderers, contentRenderers, RenderStruct }
  from '../renderers/render';
import { UnknownContent, UnknownStruct } from '../renderers/unknown';
import { NextLink, ParentLink, PrevLink } from '../views/nav-links';

structRenderers.default = UnknownStruct;
contentRenderers.default = UnknownContent;

const client = axios.create({ baseURL: `${process.env.API_BASE}akn/us` });

function buildNav(frbr) {
  const nav = {
    docType: frbr.work.doc_type,
    workId: frbr.work.work_id,
    expressionId: frbr.expression.expression_id,
  };
  if (frbr.work.doc_subtype.length) {
    nav.docSubtype = frbr.work.doc_subtype;
  }
  if (frbr.expression.author.length) {
    nav.author = frbr.expression.author;
  }
  return nav;
}

export function UnwrappedView({ struct }) {
  const nav = buildNav(struct.meta.frbr);

  return (
    <div>
      <div style={{ border: 'solid 1px black' }}>
        <ParentLink doc={struct.meta.parent_doc} nav={nav} />
        <PrevLink doc={struct.meta.prev_doc} nav={nav} />
        <NextLink doc={struct.meta.next_doc} nav={nav} />
      </div>
      <RenderStruct nav={nav} struct={struct} />
    </div>);
}
UnwrappedView.propTypes = {
  struct: PropTypes.shape({
  }).isRequired,
};

UnwrappedView.getInitialProps = async ({ asPath, query, store }) => {
  store.dispatch({ type: LOCATION_CHANGE, asPath });
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

  return { struct: data };
};

export default withRedux(makeStore)(UnwrappedView);
