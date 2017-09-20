import PropTypes from 'prop-types';
import React from 'react';


export function sec({ children, struct }) {
  return (
    <div>
      <h3>{ struct.marker } { struct.title }</h3>
      { children }
    </div>
  );
}
sec.propTypes = {
  children: PropTypes.arrayOf(PropTypes.element).isRequired,
  struct: PropTypes.shape({
    marker: PropTypes.string.isRequired,
    title: PropTypes.string.isRequired,
  }).isRequired,
};

export function par({ children, inline }) {
  return (
    <div>
      <p>{ inline }</p>
      { children }
    </div>
  );
}
par.propTypes = {
  children: PropTypes.arrayOf(PropTypes.element).isRequired,
  inline: PropTypes.arrayOf(PropTypes.element).isRequired,
};
export const defpar = par;

export function lvl1({ children, inline, struct }) {
  const markerStyle = {
    display: 'inline-block',
    height: '100%',
    verticalAlign: 'top',
    width: '10%',
  };
  return (
    <div style={{ padding: '10px' }}>
      <div style={markerStyle}>{struct.marker}</div>
      <div style={{ display: 'inline-block', width: '90%' }}>{ inline }</div>
      { children }
    </div>
  );
}
lvl1.propTypes = {
  children: PropTypes.arrayOf(PropTypes.element).isRequired,
  inline: PropTypes.arrayOf(PropTypes.element).isRequired,
  struct: PropTypes.shape({
    marker: PropTypes.string.isRequired,
  }).isRequired,
};
export const lvl2 = lvl1;
export const lvl3 = lvl1;
export const lvl4 = lvl1;
export const lvl5 = lvl1;
export const lvl6 = lvl1;
