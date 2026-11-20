// Open-model load test: requests arrive at a fixed RATE whether or not earlier ones finished.
// That is how real users behave, and it is what exposes queueing (a closed model with a
// fixed number of VUs would slow its own arrival rate and hide the knee).
import http from 'k6/http';
import { check } from 'k6';

const TARGET = __ENV.TARGET || 'http://service:8080';
const RATE = parseInt(__ENV.RATE || '50', 10);        // requests per second
const DURATION = __ENV.DURATION || '30s';

export const options = {
  discardResponseBodies: true,
  summaryTrendStats: ['avg', 'p(50)', 'p(90)', 'p(99)', 'max'],
  scenarios: {
    open: {
      executor: 'constant-arrival-rate',
      rate: RATE,
      timeUnit: '1s',
      duration: DURATION,
      preAllocatedVUs: Math.max(50, RATE),
      maxVUs: 3000,
    },
  },
};

export function setup() {
  http.get(`${TARGET}/reset`);
}

export default function () {
  const res = http.get(`${TARGET}/work`, { timeout: '60s' });
  check(res, { 'status 200': (r) => r.status === 200 });
}

export function teardown() {
  // responseType overrides discardResponseBodies for this one call.
  const s = http.get(`${TARGET}/stats`, { responseType: 'text' }).json();
  console.log(`SERVER rate=${RATE} throughput=${s.throughput_rps} util=${s.utilisation} ` +
    `W_ms=${s.mean_w_ms} L=${s.L_time_avg} lambdaW=${s.lambda_times_W}`);
}

export function handleSummary(data) {
  const d = data.metrics.http_req_duration.values;
  const reqs = data.metrics.http_reqs.values;
  const dropped = data.metrics.dropped_iterations ? data.metrics.dropped_iterations.values.count : 0;
  const failed = data.metrics.http_req_failed ? data.metrics.http_req_failed.values.rate : 0;
  const line = `RESULT rate=${RATE} achieved_rps=${reqs.rate.toFixed(1)} ` +
    `p50_ms=${d['p(50)'].toFixed(1)} p90_ms=${d['p(90)'].toFixed(1)} p99_ms=${d['p(99)'].toFixed(1)} ` +
    `max_ms=${d.max.toFixed(1)} failed=${(failed * 100).toFixed(2)}% dropped=${dropped}\n`;
  return { stdout: line };
}
