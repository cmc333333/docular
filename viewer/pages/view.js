import axios from 'axios';
import PropTypes from 'prop-types';
import React from 'react';

import { Link } from '../routes';
import { structRenderers, contentRenderers, RenderStruct }
  from '../renderers/render';
import { UnknownContent, UnknownStruct } from '../renderers/unknown';

structRenderers.default = UnknownStruct;
contentRenderers.default = UnknownContent;

const client = axios.create({ baseURL: `${process.env.API_BASE}akn/us` });

export default function View({ struct }) {
  let prev;
  let next;
  let up;
  let query;
  const nav = {
    docType: struct.meta.frbr.work.doc_type,
    workId: struct.meta.frbr.work.work_id,
    expressionId: struct.meta.frbr.expression.expression_id,
  };
  if (struct.meta.frbr.work.doc_subtype.length) {
    nav.docSubtype = struct.meta.frbr.work.doc_subtype;
  }
  if (struct.meta.frbr.expression.author.length) {
    nav.author = struct.meta.frbr.expression.author;
  }

  if (struct.meta.prev_doc) {
    query = Object.assign({}, nav, { label: struct.meta.prev_doc.identifier });
    prev = (
      <div style={{ display: 'inline-block', width: '49%' }}>
        <Link route="view" params={query}><a style={{ float: 'left' }}>
          &lt; { struct.meta.prev_doc.marker } { struct.meta.prev_doc.title }
        </a></Link>
      </div>
    );
  }
  if (struct.meta.parent_doc) {
    query = Object.assign(
      {}, nav, { label: struct.meta.parent_doc.identifier });
    up = (
      <div style={{ textAlign: 'center' }}>
        <Link route="view" params={query}><a>
          ^ { struct.meta.parent_doc.marker } { struct.meta.parent_doc.title } ^
        </a></Link>
      </div>
    );
  }
  if (struct.meta.next_doc) {
    query = Object.assign({}, nav, { label: struct.meta.next_doc.identifier });
    next = (
      <div style={{ display: 'inline-block', textAlign: 'right', width: '50%' }}>
        <Link route="view" params={query}><a>
          { struct.meta.next_doc.marker } { struct.meta.next_doc.title } &gt;
        </a></Link>
      </div>
    );
  }
  return (
    <div>
      <div style={{ border: 'solid 1px black' }}>
        { up }
        { prev } { next }
      </div>
      <RenderStruct nav={nav} struct={struct} />
    </div>);
}
View.propTypes = {
  struct: PropTypes.shape({
  }).isRequired,
};

View.getInitialProps = async ({ query }) => {
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
