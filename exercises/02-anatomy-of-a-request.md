# 02 — Exercises

Lesson: [course/01-foundations/02-anatomy-of-a-request.md](../course/01-foundations/02-anatomy-of-a-request.md)

### 1. [Core] Count the round trips

Before the first byte of the response arrives, how many round trips does a brand-new HTTPS request cost over
(a) TCP + TLS 1.2, (b) TCP + TLS 1.3, (c) QUIC/HTTP/3? Ignore DNS.

<details><summary>Answer</summary>

Handshakes plus one round trip for the request and response itself:
(a) 1 (TCP) + 2 (TLS 1.2) + 1 = **4 RTT**.
(b) 1 + 1 + 1 = **3 RTT**.
(c) 1 (combined QUIC + TLS) + 1 = **2 RTT**.
With session resumption and 0-RTT, QUIC can send the request in its first flight (**1 RTT** to the first byte),
but only for replay-safe requests. TLS 1.3 resumption over TCP still needs the TCP handshake first.
</details>

### 2. [Core] 0-RTT safety

Your team wants to enable TLS 1.3 0-RTT on the API to save a round trip. What risk does this introduce, and how
do you limit it?

<details><summary>Answer</summary>

Early data can be **replayed**: RFC 8446 §2.3 states there are "no guarantees of non-replay between
connections". An attacker who captures a client's first flight can resend it, so a `POST /payments` sent as
early data could execute twice. Mitigations: accept early data only for safe, idempotent methods (`GET`,
`HEAD`) on endpoints without side effects. Have the server or proxy answer `425 Too Early` (RFC 8470) to
anything else, which makes the client retry after the handshake. Optionally use server-side anti-replay
mechanisms (RFC 8446 §8), which limit but do not remove the risk across a distributed fleet. Never rely on 0-RTT
for state-changing requests.
</details>

### 3. [Core] DNS TTL and failover

Your `api.example.com` record has a TTL of 300 s. You fail over to another region by changing the record. Why do
some clients take much longer than 5 minutes to move? What would you do *next week* before a planned migration?

<details><summary>Answer</summary>

Reasons: resolvers cached the record at any point during the last 300 s, so the worst case is the full TTL; some
resolvers and clients stretch or ignore TTLs (minimum-TTL policies, operating-system and runtime caches); client
applications reuse **existing connections**, which never look up DNS again until they reconnect; serve-stale
(RFC 8767) can keep answering old data if a resolver can't reach your authoritative servers. Before a planned
migration: lower the TTL to about 30–60 s **at least one old TTL in advance** (ideally a day before), keep the old
target serving until traffic actually drains, and close keep-alive connections on the old side to force
reconnection.
</details>

### 4. [Core] Slow start

A server sends a 50 KB HTML response on a new TCP connection with a 10-segment initial window (MSS 1,460 bytes),
and the window doubles each round trip. How many round trips of data transfer are needed? At a 60 ms RTT, how much
time does that add compared with a 14 KB response?

<details><summary>Answer</summary>

Cumulative bytes after each round: 14.6 KB, 43.8 KB, 102.2 KB. 50 KB needs **3 rounds** (it exceeds 43.8 KB).
A 14 KB response fits in **1 round**. Difference = 2 RTT = **120 ms** at 60 ms RTT. This is an idealised slow
start with no loss and no delayed-ACK effects, but the order of magnitude explains the front-end rule of thumb
of keeping the critical first response under about 14 KB, and the value of warm connections whose window has
already grown.
</details>

### 5. [Core] HTTP/2 vs HTTP/3

On a mobile network with 2% packet loss, why can HTTP/2 over one TCP connection, by the mechanism alone, perform
*worse* than HTTP/1.1 with six connections? How does HTTP/3 address it, and what does it cost?

<details><summary>Answer</summary>

HTTP/2 multiplexes all streams onto one TCP connection. TCP delivers bytes in order, so one lost segment stalls
**every** stream until it is retransmitted (transport head-of-line blocking). With six HTTP/1.1 connections, a
loss stalls only the one connection that carried it. (This is a mechanism argument; whether it wins on a given path is something to measure.) HTTP/3 runs over QUIC, which orders data per stream, so a loss
delays only the streams whose data was in the lost packet. QUIC also merges the transport and TLS handshakes.
Costs: UDP may be blocked or throttled (keep an HTTP/2 fallback), QUIC currently uses more CPU per byte (a WWW 2024
study measured up to 45.2% lower data rates on fast links), and load balancers must understand connection IDs.
</details>

### 6. [Core] Keep-alive 502s

Users report occasional `502 Bad Gateway` errors, more often after quiet periods. The proxy's upstream idle timeout
is 75 s and the application server's keep-alive timeout is 5 s. Explain the mechanism and the fix.

<details><summary>Answer</summary>

The application closes idle keep-alive connections after 5 s, but the proxy believes they are reusable for up to
75 s. When a request arrives on a connection the server has just closed (or is closing), the proxy writes to a
dead socket, gets a reset, and returns 502. Quiet periods leave more connections idle past 5 s. Fix: make each
upstream's idle timeout **longer** than that of the hop in front of it. Here the application keep-alive should be
above the proxy's 75 s, or the proxy's upstream idle timeout should drop below 5 s. AWS documents exactly this
rule for ALB, whose default idle timeout is 60 s. Retrying idempotent requests on connection reset is a useful
second layer.
</details>

### 7. [Core] Anycast vs GeoDNS

Lumen must keep EU users' requests in the EU (data residency) and wants the fastest possible failover between
edge PoPs. Which steering mechanism do you use for each goal, and why?

<details><summary>Answer</summary>

**Anycast for the edge**: PoPs announce the same prefix, and withdrawing a failing PoP shifts traffic at routing
speed, with no DNS cache in the way. **GeoDNS or edge routing logic for residency**: anycast follows BGP, not
national borders, so a user near a border may reach a PoP in another jurisdiction. Residency is better enforced
by choosing the *origin region* per user or tenant (at the edge, from account data) than by trusting network
location. GeoDNS sees the resolver's location, not the user's, unless EDNS Client Subnet is used.
</details>

### 8. [Deep] QUIC and the load balancer

Why can't a layer-4 load balancer route QUIC by hashing the UDP 4-tuple? What do QUIC-aware balancers route on
instead?

<details><summary>Answer</summary>

QUIC connections survive changes of client address and port: connection migration (RFC 9000 §9) and NAT
rebinding. When the 4-tuple changes, a 4-tuple hash sends the packets to a different server, which has no state
for that connection, and the connection fails or must restart. QUIC packets carry **connection IDs** that the
server chose. A QUIC-aware balancer routes on the connection ID, often with routing information encoded into it
(the IETF QUIC-LB approach), so all packets of a connection reach the same server whatever path they take.
</details>

### 9. [Lab] Measure the phases with curl

Run, three times each, against `https://example.com/`:

```bash
curl -so /dev/null -w 'dns=%{time_namelookup} connect=%{time_connect} tls=%{time_appconnect} ttfb=%{time_starttransfer}\n' https://example.com/
```

Compute TCP and TLS handshake times. Then run with `--http3` (if your curl supports it) and compare. Explain the
differences between the first and later runs.

<details><summary>Answer</summary>

Values are cumulative seconds. TCP ≈ `connect − dns` (about one RTT). TLS ≈ `tls − connect` (about one RTT for
TLS 1.3). Server time + one RTT ≈ `ttfb − tls`. The first run usually has a larger `dns` value (resolver cache
miss). Later runs show `dns` near zero or a few ms (cached), while connect and TLS stay the same, because each
`curl` invocation opens a new connection. With `--http3`, `connect` and `appconnect` collapse into one combined
handshake. Expect the total to the first byte to be about one RTT lower, if UDP/443 is not blocked on your
network. If `--http3` fails, that is itself a finding: your network blocks or breaks QUIC, and real users on
similar networks fall back to TCP. Your exact numbers depend on your location relative to the nearest edge for
example.com, so there is no single correct value.
</details>

### 10. [Interview] What happens when you type a URL?

Give a structured three-minute answer to "What happens when you type `https://lumen.example.com` and press
Enter?", naming at least six components and the round trips involved.

<details><summary>Answer</summary>

A strong answer goes in order and counts round trips. (1) Browser cache, HSTS (upgrade to HTTPS), and possibly a
service worker. (2) DNS: stub resolver → recursive resolver (cached, or walks root → `.com` → authoritative) →
A/AAAA plus an HTTPS record that may advertise HTTP/3. (3) Connection: TCP handshake (1 RTT) + TLS 1.3 (1 RTT), or
QUIC (1 RTT combined), with an anycast CDN edge as the likely endpoint. Certificate validation. SNI, or ECH.
(4) HTTP request: the edge checks its cache. On a miss it forwards over a warm, pooled connection to the origin's
load balancer, then to an app instance (SYSDESIGN-03). (5) Response: slow start for large bodies, compression,
cache headers. (6) Browser parses the HTML, fetches sub-resources over the same HTTP/2 or HTTP/3 connection, and
renders. Bonus: mention what you'd measure (phase-level timings from real users) and one failure (DNS, an expired
certificate, a keep-alive mismatch). The red flag is listing components without saying which round trips they
cost or remove.
</details>
