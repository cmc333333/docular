import { stringify } from 'querystring';

import axios from 'axios';
import LRU from 'lru-cache';

class Client {
  constructor(baseURL) {
    this.httpClient = axios.create({ baseURL });
    this.cache = LRU({
      max: 50,
      maxAge: 1000 * 60 * 5, // 5 minutes
    });
  }

  async get(url, params) {
    const cacheKey = `${url}?${stringify(params || {})}`;
    if (this.cache.has(cacheKey)) {
      return this.cache.get(cacheKey);
    }

    const { data } = await this.httpClient.get(url, { params });
    this.cache.set(cacheKey, data);
    return data;
  }
}

export default new Client(`${process.env.API_BASE}akn/us`);
