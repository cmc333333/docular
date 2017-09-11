const routes = require('next-routes')();

routes
  .add('view', '/:docType/:docSubtype?/:workId/@:expressionId/:author?/~:label')
  .add('about');

module.exports = routes;
