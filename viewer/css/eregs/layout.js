import React from 'react';

import * as uswds from '../uswds';


const bannerHeight = '50px';

export const banner = (
  <style>{`
  header {
    background-color: ${uswds.colorPrimaryDarkest};
    color: ${uswds.colorWhite};
    height: ${bannerHeight};
  }

  h1 {
    margin: 0 20px;
    line-height: ${bannerHeight};
  }
  `}</style>
);

export const tocMenu = (
  <style>{`
  nav {
    width: 200px;
    display: inline-block;
    border-bottom: 1px solid black;
    border-right: 1px solid black;
  }
  ol {
    margin: 0;
    padding: 0;
  }
  li {
    border-top: 1px solid black;
  }
  .marker {
    display: block;
  }
  .title {
    font-size: 18px;
  }
  `}</style>
);
