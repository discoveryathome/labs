// Standalone baseline solver; the authoritative checker is verify.py.
#include <algorithm>
#include <chrono>
#include <cstdint>
#include <ctime>
#include <iostream>
#include <limits>
#include <stdexcept>
#include <string>
#include <vector>
using std::vector;
using i64 = std::int64_t;

struct RNG {
    std::uint64_t x;
    std::uint64_t next() { // SplitMix64, specified independently of stdlib distributions.
        std::uint64_t z = (x += 0x9e3779b97f4a7c15ULL);
        z = (z ^ (z >> 30)) * 0xbf58476d1ce4e5b9ULL;
        z = (z ^ (z >> 27)) * 0x94d049bb133111ebULL;
        return z ^ (z >> 31);
    }
    std::uint64_t below(std::uint64_t n) {
        auto threshold = -n % n;
        for (;;) { auto r = next(); if (r >= threshold) return r % n; }
    }
};
struct State {
    vector<int> s, c;
    i64 e = 0;
    explicit State(vector<int> v): s(v), c(v.size(), 0) {
        for (int k=1; k<(int)s.size(); ++k) {
            for (int j=0; j+k<(int)s.size(); ++j) c[k] += s[j]*s[j+k];
            e += i64(c[k])*c[k];
        }
    }
    int dc(int j, int k) const {
        int a=0;
        if (j>=k) a+=s[j-k];
        if (j+k<(int)s.size()) a+=s[j+k];
        return -2*s[j]*a;
    }
    i64 delta(int j) const {
        i64 d=0;
        for (int k=1; k<(int)s.size(); ++k) {
            int a=dc(j,k);
            d+=2*i64(c[k])*a+i64(a)*a;
        }
        return d;
    }
    void flip(int j) {
        for (int k=1; k<(int)s.size(); ++k) {
            int a=dc(j,k);
            e+=2*i64(c[k])*a+i64(a)*a;
            c[k]+=a;
        }
        s[j]=-s[j];
    }
};

void selftest() {
    RNG rng{17};
    for (int n=2;n<=128;++n) {
        vector<int> s(n);
        for (auto &v:s) v=rng.below(2)?1:-1;
        State a(s);
        for (int t=0;t<12;++t) {
            for (int j=0;j<n;++j) {
                auto v=a.s; v[j]*=-1; State b(v);
                if (a.e+a.delta(j)!=b.e) throw std::runtime_error("delta mismatch");
            }
            a.flip(rng.below(n));
            State b(a.s);
            if (a.e!=b.e || a.c!=b.c) throw std::runtime_error("update mismatch");
        }
    }
    std::cout<<"PASS: incremental deltas and updates N=2..128\n";
}

int main(int argc,char**argv) {
    try {
        if (argc==2 && std::string(argv[1])=="--self-test") {selftest();return 0;}
        if (argc<5 || argc>6) throw std::runtime_error("usage: search N SEED EVAL_BUDGET hill|tabu [01-start]");
        int n=std::stoi(argv[1]); std::uint64_t seed=std::stoull(argv[2]);
        i64 budget=std::stoll(argv[3]); std::string method=argv[4];
        if (n<2 || n>10000 || budget<n || (method!="hill" && method!="tabu"))
            throw std::runtime_error("invalid N, budget or method");
        RNG rng{seed};
        vector<int> initial(n);
        bool warm=argc==6;
        if (warm) {
            std::string b=argv[5];
            if ((int)b.size()!=n || b.find_first_not_of("01")!=std::string::npos)
                throw std::runtime_error("invalid start");
            for (int i=0;i<n;++i) initial[i]=b[i]=='1'?1:-1;
        } else for (auto &v:initial) v=rng.below(2)?1:-1;
        auto wall0=std::chrono::steady_clock::now(); auto cpu0=std::clock();
        State cur(initial);
        i64 initial_e=cur.e, best_e=cur.e, evals=0, iter=0, restarts=0;
        i64 last_improve=0, improvements=0;
        vector<int> best=cur.s;
        vector<i64> tabu(n,0);
        while (evals+n<=budget) {
            i64 min_delta=std::numeric_limits<i64>::max(); int chosen=-1,ties=0;
            for (int j=0;j<n;++j) {
                i64 d=cur.delta(j);++evals;
                if (method=="tabu" && tabu[j]>iter && cur.e+d>=best_e) continue;
                if (d<min_delta) {min_delta=d;chosen=j;ties=1;}
                else if (d==min_delta && rng.below(++ties)==0) chosen=j;
            }
            bool restart=chosen<0 || (method=="hill" && min_delta>=0) ||
                         (method=="tabu" && iter-last_improve>=4*n);
            if (restart) {
                vector<int> s(n);
                if (warm) {
                    s=best;
                    // Distinct kick coordinates: exactly 2..9 bit flips.
                    vector<int> positions(n);
                    for (int j=0;j<n;++j) positions[j]=j;
                    int count=std::min(n,2+int(rng.below(8)));
                    for (int j=0;j<count;++j) {
                        int k=j+rng.below(n-j);std::swap(positions[j],positions[k]);
                        s[positions[j]]*=-1;
                    }
                } else for (auto &v:s) v=rng.below(2)?1:-1;
                cur=State(s);std::fill(tabu.begin(),tabu.end(),0);
                ++restarts;last_improve=iter;
            } else {
                cur.flip(chosen);
                tabu[chosen]=iter+1+std::max(2,n/10)+rng.below(std::max(1,n/20));
            }
            ++iter;
            if (cur.e<best_e) {
                best_e=cur.e;best=cur.s;last_improve=iter;++improvements;
            }
        }
        State check(best);
        if (check.e!=best_e) throw std::runtime_error("final full-score mismatch");
        double cpu=double(std::clock()-cpu0)/CLOCKS_PER_SEC;
        double wall=std::chrono::duration<double>(std::chrono::steady_clock::now()-wall0).count();
        std::string bits;for (int v:best) bits+=v==1?'1':'0';
        std::cout.precision(12);
        std::cout<<"{\"N\":"<<n<<",\"seed\":"<<seed<<",\"budget\":"<<budget
                 <<",\"method\":\""<<method<<"\",\"start\":\""<<(warm?"published":"random")
                 <<"\",\"initial_E\":"<<initial_e<<",\"E\":"<<best_e
                 <<",\"evaluations\":"<<evals<<",\"iterations\":"<<iter
                 <<",\"restarts\":"<<restarts<<",\"incumbent_improvements\":"<<improvements
                 <<",\"cpu_seconds\":"<<cpu<<",\"wall_seconds\":"<<wall
                 <<",\"sequence\":\""<<bits<<"\"}\n";
    } catch (const std::exception &e) {std::cerr<<e.what()<<"\n";return 1;}
}
