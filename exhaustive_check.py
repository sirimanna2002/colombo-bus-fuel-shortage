# Exhaustive check: is greedy optimal for small budgets (k <= 7)?
# Also computes the centrality-first baseline. Run: python exhaustive_check.py
# (about 2-4 minutes). Data is the same as in bus_route_selection.py.
import json, itertools, random, time
import networkx as nx
r = {
 "bus": {
  "138": [
   "Homagama",
   "Kottawa",
   "Maharagama",
   "Nugegoda",
   "Kirulapana",
   "Thummulla",
   "SlaveIsland",
   "Fort",
   "Pettah"
  ],
  "183": [
   "Nugegoda",
   "Kalubowila",
   "Dehiwala",
   "Moratuwa",
   "Panadura"
  ],
  "212/341": [
   "Nugegoda",
   "Maharagama",
   "Pannipitiya",
   "Erawwala",
   "Makuludoowa",
   "Bokundara"
  ],
  "992": [
   "Nugegoda",
   "Maharagama",
   "Pannipitiya",
   "Athurugiriya"
  ],
  "119": [
   "Nugegoda",
   "JubileePost",
   "Embuldeniya",
   "Maharagama"
  ],
  "689": [
   "Nugegoda",
   "Udahamulla",
   "Madiwela",
   "Thalawathugoda",
   "Hokandara"
  ],
  "690": [
   "Nugegoda",
   "JubileePost",
   "Embuldeniya",
   "Madiwela",
   "Kimbulawala",
   "JayawardenepuraHospital"
  ],
  "163": [
   "Dehiwala",
   "Nugegoda",
   "Pagoda",
   "Kotte",
   "Battaramulla"
  ],
  "313": [
   "Homagama",
   "Kottawa",
   "Maharagama",
   "Kohuwala",
   "Kalubowila"
  ],
  "308": [
   "Maharagama",
   "Niyandagala",
   "Kottawa",
   "Homagama"
  ],
  "128/1": [
   "Maharagama",
   "Homagama",
   "Munamalewatta"
  ],
  "124": [
   "Maharagama",
   "Godagama",
   "Homagama",
   "IhalaBope"
  ],
  "376": [
   "Kottawa",
   "Rukmale",
   "Malabe"
  ],
  "171": [
   "Pelawatta",
   "Battaramulla",
   "Rajagiriya",
   "Borella",
   "Fort"
  ],
  "170": [
   "Athurugiriya",
   "Battaramulla",
   "Borella",
   "TownHall",
   "Pettah"
  ],
  "190": [
   "Meegoda",
   "Godagama",
   "Battaramulla",
   "Borella",
   "TownHall",
   "Pettah"
  ],
  "174": [
   "Kottawa",
   "Thalawathugoda",
   "Battaramulla",
   "Borella"
  ],
  "177": [
   "Kaduwela",
   "Battaramulla",
   "Borella",
   "Kollupitiya"
  ],
  "17": [
   "Panadura",
   "Moratuwa",
   "Ratmalana",
   "Dehiwala",
   "Nugegoda",
   "Kotte",
   "Battaramulla"
  ],
  "103": [
   "Borella",
   "Narahenpita"
  ],
  "144": [
   "Rajagiriya",
   "Fort"
  ],
  "117": [
   "Nugegoda",
   "Pepiliyana",
   "Attidiya",
   "Ratmalana"
  ],
  "192": [
   "Moratuwa",
   "Maharagama"
  ],
  "Mhg-Dehiwala": [
   "Maharagama",
   "Boralesgamuwa",
   "Bellanwila",
   "Dehiwala"
  ],
  "Mhg-Ratmalana": [
   "Maharagama",
   "Borupana",
   "Ratmalana"
  ],
  "CM01": [
   "Makumbura",
   "Pettah",
   "Fort"
  ],
  "CM02": [
   "MillenniumCity",
   "Fort"
  ],
  "CM03": [
   "Kadawatha",
   "Makumbura"
  ],
  "CM04": [
   "Dematagoda",
   "Panadura"
  ],
  "CM05": [
   "Battaramulla",
   "Ekala"
  ],
  "CM08": [
   "Kesbewa",
   "Pettah"
  ]
 },
 "train": {
  "Train-Coastal": [
   "Fort",
   "Kollupitiya",
   "Bambalapitiya",
   "Wellawatte",
   "Dehiwala",
   "MtLavinia",
   "Ratmalana",
   "Moratuwa",
   "Panadura"
  ],
  "Train-KV": [
   "Fort",
   "Nugegoda",
   "Pangiriwatte",
   "Nawinna",
   "Maharagama"
  ],
  "Train-Main": [
   "Fort",
   "Maradana",
   "Dematagoda",
   "Kelaniya",
   "Ragama"
  ]
 }
}


def prep(bus, train):
    allr = {**bus, **train}
    stops = sorted({s for v in allr.values() for s in v}); idx = {s:i for i,s in enumerate(stops)}
    edges = {n: [(idx[a], idx[b]) for a,b in zip(v,v[1:]) if a!=b] for n,v in allr.items()}
    return allr, stops, idx, edges

def make_eval(bus, train):
    allr, stops, idx, edges = prep(bus, train)
    n = len(stops); tn = list(train); bn = list(bus)
    base_edges = [e for t in tn for e in edges[t]]
    def score(kept):
        p = list(range(n))
        def find(x):
            while p[x] != x:
                p[x] = p[p[x]]; x = p[x]
            return x
        for a,b in base_edges:
            ra, rb = find(a), find(b)
            if ra != rb: p[ra] = rb
        for rt in kept:
            for a,b in edges[rt]:
                ra, rb = find(a), find(b)
                if ra != rb: p[ra] = rb
        cnt = {}
        for i in range(n):
            ri = find(i); cnt[ri] = cnt.get(ri,0)+1
        return sum(c*(c-1) for c in cnt.values())/(n*(n-1))
    return score, bn, tn, allr, stops

def greedy(score, bn):
    kept, cur, rem, curve = [], score([]), list(bn), [score([])]
    for k in range(1, len(bn)+1):
        best = max(rem, key=lambda x: score(kept+[x])); kept.append(best); rem.remove(best); curve.append(score(kept))
    return curve

def central_first(bus, train, score, bn):
    G = nx.Graph(); allr = {**bus, **train}
    for v in allr.values():
        for a,b in zip(v,v[1:]):
            if a!=b: G.add_edge(a,b)
    btw = nx.betweenness_centrality(G)
    rank = sorted(bn, key=lambda x: sum(btw[s] for s in set(bus[x])), reverse=True)
    return [score(rank[:k]) for k in range(len(bn)+1)], rank

def auc(ys):
    N = len(ys)-1
    return sum((ys[i]+ys[i+1])/2 for i in range(N))/N

out = {}
for label, bus in (("full", r['bus']), ("noCM", {k:v for k,v in r['bus'].items() if not k.startswith('CM')})):
    score, bn, tn, allr, stops = make_eval(bus, r['train'])
    N = len(bn)
    g = greedy(score, bn)
    cf, rank = central_first(bus, r['train'], score, bn)
    out[label] = {"N": N, "greedy": g, "central": cf, "central_rank": rank,
                  "central_auc": auc(cf), "greedy_auc": auc(g)}
    ks = {"25": round(.25*N), "50": round(.5*N), "75": round(.75*N)}
    print(label, "N=",N, {p:(k, round(cf[k],3)) for p,k in ks.items()}, "central AUC", round(auc(cf),3), "greedy AUC", round(auc(g),3))
    print("  central order (top 8):", rank[:8])
    # exhaustive for small k
    ex = {}
    for k in range(1, 8):
        t0 = time.time(); best = -1; bset = None
        for combo in itertools.combinations(bn, k):
            s = score(combo)
            if s > best + 1e-12: best, bset = s, combo
        ex[k] = (best, list(bset), time.time()-t0, sum(1 for _ in [0]))
        print(f"  exact k={k}: best={best:.4f} greedy={g[k]:.4f} diff={best-g[k]:+.4f}  ({time.time()-t0:.1f}s) set={bset}")
    out[label]["exact"] = {k:(v[0], v[1]) for k,v in ex.items()}


# non-submodularity: toy + search in real data
score, bn, tn, allr, stops = make_eval(r['bus'], r['train'])
random.seed(0); found = None
for _ in range(20000):
    k = random.randint(0,6); S = random.sample(bn,k); extra = random.sample([x for x in bn if x not in S], random.randint(1,4))
    T = S + extra; rest = [x for x in bn if x not in T]
    x = random.choice(rest)
    gS = score(S+[x]) - score(S); gT = score(T+[x]) - score(T)
    if gT > gS + 1e-9: found = (S, T, x, gS, gT); break
print("non-submodular instance in data:", found)
