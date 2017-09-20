import withRedux from 'next-redux-wrapper';
import PropTypes from 'prop-types';
import React from 'react';

import client from '../client';
import { changeLocation, makeStore, setDocFRBR } from '../store';
import { RenderStruct } from '../containers/render';
import * as cfr from '../renderers/cfr';
import { UnknownInline, UnknownStruct } from '../renderers/unknown';

const inlineRenderers = {
  default: UnknownInline,
};
const structRenderers = {
  default: UnknownStruct,
  ...cfr,
};

export function Eregs({ struct }) {
  return (
    <div>
      <RenderStruct {...{ inlineRenderers, struct, structRenderers }} />
    </div>
  );
}
Eregs.propTypes = {
  struct: PropTypes.shape({}).isRequired,
};

Eregs.getInitialProps = async ({ asPath, query, store }) => {
  store.dispatch(changeLocation(asPath));
  const { title, part, expressionId, author, section } = query;
  const url = (`cfr/title_${title}/part_${part}/@${expressionId}/${author}`
               + `/~part_${part}__${section}.json`);
  const { data } = await client.get(url);
  store.dispatch(setDocFRBR(data.meta.frbr));

  return { struct: data };
};

export default withRedux(makeStore)(Eregs);
