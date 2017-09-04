const axios = require('axios');
const webpack = require('webpack');

const routes = require('./routes');


function exportPathMap() {
  const result = {};
  function processPage(url) {
    return axios.get(url).then((resp) => {
      resp.data.results.forEach((docStruct) => {
        const params = {
          docType: docStruct.expression.work.doc_type,
          docSubtype: docStruct.expression.work.doc_subtype,
          workId: docStruct.expression.work.work_id,
          expressionId: docStruct.expression.expression_id,
          author: docStruct.expression.author,
          label: docStruct.identifier,
        };
        const path = routes.findByName('view').getAs(params);

        result[path] = { page: '/view', query: params };
      });
      if (resp.data.next) {
        return processPage(resp.data.next);
      }
      return result;
    });
  }
  return processPage(
    `${process.env.API_BASE}/doc_struct/?fields=identifier,expression`);
}

module.exports = {
  exportPathMap,
  webpack: (config) => {
    config.plugins.push(new webpack.EnvironmentPlugin({
      NODE_ENV: 'development',
      DEBUG: true,
      API_BASE: '',
    }));
    return config;
  },
};
