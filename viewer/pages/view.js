import axios from 'axios';
import PropTypes from 'prop-types';
import React from 'react';
import hash from 'string-hash';

import { Link } from '../routes';

const client = axios.create({ baseURL: `${process.env.API_BASE}akn/us` });

function color({ min, max, name }) {
  const nameHash = hash(name);
  const span = ((max || 255) - (min || 0)) / 255;
  const project = val => ((min || 0) + (val * span)).toFixed(0);
  /* eslint-disable  no-bitwise */
  const red = project(nameHash & 255);
  const blue = project((nameHash >> 8) & 255);
  const green = project((nameHash >> 16) & 255);
  /* eslint-enable  no-bitwise */

  return `rgb(${red}, ${blue}, ${green})`;
}

function Content({ content }) {
  const style = {};
  if (content.layer_id) {
    const layerStr = `${content.layer_id}`;
    style.backgroundColor = color({ min: 192, name: layerStr });
    style.border = `1px solid ${color({ min: 64, max: 128, name: layerStr })}`;
  }
  return (
    <span style={style}>
      { content.text }
      { content.children.map(c => <Content content={c} />) }
    </span>
  );
}
Content.propTypes = {
  content: PropTypes.shape({
    layer_id: PropTypes.number,
    text: PropTypes.string.isRequired,
    children: PropTypes.arrayOf(PropTypes.shape({})).isRequired,
  }).isRequired,
};


function Struct({ nav, struct }) {
  let header;
  const style = {
    backgroundColor: color({ min: 192, name: struct.tag }),
    border: `1px solid ${color({ min: 64, max: 128, name: struct.tag })}`,
    margin: '5px',
    padding: '10px',
  };
  const markerStyle = {
    display: 'inline-block',
    height: '100%',
    verticalAlign: 'top',
    width: '10%',
  };
  const markerQuery = Object.assign({}, nav, { label: struct.identifier });
  if (struct.title) {
    const HTag = `h${struct.depth + 1}`;
    header = <HTag style={{ margin: 0 }}>{struct.title}</HTag>;
  }


  return (
    <div style={style}>
      <div style={markerStyle}>
        <Link route="view" params={markerQuery}>
          <a>{struct.marker || '_'}</a>
        </Link>
      </div>
      <div style={{ display: 'inline-block', width: '90%' }}>
        { header }
        { struct.content.map(c => <Content content={c} />) }
      </div>
      { struct.children.map(c =>
        <Struct key={c.identifier} nav={nav} struct={c} />) }
    </div>
  );
}
Struct.propTypes = {
  nav: PropTypes.shape({
  }).isRequired,
  struct: PropTypes.shape({
  }).isRequired,
};

export default function View({ struct }) {
  let prev;
  let next;
  let up;
  let query;
  const nav = {
    docType: struct.meta.frbr.work.doc_type,
    docSubtype: struct.meta.frbr.work.doc_subtype,
    workId: struct.meta.frbr.work.work_id,
    expressionId: struct.meta.frbr.expression.expression_id,
    author: struct.meta.frbr.expression.author,
  };
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
      <Struct nav={nav} struct={struct} />
    </div>);
}
View.propTypes = {
  struct: PropTypes.shape({
  }).isRequired,
};

View.getInitialProps = async ({ query }) => {
  const { docType, docSubtype, workId, expressionId, author, label } = query;
  const url = (`${docType}/${docSubtype}/${workId}/@${expressionId}`
               + `/${author}/~${label}.json`);
  const { data } = await client.get(url);

  return { struct: data };
};
