const express = require('express');
const next = require('next');

const app = next({ dev: process.env.NODE_ENV !== 'production' });
const handle = app.getRequestHandler();

app.prepare().then(() => {
  const server = express();

  server.get('*', handle);

  server.listen(8000);
}).catch((ex) => {
  console.error(ex.stack);
  process.exit(1);
});
