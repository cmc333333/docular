const routes = require('next-routes')();

routes
  .add('eregs-section', '/eregs/:title/:part/@:expressionId/:author/~:section',
       'eregs/section')
  .add('view', '/:docType/:docSubtype?/:workId/@:expressionId/:author?/~:label');

module.exports = routes;
