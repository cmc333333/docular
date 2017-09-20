const routes = require('next-routes')();

routes
  .add('eregs', '/eregs/:title/:part/@:expressionId/:author/~:section')
  .add('view', '/:docType/:docSubtype?/:workId/@:expressionId/:author?/~:label');

module.exports = routes;
