const routes = require('next-routes')();

routes
  .add('view', '/:docType/:docSubtype?/:workId/@:expressionId/:author?/~:label');

module.exports = routes;
