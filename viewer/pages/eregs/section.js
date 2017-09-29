import withRedux from 'next-redux-wrapper';
import PropTypes from 'prop-types';
import React from 'react';

import client from '../../client';
import { makeStore, setDocFRBR } from '../../store';
import { RenderStruct } from '../../containers/render';
import * as cfr from '../../renderers/cfr';
import { UnknownInline, UnknownStruct } from '../../renderers/unknown';
import Layout from '../../views/eregs/layout';
import FooterNav from '../../views/eregs/footer-nav';

const inlineRenderers = {
  default: UnknownInline,
};
const structRenderers = {
  default: UnknownStruct,
  ...cfr,
};

export function Eregs({ cfrPart, cfrTitle, struct }) {
  return (
    <Layout cfrPart={cfrPart} cfrTitle={cfrTitle}>
      <RenderStruct {...{ inlineRenderers, struct, structRenderers }} />
      <FooterNav struct={struct} />
    </Layout>
  );
}
Eregs.propTypes = {
  cfrPart: PropTypes.string.isRequired,
  cfrTitle: PropTypes.string.isRequired,
  struct: PropTypes.shape({}).isRequired,
};

Eregs.getInitialProps = async ({ query, store }) => {
  const { title, part, expressionId, author, section } = query;
  const url = (`cfr/title_${title}/part_${part}/@${expressionId}/${author}`
               + `/~part_${part}__${section}.json`);
  const struct = await client.get(url);
  store.dispatch(setDocFRBR(struct.meta.frbr));

  return { cfrPart: part, cfrTitle: title, struct };
};

export default withRedux(makeStore)(Eregs);
