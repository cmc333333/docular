import Head from 'next/head';
import { withRouter } from 'next/router';
import PropTypes from 'prop-types';
import React from 'react';

import * as styles from '../../css/eregs/layout';
import { Link } from '../../routes';


function MenuItem({ router, struct }) {
  let submenu = null;
  const { children, marker, tag, title } = struct;
  if (children.length) {
    submenu = (
      <ol>
        { children.map(c => <MenuItemContainer key={c.identifier} struct={c} />) }
      </ol>
    );
  }
  switch (tag) {
    case 'subpart':
      return <li><span>{ marker } - { title }</span>{ submenu }</li>;
    case 'subjgrp':
      return <li><span>{ title }</span>{ submenu }</li>;
    case 'sec': {
      const section = struct.identifier.split('__').slice(1).join('__');
      const params = Object.assign({}, router.query, { section });
      return (
        <li>
          <Link route="eregs-section" params={params}>
            <a>
              <span className="marker">{ marker }</span>
              <span className="title">{ title }</span>
            </a>
          </Link>
        </li>
      );
    }
    default:
      return null;
  }
}
MenuItem.propTypes = {
  router: PropTypes.shape({
    query: PropTypes.shape({}).isRequired,
  }).isRequired,
  struct: PropTypes.shape({
    children: PropTypes.arrayOf(PropTypes.shape({
      identifier: PropTypes.string.isRequired,
    })).isRequired,
    identifier: PropTypes.string.isRequired,
    marker: PropTypes.string,
    tag: PropTypes.string.isRequired,
    title: PropTypes.string,
  }).isRequired,
};

const MenuItemContainer = withRouter(MenuItem);


export default function Layout({ cfrPart, cfrTitle, children, toc }) {
  return (
    <div>
      <Head>
        <link rel="stylesheet" href="/static/css/normalize.css" />
      </Head>
      <header>
        <h1>eRegulations | {cfrTitle} CFR {cfrPart}</h1>
        { styles.banner }
      </header>
      <nav>
        <ol>
          { toc.children.map(c => <MenuItemContainer key={c.identifier} struct={c} />) }
        </ol>
        { styles.tocMenu }
      </nav>
      { children }
    </div>
  );
}
Layout.propTypes = {
  cfrPart: PropTypes.string.isRequired,
  cfrTitle: PropTypes.string.isRequired,
  children: PropTypes.node.isRequired,
  toc: PropTypes.shape({
    children: PropTypes.arrayOf(PropTypes.shape({
      identifier: PropTypes.string.isRequired,
    })).isRequired,
  }).isRequired,
};
