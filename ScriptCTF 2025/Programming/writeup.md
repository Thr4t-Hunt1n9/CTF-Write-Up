### Intro
- This week my team played scriptCTF, and here is the writeup for `Programming/Back From Where` (The remaining 3 chall first have been officially writeup by the organizers)

    - [Link for official writeup](https://github.com/Thr4t-Hunt1n9/scriptCTF2025-OfficialWriteups/tree/main/Programming)


![alt text](/ScriptCTF%202025/Programming/imgs/image.png)

### Description
```
On a grid, you begin on the top left, moving right and down until reaching the bottom right, multiplying every number you encounter on the path. Find the maximum number of trailing zeroes for every node. Note: You might want to check out BackFromBrazil from n00bzctf 2024.

(if you have any questions about input/output, plz open a ticket)
```

- [Source](/ScriptCTF%202025/Programming/server.py)

![alt text](/ScriptCTF%202025/Programming/imgs/image-1.png)

### TL;DR

- In this CTF challenge, we connect to receive a `100x100` grid of integers. The task is to compute, for each cell `(i,j)`, the maximum number of trailing zeros in the product of numbers along any path from `(0,0)` to `(i,j)`, moving only right or down. Trailing zeros are determined by the minimum of the counts of factors 2 and 5 in the product. We use dynamic programming (DP) to track the maximum count of 2s for each possible count of 5s up to a cell, precomputing factor counts per cell. The solution outputs a `100x100` matrix of these maximum trailing zero counts to get the flag

### Analysis

- The challenge is inspired by [BackFromBrazil](https://moormaster.github.io/CtfWriteups/backfrombrazil.html) from `n00bzCTF 2024`, where the goal is to maximize trailing zeros in path products on a grid with restricted movements (right or down). - The grid is `100x100`, with each cell containing a number that's either a random multiple of 2 (even) or 5 (multiple of 5), generated as `random.randint(1,696)*2` or `*5`.
- Trailing zeros in a number's decimal representation come from factors of 10, which are pairs of 2 and 5 in its prime factorization. Since there are usually more 2s than 5s, the count is typically limited by the number of 5s, but we must compute `min(count_2, count_5)` for the product.
- A naive approach of enumerating all paths is impossible due to the exponential number of paths (up to `C(198,99) ~ 10^59)`. Instead, we use DP to efficiently compute the best path to each cell.
- Key insights:

    - Precompute for each cell (i,j): `twos[i][j]` (exponent of 2) and `fives[i][j]` (exponent of 5) by repeatedly dividing by 2 or 5.
    - For paths to (i,j), the total `count_5` is the sum of fives along the path, and total `count_2` is the sum of twos.
    - To maximize `min(total_2, total_5)`, we track the maximum total_2 for each possible total_5 value at each cell.
    - DP state: `dp[i][j][k] = maximum total_2` achievable with exactly k total_5 to reach `(i,j)`.
    - Transitions: From left (j-1) or up (i-1), add the current cell's twos and fives.
    - Since max k (total_5) per path is bounded (e.g., <1000 given grid size and numbers up to ~3500), we cap it at 1000 to avoid overflow.
    - For each cell, iterate over possible k and take max over k of `min(dp[i][j][k], k)` as the max trailing zeros.
    - Time complexity: `O(N^2 * MAX_S) ~ 100^2 * 1000 = 10^7`, efficient enough `(<20s limit)`.

- The server runs our output against a reference solution [Script](/ScriptCTF%202025/Programming/solve.py) and checks for equality, with a time limit.

### Solution

- I use `pwntools` to connect, read the grid, compute the DP solution, and submit the output matrix. The process involves:

- Preparation:

    - Connect to `nc play.scriptsorcerers.xyz PORT` and read the `100x100` grid.


- Helper Functions:

    - Define `count_twos(num)` and `count_fives(num)` to compute the exponents of 2 and 5 in each cell’s value by iterative division.


- DP Implementation:

    - Initialize a 3D DP array `dp[i][j][k]` with a sentinel value (e.g., -1) for unreachable states.
    Set the base case `dp[0][0][fives[0][0]] = twos[0][0]`.
    - For each cell `(i,j)`, update `dp[i][j][ns]` by considering transitions from `(i-1,j)` or `(i,j-1)`, where `ns = s + fives[i][j]` and the new `total_2 = dp[prev][prev_s] + twos[i][j]`.
    Cap ns at `MAX_S = 1000` to manage array bounds.

- Compute Answer:

    - For each cell, iterate over `k` from 0 to `MAX_S`, and set `ans[i][j]` to the maximum of `min(dp[i][j][k], k)` where `dp[i][j][k] != INF`.


- Submit Output:

    - Send each row of the `ans` matrix as a space-separated string via the connection.

    ![alt text](/ScriptCTF%202025/Programming/imgs/image-2.png)

    - Flag: `scriptCTF{d0nt_u_ju5t_!@ve_z%ro3s???_31fd64473d91}`


### My solve for another chal (have official wu)

- [Windows To Infinity](/ScriptCTF%202025/Programming/Windows%20To%20Infinity.py)