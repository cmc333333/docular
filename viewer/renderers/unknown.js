import React from 'react';
import hash from 'string-hash';

import { Link } from '../routes';
import { RenderStruct, RenderContent } from './render';


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


export function UnknownStruct({ nav, struct }) {
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
        { struct.content.map((c, idx) =>
          /* eslint-disable react/no-array-index-key */
          <RenderContent content={c} key={idx} />)
          /* eslint-enable react/no-array-index-key */
        }
      </div>
      { struct.children.map(c =>
        <RenderStruct key={c.identifier} nav={nav} struct={c} />) }
    </div>
  );
}
UnknownStruct.propTypes = RenderStruct.propTypes;


export function UnknownContent({ content }) {
  const style = {};
  let altStr;
  if (content.layer) {
    const layerStr = `${content.layer.name}`;
    style.backgroundColor = color({ min: 192, name: layerStr });
    style.border = `1px solid ${color({ min: 64, max: 128, name: layerStr })}`;

    altStr = Object.entries(content.layer).map(
      ([key, val]) => `${key}: ${val}`).join('\n');
  }
  return (
    <span style={style} title={altStr}>
      { content.text }
      { content.children.map(c => <RenderContent content={c} />) }
    </span>
  );
}
UnknownContent.propTypes = RenderContent.propTypes;
