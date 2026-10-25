// Exhaustive Hamming-ball scorer for LABS energies.
// For each start sequence, scores every sequence within Hamming radius r (2 or 3) using
// exact integer incremental autocorrelation updates, and reports the per-shell minima,
// counts below / equal to the start's threshold, and sampled evaluations for rescoring.
//
// Input (TSV): id N radius threshold E_start bits
// Output (JSONL, one line per start, in id order).
// Self-test: ./ball --self-test  (compares incremental energies with direct scoring for
// every flip set of size <= 3 on random sequences, N = 3..40).
#include <algorithm>
#include <atomic>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <fstream>
#include <iostream>
#include <mutex>
#include <sstream>
#include <string>
#include <thread>
#include <vector>

using std::vector;
using i64 = long long;

struct Start { int id, n, radius; i64 T, E; std::string bits; };

struct Hit { int f[3]; int k; i64 E; };

struct Result {
  i64 E0 = 0, min1 = INT64_MAX, min2 = INT64_MAX, min3 = INT64_MAX;
  Hit arg1{}, arg2{}, arg3{};
  i64 evaluated = 0, below = 0, ties = 0;
  vector<Hit> below_hits, tie_hits, samples;
};

static vector<int> spins(const std::string& b) {
  vector<int> s(b.size());
  for (size_t i = 0; i < b.size(); ++i) s[i] = b[i] == '1' ? 1 : -1;
  return s;
}

static i64 direct_energy(const vector<int>& s) {
  int n = s.size(); i64 e = 0;
  for (int k = 1; k < n; ++k) { i64 c = 0; for (int i = 0; i + k < n; ++i) c += s[i] * s[i + k]; e += c * c; }
  return e;
}

static inline i64 dot(const int* a, const int* b, int m) {
  int acc = 0;  // |a| <= ~2N, |b| <= 4, m < N: fits int32 for N < 10^4
  for (int k = 0; k < m; ++k) acc += a[k] * b[k];
  return acc;
}

// Core: enumerate the Hamming ball. sample_stride > 0 records every stride-th evaluation.
static Result score(const Start& st, i64 sample_stride, int cap = 10000) {
  const int n = st.n, m = n - 1;  // shifts k = 1..n-1 stored at index k-1
  vector<int> s = spins(st.bits);
  vector<int> C(m), D((size_t)n * m), Q(n);
  for (int k = 1; k < n; ++k) { int c = 0; for (int i = 0; i + k < n; ++i) c += s[i] * s[i + k]; C[k - 1] = c; }
  for (int x = 0; x < n; ++x) {
    int q = 0;
    for (int k = 1; k < n; ++k) {
      int t = 0;
      if (x + k < n) t += s[x + k];
      if (x - k >= 0) t += s[x - k];
      int d = -2 * s[x] * t;
      D[(size_t)x * m + k - 1] = d; q += d * d;
    }
    Q[x] = q;
  }
  Result r; i64 E0 = 0; for (int c : C) E0 += (i64)c * c; r.E0 = E0;
  auto rec = [&](int k, int a, int b, int c, i64 e) {
    r.evaluated++;
    Hit h{{a, b, c}, k, e};
    if (e < st.T) { r.below++; if ((int)r.below_hits.size() < cap) r.below_hits.push_back(h); }
    else if (e == st.T) { r.ties++; if ((int)r.tie_hits.size() < 200) r.tie_hits.push_back(h); }
    if (sample_stride > 0 && r.evaluated % sample_stride == 0) r.samples.push_back(h);
    if (k == 1 && e < r.min1) { r.min1 = e; r.arg1 = h; }
    if (k == 2 && e < r.min2) { r.min2 = e; r.arg2 = h; }
    if (k == 3 && e < r.min3) { r.min3 = e; r.arg3 = h; }
  };
  rec(0, -1, -1, -1, E0);
  vector<int> w(m), v(m);
  for (int i = 0; i < n; ++i) {
    const int* Di = &D[(size_t)i * m];
    rec(1, i, -1, -1, E0 + 2 * dot(C.data(), Di, m) + Q[i]);
    if (st.radius < 2) continue;
    i64 W = 0;
    for (int k = 0; k < m; ++k) { w[k] = C[k] + Di[k]; W += (i64)w[k] * w[k]; }
    for (int j = i + 1; j < n; ++j) {
      const int* Dj = &D[(size_t)j * m];
      int a = j - i - 1, c = 4 * s[i] * s[j];
      i64 e = W + 2 * dot(w.data(), Dj, m) + Q[j];
      i64 base = w[a] + Dj[a];
      e += 2 * c * base + (i64)c * c;
      rec(2, i, j, -1, e);
      if (st.radius < 3) continue;
      // v = C + D_i + D_j with the pair correction at shift j-i
      i64 V = 0;
      for (int k = 0; k < m; ++k) { v[k] = w[k] + Dj[k]; }
      v[a] += c;
      for (int k = 0; k < m; ++k) V += (i64)v[k] * v[k];
      for (int l = j + 1; l < n; ++l) {
        const int* Dl = &D[(size_t)l * m];
        int ai = l - i - 1, aj = l - j - 1, ci = 4 * s[i] * s[l], cj = 4 * s[j] * s[l];
        i64 e3 = V + 2 * dot(v.data(), Dl, m) + Q[l];
        e3 += 2 * ci * (i64)(v[ai] + Dl[ai]) + (i64)ci * ci;
        e3 += 2 * cj * (i64)(v[aj] + Dl[aj]) + (i64)cj * cj;
        rec(3, i, j, l, e3);
      }
    }
  }
  return r;
}

static int self_test() {
  uint64_t x = 0x9E3779B97F4A7C15ULL;
  auto rnd = [&]() { x ^= x << 13; x ^= x >> 7; x ^= x << 17; return x; };
  i64 checked = 0;
  for (int n = 3; n <= 40; ++n) {
    for (int rep = 0; rep < 3; ++rep) {
      std::string b(n, '0');
      for (auto& ch : b) ch = (rnd() & 1) ? '1' : '0';
      Start st{0, n, 3, 0, 0, b};
      Result r = score(st, 1, 0);
      vector<int> s = spins(b);
      if (r.E0 != direct_energy(s)) { std::fprintf(stderr, "E0 mismatch n=%d\n", n); return 1; }
      for (const Hit& h : r.samples) {
        vector<int> t = s;
        for (int q = 0; q < 3; ++q) if (h.f[q] >= 0) t[h.f[q]] = -t[h.f[q]];
        if (direct_energy(t) != h.E) {
          std::fprintf(stderr, "mismatch n=%d k=%d flips=%d,%d,%d got=%lld want=%lld\n", n, h.k,
                       h.f[0], h.f[1], h.f[2], h.E, direct_energy(t));
          return 1;
        }
        ++checked;
      }
      i64 expect = 1 + n + (i64)n * (n - 1) / 2 + (i64)n * (n - 1) * (n - 2) / 6;
      if (r.evaluated != expect) { std::fprintf(stderr, "count mismatch n=%d\n", n); return 1; }
    }
  }
  std::printf("self-test PASS: %lld flip sets (|F|<=3, N=3..40) match direct scoring\n", checked);
  return 0;
}

static std::string hit_json(const Hit& h) {
  std::ostringstream o;
  o << "{\"flips\":[";
  bool first = true;
  for (int q = 0; q < 3; ++q) if (h.f[q] >= 0) { o << (first ? "" : ",") << h.f[q]; first = false; }
  o << "],\"E\":" << h.E << "}";
  return o.str();
}

int main(int argc, char** argv) {
  if (argc > 1 && !std::strcmp(argv[1], "--self-test")) return self_test();
  if (argc < 3) { std::fprintf(stderr, "usage: ball starts.tsv threads\n"); return 2; }
  vector<Start> starts;
  { std::ifstream in(argv[1]); Start s; while (in >> s.id >> s.n >> s.radius >> s.T >> s.E >> s.bits) starts.push_back(s); }
  int threads = std::atoi(argv[2]);
  vector<int> order(starts.size());
  for (size_t i = 0; i < order.size(); ++i) order[i] = i;
  auto cost = [&](const Start& s) { double n = s.n; return s.radius == 3 ? n * n * n * n / 6 : n * n * n / 2; };
  std::sort(order.begin(), order.end(), [&](int a, int b) { return cost(starts[a]) > cost(starts[b]); });
  vector<std::string> out(starts.size());
  std::atomic<size_t> next{0};
  std::mutex mu;
  auto worker = [&]() {
    for (size_t q; (q = next++) < order.size();) {
      const Start& st = starts[order[q]];
      i64 total = 1 + st.n + (i64)st.n * (st.n - 1) / 2 + (st.radius == 3 ? (i64)st.n * (st.n - 1) * (st.n - 2) / 6 : 0);
      Result r = score(st, std::max<i64>(1, total / 12));
      if (r.E0 != st.E) { std::fprintf(stderr, "start %d: E0 %lld != input %lld\n", st.id, r.E0, st.E); std::exit(1); }
      std::ostringstream o;
      o << "{\"id\":" << st.id << ",\"N\":" << st.n << ",\"radius\":" << st.radius << ",\"T\":" << st.T
        << ",\"E_start\":" << r.E0 << ",\"evaluated\":" << r.evaluated << ",\"expected\":" << total
        << ",\"min1\":" << hit_json(r.arg1) << ",\"min2\":" << (st.radius >= 2 ? hit_json(r.arg2) : "null")
        << ",\"min3\":" << (st.radius >= 3 ? hit_json(r.arg3) : "null")
        << ",\"below\":" << r.below << ",\"ties\":" << r.ties << ",\"below_hits\":[";
      for (size_t z = 0; z < r.below_hits.size(); ++z) o << (z ? "," : "") << hit_json(r.below_hits[z]);
      o << "],\"tie_hits\":[";
      for (size_t z = 0; z < r.tie_hits.size(); ++z) o << (z ? "," : "") << hit_json(r.tie_hits[z]);
      o << "],\"samples\":[";
      for (size_t z = 0; z < r.samples.size(); ++z) o << (z ? "," : "") << hit_json(r.samples[z]);
      o << "]}";
      out[order[q]] = o.str();
      std::lock_guard<std::mutex> g(mu);
      std::fprintf(stderr, "done id=%d N=%d r=%d\n", st.id, st.n, st.radius);
    }
  };
  vector<std::thread> pool;
  for (int t = 0; t < threads; ++t) pool.emplace_back(worker);
  for (auto& t : pool) t.join();
  for (auto& line : out) std::cout << line << "\n";
  return 0;
}
