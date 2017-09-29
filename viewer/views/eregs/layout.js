import Head from 'next/head';
import PropTypes from 'prop-types';
import React from 'react';

import * as styles from '../../css/eregs/layout';


export default function Layout({ cfrPart, cfrTitle, children }) {
  return (
    <div>
      <Head>
        <link rel="stylesheet" href="/static/css/normalize.css" />
      </Head>
      <header>
        <h1>eRegulations | {cfrTitle} CFR {cfrPart}</h1>
        { styles.banner }
      </header>
      { children }
    </div>
  );
}
Layout.propTypes = {
  cfrPart: PropTypes.string.isRequired,
  cfrTitle: PropTypes.string.isRequired,
  children: PropTypes.node.isRequired,
};
