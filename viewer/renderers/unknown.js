import PropTypes from 'prop-types';
import React from 'react';
import { connect } from 'react-redux';
import hash from 'string-hash';

import { Link } from '../routes';


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


export function Marker({ docFRBR, struct }) {
  const markerQuery = Object.assign({}, docFRBR, { label: struct.identifier });
  const style = {
    display: 'inline-block',
    height: '100%',
    verticalAlign: 'top',
    width: '10%',
  };
  return (
    <div style={style}>
      <Link route="view" params={markerQuery}>
        <a>{struct.marker || '_'}</a>
      </Link>
    </div>
  );
}
Marker.propTypes = {
  docFRBR: PropTypes.shape({}).isRequired,
  struct: PropTypes.shape({
    identifier: PropTypes.string.isRequired,
    marker: PropTypes.string,
  }).isRequired,
};
const MarkerContainer = connect(({ docFRBR }) => ({ docFRBR }))(Marker);


export function UnknownStruct({ children, inline, struct }) {
  let header;
  const style = {
    backgroundColor: color({ min: 192, name: struct.tag }),
    border: `1px solid ${color({ min: 64, max: 128, name: struct.tag })}`,
    margin: '5px',
    padding: '10px',
  };
  if (struct.title) {
    const HTag = `h${struct.depth + 1}`;
    header = <HTag style={{ margin: 0 }}>{struct.title}</HTag>;
  }

  return (
    <div style={style}>
      <MarkerContainer struct={struct} />
      <div style={{ display: 'inline-block', width: '90%' }}>
        { header }
        { inline }
      </div>
      { children }
    </div>
  );
}


export function UnknownInline({ children, inline }) {
  const style = {};
  let altStr;
  if (inline.layer) {
    const layerStr = `${inline.layer.name}`;
    style.backgroundColor = color({ min: 192, name: layerStr });
    style.border = `1px solid ${color({ min: 64, max: 128, name: layerStr })}`;

    altStr = Object.entries(inline.layer).map(
      ([key, val]) => `${key}: ${val}`).join('\n');
  }
  return (
    <span style={style} title={altStr}>
      { inline.text }
      { children }
    </span>
  );
}
