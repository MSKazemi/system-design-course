// Open-model load through the load balancer. Counts responses per backend replica and
// reports client-side latency percentiles and errors.
import http from 'k6/http';
import { check } from 'k6';
import { Counter } from 'k6/metrics';

const PORTS = { roundrobin: 8080, leastconn: 8081, p2c: 8082 };
const ALGO = __ENV.ALGO || 'roundrobin';
const TARGET = __ENV.TARGET || `http://lb:${PORTS[ALGO]}`;  // override when running k6 outside compose
const RATE = parseInt(__ENV.RATE || '300', 10);
const DURATION = __ENV.DURATION || '30s';
const perBackend = new Counter('per_backend');

export const options = {
  summaryTrendStats: ['avg', 'p(50)', 'p(99)', 'max'],
  // k6 only reports tagged sub-metrics that have a threshold, so declare a no-op one for each.
  thresholds: Object.fromEntries(
    ['app1', 'app2', 'app3', 'status_0', 'status_502', 'status_503', 'status_504']
      .map((b) => [`per_backend{backend:${b}}`, ['count>=0']])),
  scenarios: {
    open: {
      executor: 'constant-arrival-rate',
      rate: RATE, timeUnit: '1s', duration: DURATION,
      preAllocatedVUs: Math.max(100, RATE), maxVUs: 5000,
    },
  },
};

export default function () {
  const res = http.get(`${TARGET}/work`, { timeout: '30s' });
  check(res, { 'status 200': (r) => r.status === 200 });
  let name = `status_${res.status}`;
  if (res.status === 200) {
    try { name = res.json().name; } catch (e) { name = 'unparsable'; }
  }
  perBackend.add(1, { backend: name });
}

export function handleSummary(data) {
  const d = data.metrics.http_req_duration.values;
  const failed = data.metrics.http_req_failed.values;
  const n = data.metrics.http_reqs.values.count;
  const parts = [];
  for (const [k, v] of Object.entries(data.metrics)) {
    const m = k.match(/^per_backend\{backend:(.+)\}$/);
    if (m) parts.push(`${m[1]}=${v.values.count}`);
  }
  return { stdout: `RESULT algo=${ALGO} rate=${RATE} requests=${n} ` +
    `p50_ms=${d['p(50)'].toFixed(1)} p99_ms=${d['p(99)'].toFixed(1)} max_ms=${d.max.toFixed(1)} ` +
    `errors=${failed.passes} (${(failed.rate * 100).toFixed(2)}%) split: ${parts.sort().join(' ')}\n` };
}
