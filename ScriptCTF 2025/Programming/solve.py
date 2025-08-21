from pwn import *

def count_twos(num):
    count = 0
    while num % 2 == 0 and num > 0:
        num //= 2
        count += 1
    return count

def count_fives(num):
    count = 0
    while num % 5 == 0 and num > 0:
        num //= 5
        count += 1
    return count

r = remote('play.scriptsorcerers.xyz', 10294)

grid = []
for _ in range(100):
    line = r.recvline().decode().strip()
    if line:
        row = list(map(int, line.split()))
        grid.append(row)

n = 100
twos = [[count_twos(grid[i][j]) for j in range(n)] for i in range(n)]
fives = [[count_fives(grid[i][j]) for j in range(n)] for i in range(n)]

MAX_S = 1000
INF = -1
dp = [[[INF for _ in range(MAX_S + 1)] for _ in range(n)] for _ in range(n)]

dp[0][0][fives[0][0]] = twos[0][0]

for i in range(n):
    for j in range(n):
        if i == 0 and j == 0:
            continue
        # From up
        if i > 0:
            for s in range(MAX_S + 1):
                if dp[i-1][j][s] != INF:
                    ns = s + fives[i][j]
                    if ns > MAX_S:
                        continue
                    n2 = dp[i-1][j][s] + twos[i][j]
                    dp[i][j][ns] = max(dp[i][j][ns], n2)
        # From left
        if j > 0:
            for s in range(MAX_S + 1):
                if dp[i][j-1][s] != INF:
                    ns = s + fives[i][j]
                    if ns > MAX_S:
                        continue
                    n2 = dp[i][j-1][s] + twos[i][j]
                    dp[i][j][ns] = max(dp[i][j][ns], n2)

ans = [[0 for _ in range(n)] for _ in range(n)]
for i in range(n):
    for j in range(n):
        max_zeros = 0
        for s in range(MAX_S + 1):
            if dp[i][j][s] != INF:
                zeros = min(dp[i][j][s], s)
                max_zeros = max(max_zeros, zeros)
        ans[i][j] = max_zeros

for i in range(n):
    r.sendline(' '.join(map(str, ans[i])))

r.interactive()