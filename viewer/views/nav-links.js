import PropTypes from 'prop-types';
import React from 'react';

import { Link } from '../routes';

export function ParentLink({ doc, docFRBR }) {
  if (!doc) return null;

  const query = Object.assign({}, docFRBR, { label: doc.identifier });
  return (
    <div style={{ textAlign: 'center' }}>
      <Link route="view" params={query}><a>
        ^ { doc.marker } { doc.title } ^
      </a></Link>
    </div>
  );
}
ParentLink.propTypes = {
  doc: PropTypes.shape({
    identifier: PropTypes.string.isRequired,
    marker: PropTypes.string.isRequired,
    title: PropTypes.string,
  }),
  docFRBR: PropTypes.shape({}).isRequired,
};
ParentLink.defaultProps = { doc: null };

export function PrevLink({ doc, docFRBR }) {
  if (!doc) return null;

  const query = Object.assign({}, docFRBR, { label: doc.identifier });
  return (
    <div style={{ display: 'inline-block', width: '49%' }}>
      <Link route="view" params={query}><a style={{ float: 'left' }}>
        &lt; { doc.marker } { doc.title }
      </a></Link>
    </div>
  );
}
PrevLink.propTypes = {
  doc: PropTypes.shape({
    identifier: PropTypes.string.isRequired,
    marker: PropTypes.string.isRequired,
    title: PropTypes.string,
  }),
  docFRBR: PropTypes.shape({}).isRequired,
};
PrevLink.defaultProps = { doc: null };

export function NextLink({ doc, docFRBR }) {
  if (!doc) return null;

  const query = Object.assign({}, docFRBR, { label: doc.identifier });
  return (
    <div style={{ display: 'inline-block', textAlign: 'right', width: '50%' }}>
      <Link route="view" params={query}><a>
        { doc.marker } { doc.title } &gt;
      </a></Link>
    </div>
  );
}
NextLink.propTypes = {
  doc: PropTypes.shape({
    identifier: PropTypes.string.isRequired,
    marker: PropTypes.string.isRequired,
    title: PropTypes.string,
  }),
  docFRBR: PropTypes.shape({}).isRequired,
};
NextLink.defaultProps = { doc: null };
