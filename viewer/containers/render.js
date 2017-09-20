import PropTypes from 'prop-types';
import React from 'react';

export function RenderInline({ inline, inlineRenderers }) {
  const Renderer = inlineRenderers.default;

  return (
    <Renderer inline={inline}>
      { inline.children.map((c, idx) =>
        /* eslint-disable react/no-array-index-key */
        <RenderInline inline={c} inlineRenderers={inlineRenderers} key={idx} />)
        /* eslint-enable react/no-array-index-key */
      }
    </Renderer>
  );
}
RenderInline.propTypes = {
  inline: PropTypes.shape({
    children: PropTypes.arrayOf(PropTypes.shape({})).isRequired,
  }).isRequired,
  inlineRenderers: PropTypes.shape({
    default: PropTypes.func.isRequired,
  }).isRequired,
};

export function RenderStruct({ inlineRenderers, struct, structRenderers }) {
  const Renderer = structRenderers[struct.tag] || structRenderers.default;
  const inline = struct.content.map((child, idx) =>
    /* eslint-disable react/no-array-index-key */
    <RenderInline inline={child} inlineRenderers={inlineRenderers} key={idx} />);
    /* eslint-enable react/no-array-index-key */

  return (
    <Renderer inline={inline} struct={struct}>
      { struct.children.map(c => (
        <RenderStruct
          inlineRenderers={inlineRenderers}
          key={c.identifier}
          struct={c}
          structRenderers={structRenderers}
        />)) }
    </Renderer>
  );
}
RenderStruct.propTypes = {
  inlineRenderers: PropTypes.shape({}).isRequired,
  struct: PropTypes.shape({
    tag: PropTypes.string.isRequired,
  }).isRequired,
  structRenderers: PropTypes.shape({
    default: PropTypes.func.isRequired,
  }).isRequired,
};
