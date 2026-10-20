// Donor experiment: State and RNG copied from baseline at 033dc75.
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

// Eight exact energy-preserving transformations; rotation is deliberately absent.
std::string canonical(const vector<int>& s) {
    std::string best;
    int n=s.size();
    for (int rev=0;rev<2;++rev) for (int alt=0;alt<2;++alt)
        for (int sign: {-1,1}) {
            std::string b;
            for (int j=0;j<n;++j) {
                int v=s[rev?n-1-j:j]*sign*((alt && j%2)?-1:1);
                b+=v==1?'1':'0';
            }
            if (best.empty() || b<best) best=b;
        }
    return best;
}
struct Entry { i64 e; vector<int> s; std::string key; };
void archive(vector<Entry>& pool, const State& a, int capacity) {
    std::string key=canonical(a.s);
    for (auto &x:pool) if (x.key==key) return;
    pool.push_back({a.e,a.s,key});
    std::sort(pool.begin(),pool.end(),[](const Entry&a,const Entry&b){
        return a.e<b.e || (a.e==b.e && a.key<b.key);
    });
    if ((int)pool.size()>capacity) pool.pop_back();
}
void test() {
    RNG rng{8837};
    for (int n=2;n<=128;++n) {
        vector<int>s(n);
        for (auto&v:s)v=rng.below(2)?1:-1;
        State a(s);
        for (int t=0;t<20;++t) {
            for (int j=0;j<n;++j) {
                auto s2=a.s;s2[j]*=-1;State b(s2);
                if (a.e+a.delta(j)!=b.e) throw std::runtime_error("delta");
            }
            a.flip(rng.below(n));State b(a.s);
            if (a.e!=b.e || a.c!=b.c) throw std::runtime_error("state");
        }
        auto key=canonical(a.s);
        vector<int>v;for(char x:key)v.push_back(x=='1'?1:-1);
        if (State(v).e!=a.e || canonical(v)!=key) throw std::runtime_error("orbit");
        vector<Entry>pool;archive(pool,a,8);archive(pool,State(v),8);
        if (pool.size()!=1) throw std::runtime_error("dedup");
    }
    std::cout<<"PASS: deltas, updates, symmetry and archive N=2..128\n";
}
int main(int argc,char**argv) {
  try {
    if (argc==2 && std::string(argv[1])=="--self-test"){test();return 0;}
    if (argc<6 || argc>7) throw std::runtime_error(
        "usage: search N SEED EVAL_BUDGET iterated|population STAGNATION_N [01-start]");
    int n=std::stoi(argv[1]),stagnation=std::stoi(argv[5]);
    std::uint64_t seed=std::stoull(argv[2]);i64 budget=std::stoll(argv[3]);
    std::string method=argv[4];bool warm=argc==7;
    if(n<2 || n>10000 || budget<n || stagnation<1 ||
       (method!="iterated" && method!="population"))throw std::runtime_error("arguments");
    RNG rng{seed};vector<int> initial(n);
    if(warm){
        std::string b=argv[6];
        if((int)b.size()!=n || b.find_first_not_of("01")!=std::string::npos)
            throw std::runtime_error("start");
        for(int j=0;j<n;++j)initial[j]=b[j]=='1'?1:-1;
    }else for(auto&v:initial)v=rng.below(2)?1:-1;
    auto w0=std::chrono::steady_clock::now();auto c0=std::clock();
    State cur(initial),best(cur),local(cur);
    i64 initial_e=cur.e,evals=0,iter=0,restarts=0,last_local=0,epoch=0,improvements=0;
    vector<i64>tabu(n,0);vector<Entry>pool;
    archive(pool,cur,method=="population"?8:1);
    while(evals+n<=budget){
        i64 md=std::numeric_limits<i64>::max();int chosen=-1,ties=0;
        for(int j=0;j<n;++j){
            i64 d=cur.delta(j);++evals;
            if(tabu[j]>iter && cur.e+d>=local.e)continue;
            if(d<md){md=d;chosen=j;ties=1;}
            else if(d==md && rng.below(++ties)==0)chosen=j;
        }
        if(chosen<0 || iter-last_local>=i64(stagnation)*n ||
           iter-epoch>=i64(4*stagnation)*n){
            archive(pool,local,method=="population"?8:1);
            vector<int>s;
            // One in ten restarts is a wholly fresh start, even for warm runs.
            if(rng.below(10)==0){
                s.resize(n);for(auto&v:s)v=rng.below(2)?1:-1;
            }else{
                int a=0;
                if(method=="population"){
                    int p=rng.below(pool.size()),q=rng.below(pool.size());
                    a=std::min(p,q); // Rank-biased tournament.
                }
                s=pool[a].s;
                if(method=="population" && pool.size()>1 && rng.below(4)==0){
                    int b=rng.below(pool.size());
                    for(int j=0;j<n;++j)if(rng.below(2))s[j]=pool[b].s[j];
                }
                vector<int>positions(n);for(int j=0;j<n;++j)positions[j]=j;
                int count=std::min(n,2+int(rng.below(11)));
                for(int j=0;j<count;++j){
                    int k=j+rng.below(n-j);std::swap(positions[j],positions[k]);
                    s[positions[j]]*=-1;
                }
            }
            cur=State(s);local=cur;epoch=last_local=iter;
            std::fill(tabu.begin(),tabu.end(),0);++restarts;
        }else{
            cur.flip(chosen);
            tabu[chosen]=iter+1+std::max(2,n/10)+rng.below(std::max(1,n/20));
        }
        ++iter;
        if(cur.e<local.e){local=cur;last_local=iter;}
        if(cur.e<best.e){best=cur;++improvements;}
    }
    State exact(best.s);
    if(exact.e!=best.e || exact.c!=best.c)throw std::runtime_error("final check");
    std::string bits;for(int v:best.s)bits+=v==1?'1':'0';
    std::cout.precision(12);
    std::cout<<"{\"N\":"<<n<<",\"seed\":"<<seed<<",\"budget\":"<<budget
      <<",\"method\":\""<<method<<"\",\"stagnation\":"<<stagnation
      <<",\"start\":\""<<(warm?"published":"random")<<"\",\"initial_E\":"<<initial_e
      <<",\"E\":"<<best.e<<",\"evaluations\":"<<evals<<",\"iterations\":"<<iter
      <<",\"restarts\":"<<restarts<<",\"incumbent_improvements\":"<<improvements
      <<",\"pool_size\":"<<pool.size()<<",\"canonical\":\""<<canonical(best.s)
      <<"\",\"cpu_seconds\":"<<double(std::clock()-c0)/CLOCKS_PER_SEC
      <<",\"wall_seconds\":"<<std::chrono::duration<double>(std::chrono::steady_clock::now()-w0).count()
      <<",\"sequence\":\""<<bits<<"\"}\n";
  }catch(const std::exception&e){std::cerr<<e.what()<<"\n";return 1;}
}

