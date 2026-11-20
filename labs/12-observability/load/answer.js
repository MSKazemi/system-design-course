// Lab L12 load: a constant *arrival rate* (open model), so slowdowns do not reduce offered load.
import http from 'k6/http';

const RATE = parseInt(__ENV.RATE || '20');        // requests per second
const USERS = parseInt(__ENV.USERS || '5000');    // distinct user ids (drives the cardinality experiment)

export const options = {
  scenarios: {
    steady: {
      executor: 'constant-arrival-rate',
      rate: RATE,
      timeUnit: '1s',
      duration: __ENV.DURATION || '15m',
      preAllocatedVUs: 20,
      maxVUs: 200,
    },
  },
  summaryTrendStats: ['avg', 'p(50)', 'p(95)', 'p(99)', 'max'],
};

export default function () {
  const user = `u${Math.floor(Math.random() * USERS)}`;
  http.get(`${__ENV.TARGET}/api/answer?user=${user}`, { tags: { name: '/api/answer' } });
}
