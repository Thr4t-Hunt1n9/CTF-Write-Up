import sys
from pwn import *
from collections import defaultdict
import math
import heapq

HOST = "play.scriptsorcerers.xyz"
PORT = 10325

ASSUMED_MAXV = 100000

def precompute_phi_divisors(V):
    phi = list(range(V+1))
    for i in range(2, V+1):
        if phi[i] == i:
            for j in range(i, V+1, i):
                phi[j] -= phi[j] // i
    divisors = [[] for _ in range(V+1)]
    for d in range(1, V+1):
        for m in range(d, V+1, d):
            divisors[m].append(d)
    return phi, divisors

class SlidingMedian:
    def __init__(self, w):
        self.w = w
        self.lower = []   
        self.upper = []   
        self.del_lower = defaultdict(int)
        self.del_upper = defaultdict(int)
        self.size_lower = 0
        self.size_upper = 0

    def prune_lower(self):
        
        while self.lower:
            val = -self.lower[0]
            if self.del_lower.get(val, 0) > 0:
                heapq.heappop(self.lower)
                self.del_lower[val] -= 1
                if self.del_lower[val] == 0:
                    del self.del_lower[val]
            else:
                break

    def prune_upper(self):
        while self.upper:
            val = self.upper[0]
            if self.del_upper.get(val, 0) > 0:
                heapq.heappop(self.upper)
                self.del_upper[val] -= 1
                if self.del_upper[val] == 0:
                    del self.del_upper[val]
            else:
                break

    def rebalance(self):
        target = (self.w + 1) // 2

        self.prune_lower()
        self.prune_upper()

        while self.size_lower > target:
            self.prune_lower()
            if not self.lower:
                break
            v = -heapq.heappop(self.lower)
            self.size_lower -= 1
            heapq.heappush(self.upper, v)
            self.size_upper += 1
            self.prune_lower()
            self.prune_upper()

        while self.size_lower < target:
            self.prune_upper()
            if not self.upper:
                break
            v = heapq.heappop(self.upper)
            self.size_upper -= 1
            heapq.heappush(self.lower, -v)
            self.size_lower += 1
            self.prune_upper()
            self.prune_lower()

        self.prune_lower()
        self.prune_upper()
        if self.lower and self.upper:
            if -self.lower[0] > self.upper[0]:
                ltop = -heapq.heappop(self.lower)
                utop = heapq.heappop(self.upper)
                heapq.heappush(self.lower, -utop)
                heapq.heappush(self.upper, ltop)
        
    def insert(self, x):
        if not self.lower:
            heapq.heappush(self.lower, -x)
            self.size_lower += 1
        else:
            self.prune_lower()
            med = -self.lower[0] if self.lower else None
            if med is None or x <= med:
                heapq.heappush(self.lower, -x)
                self.size_lower += 1
            else:
                heapq.heappush(self.upper, x)
                self.size_upper += 1
        self.rebalance()

    def remove(self, x):
        self.prune_lower()
        if self.lower:
            med = -self.lower[0]
            if x <= med:
                self.del_lower[x] += 1
                self.size_lower -= 1
            else:
                self.del_upper[x] += 1
                self.size_upper -= 1
        else:
            self.del_upper[x] += 1
            self.size_upper -= 1
        self.rebalance()

    def median(self):
        self.prune_lower()
        if not self.lower:
            return 0
        return -self.lower[0]


def main():
    io = remote(HOST, PORT)

    data = io.recvline(timeout=30)
    if not data:
        data = io.recvall(timeout=10)
    txt = data.decode(errors="ignore")
    lines = [ln for ln in txt.splitlines() if ln.strip()]
    nums_line = lines[-1]
    a = list(map(int, nums_line.split()))
    n = len(a)
    w = n // 2
    m = n - w + 1
    print(f"n={n}, w={w}, windows={m}", file=sys.stderr)

    prefix_sum = [0] * (n+1)
    prefix_xor = [0] * (n+1)
    for i in range(n):
        prefix_sum[i+1] = prefix_sum[i] + a[i]
        prefix_xor[i+1] = prefix_xor[i] ^ a[i]

    sums_out = [str(prefix_sum[i+w] - prefix_sum[i]) for i in range(m)]
    xors_out = [str(prefix_xor[i+w] ^ prefix_xor[i]) for i in range(m)]
    means_out = [str((prefix_sum[i+w] - prefix_sum[i]) // w) for i in range(m)]

    sm = SlidingMedian(w)
    for i in range(w):
        sm.insert(a[i])
    medians_out = [str(sm.median())]
    for i in range(1, m):
        sm.remove(a[i-1])
        sm.insert(a[i+w-1])
        medians_out.append(str(sm.median()))
        if (i & 0x3FFFF) == 0:
            print(f"[median] slid {i}/{m}", file=sys.stderr)

    max_val = max(a) if a else 0
    V = max(ASSUMED_MAXV, max_val)
    if V > ASSUMED_MAXV:
        print(f"[warn] observed max {V} > ASSUMED_MAXV ({ASSUMED_MAXV}); using {V}", file=sys.stderr)
    phi, divisors = precompute_phi_divisors(V)

    freq_map = [0] * (V+1)
    for i in range(w):
        val = a[i]
        if 0 <= val <= V:
            freq_map[val] += 1
        else:
            raise RuntimeError("value exceeds precomputed V")

    bucket = defaultdict(set)
    maxfreq = 0
    for val in range(V+1):
        f = freq_map[val]
        if f > 0:
            bucket[f].add(val)
            if f > maxfreq:
                maxfreq = f

    missing_heap = []
    present = [0] * (V+2)
    for v in range(V+1):
        if freq_map[v] > 0:
            present[v] = 1
    for v in range(V+1):
        if present[v] == 0:
            heapq.heappush(missing_heap, v)
    heapq.heappush(missing_heap, V+1)

    def get_mex():
        while missing_heap:
            top = missing_heap[0]
            if top <= V:
                if present[top] == 0:
                    return top
                else:
                    heapq.heappop(missing_heap)
            else:
                return top
        return V+1

    distinct_count = sum(1 for v in range(V+1) if freq_map[v] > 0)

    cnt_div = [0] * (V + 1)
    gcd_total = 0
    zeros_count = freq_map[0] if 0 <= V else 0
    sum_nonzero = 0
    for val in range(1, V+1):
        f = freq_map[val]
        if f:
            sum_nonzero += val * f
            for d in divisors[val]:
                old = cnt_div[d]
                new = old + f
                gcd_total += phi[d] * (new*(new-1)//2 - old*(old-1)//2)
                cnt_div[d] = new

    modes_out = []
    mex_out = []
    distinct_out = []
    gcds_out = []

    modes_out.append(str(max(bucket[maxfreq])) if maxfreq else "0")
    mex_out.append(str(get_mex()))
    distinct_out.append(str(distinct_count))
    gcds_out.append(str(gcd_total + zeros_count * sum_nonzero))

    for i in range(1, m):
        rem = a[i-1]
        add = a[i+w-1]

        oldf = freq_map[rem]
        if oldf > 0:
            if rem in bucket.get(oldf, set()):
                bucket[oldf].remove(rem)
                if not bucket[oldf]:
                    del bucket[oldf]
            freq_map[rem] = oldf - 1
            if oldf-1 > 0:
                bucket[oldf-1].add(rem)
            while maxfreq > 0 and maxfreq not in bucket:
                maxfreq -= 1

        if rem <= V and present[rem] == 1 and freq_map[rem] == 0:
            present[rem] = 0
            heapq.heappush(missing_heap, rem)

        if rem <= V and freq_map[rem] == 0:
            distinct_count -= 1

        if rem == 0:
            zeros_count -= 1
        else:
            sum_nonzero -= rem
            for d in divisors[rem]:
                cnt_div[d] -= 1
                gcd_total -= phi[d] * cnt_div[d]

        oldf = freq_map[add]
        if oldf > 0:
            if add in bucket.get(oldf, set()):
                bucket[oldf].remove(add)
                if not bucket[oldf]:
                    del bucket[oldf]
        freq_map[add] = oldf + 1
        bucket[oldf+1].add(add)
        if oldf+1 > maxfreq:
            maxfreq = oldf+1

        if add <= V and present[add] == 0 and freq_map[add] > 0:
            present[add] = 1

        if add <= V and oldf == 0:
            distinct_count += 1

        if add == 0:
            zeros_count += 1
        else:
            for d in divisors[add]:
                gcd_total += phi[d] * cnt_div[d]
                cnt_div[d] += 1
            sum_nonzero += add

        modes_out.append(str(max(bucket[maxfreq])) if maxfreq else "0")
        mex_out.append(str(get_mex()))
        distinct_out.append(str(distinct_count))
        gcds_out.append(str(gcd_total + zeros_count * sum_nonzero))

        if (i & 0x3FFFF) == 0:
            print(f"slid {i}/{m}", file=sys.stderr)

    for rnd in range(1, 9):
        prompt = io.recvuntil(b"!", timeout=60).decode(errors="ignore").strip()
        print(prompt, file=sys.stderr)
        if "Sums" in prompt:
            res = " ".join(sums_out)
        elif "Xors" in prompt:
            res = " ".join(xors_out)
        elif "Means" in prompt:
            res = " ".join(means_out)
        elif "Median" in prompt:
            res = " ".join(medians_out)
        elif "Modes" in prompt:
            res = " ".join(modes_out)
        elif "Mex" in prompt:
            res = " ".join(mex_out)
        elif "# of Distinct" in prompt or "Distinct" in prompt:
            res = " ".join(distinct_out)
        elif "GCD" in prompt or "pairwise GCD" in prompt:
            res = " ".join(gcds_out)
        else:
            res = " ".join(["0"] * m)
        io.sendline(res)
        print(f"sent round {rnd}", file=sys.stderr)

    final = io.recvall(timeout=30)
    try:
        print(final.decode())
    except:
        print(final)
    io.close()

if __name__ == "__main__":
    main()
