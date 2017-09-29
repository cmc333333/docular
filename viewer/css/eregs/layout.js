import * as uswds from '../uswds';

const bannerHeight = '50px';

export const banner = <style jsx>{`
  header {
    background-color: ${uswds.colorPrimaryDarkest};
    color: ${uswds.colorWhite};
    height: ${bannerHeight};
  }

  h1 {
    margin: 0 20px;
    line-height: ${bannerHeight};
  }
`}</style>;
