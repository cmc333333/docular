import PropTypes from 'prop-types';
import React from 'react';

export const structRenderers = {};
export const contentRenderers = {};

export function RenderStruct({ nav, struct }) {
  const Renderer = structRenderers[struct.tag] || structRenderers.default;
  return <Renderer nav={nav} struct={struct} />;
}
RenderStruct.propTypes = {
  nav: PropTypes.shape({}).isRequired,
  struct: PropTypes.shape({}).isRequired,
};

export function RenderContent({ content }) {
  if (content.layer) {
    const Renderer = (contentRenderers[content.layer]
                      || contentRenderers.default);
    return <Renderer content={content} />;
  }
  return <span>{content.text}</span>;
}
RenderContent.propTypes = {
  content: PropTypes.shape({}).isRequired,
};
