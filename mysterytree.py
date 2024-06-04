import sys

# Example binary matrix
matrix = [
    [1, 0, 0, 0, 0],
    [0, 1, 0, 0, 1],
    [1, 1, 0, 0, 0],
    [0, 0, 0, 0, 0],
    [1, 0, 0, 1, 0]
]

s = len(matrix)  # Number of rows
t = len(matrix[0])  # Number of columns

# Precompute maximum consecutive 1s for each position to 0th row
max_consecutive_ones = [[0] * t for _ in range(s)]

# Function to calculate maximum consecutive 1s from position (i, j) to 0th row
def calculate_max_consecutive_ones():
    # Calculate for each row from bottom to top
    for i in range(s - 1, -1, -1):
        for j in range(t):
            if matrix[i][j] == 1:
                if i == s - 1:
                    max_consecutive_ones[i][j] = 1
                else:
                    max_consecutive_ones[i][j] = max_consecutive_ones[i + 1][j] + 1
            else:
                max_consecutive_ones[i][j] = 0

calculate_max_consecutive_ones()

# van Emde Boas tree implementation
class VanEmdeBoasTree:
    def __init__(self, universe_size):
        self.universe_size = universe_size
        self.min = None
        self.max = None
        self.clusters = {}
        self.summary = None

    def insert(self, x):
        if self.min is None:
            self.min = x
            self.max = x
        else:
            if x < self.min:
                x, self.min = self.min, x
            if x > self.max:
                self.max = x

            if self.universe_size > 2:
                high = self.high(x)
                low = self.low(x)
                if high not in self.clusters:
                    self.clusters[high] = VanEmdeBoasTree(self.sqrt_universe_size())
                self.clusters[high].insert(low)
                if self.summary is None:
                    self.summary = VanEmdeBoasTree(self.sqrt_universe_size())
                self.summary.insert(high)

    def member(self, x):
        if x == self.min or x == self.max:
            return True
        elif self.universe_size == 2:
            return False
        else:
            high = self.high(x)
            low = self.low(x)
            if high in self.clusters and self.clusters[high].member(low):
                return True
            else:
                return False

    def successor(self, x):
        if x is None:
            return None
        if self.universe_size == 2:
            if x == 0 and self.max == 1:
                return 1
            else:
                return None
        elif self.min is not None and x < self.min:
            return self.min
        else:
            high = self.high(x)
            low = self.low(x)
            max_low = None
            if high in self.clusters:
                max_low = self.clusters[high].max
            if max_low is not None and low < max_low:
                offset = self.clusters[high].successor(low)
                return self.index(high, offset)
            else:
                succ_cluster = None
                if self.summary is not None:
                    succ_cluster = self.summary.successor(high)
                if succ_cluster is not None:
                    offset = self.clusters[succ_cluster].min
                    return self.index(succ_cluster, offset)
                else:
                    return None

    def sqrt_universe_size(self):
        return 2 ** ((self.universe_size.bit_length() + 1) // 2)

    def high(self, x):
        return x // self.sqrt_universe_size()

    def low(self, x):
        return x % self.sqrt_universe_size()

    def index(self, high, low):
        return high * self.sqrt_universe_size() + low

# Function to find the maximum path with the most 1s using dynamic programming
def find_maximum_path(vEB_tree, i, j, dp, path):
    # Base case: Reach the 0th row
    if i == 0:
        return matrix[i][j], [(i, j)]

    if dp[i][j] != -1:
        return dp[i][j], path[i][j]

    # Recursive case
    current_row = i - 1
    max_ones = 0
    best_path = []

    # Check the three possible moves
    candidates = [
        (current_row, j - 1),  # Left-up move
        (current_row, j),      # Up move
        (current_row, j + 1)   # Right-up move
    ]

    for row, col in candidates:
        if 0 <= col < t:
            consecutive_ones = matrix[i][j]
            score, p = find_maximum_path(vEB_tree, row, col, dp, path)
            if consecutive_ones + score > max_ones:
                max_ones = consecutive_ones + score
                best_path = [(i, j)] + p

    dp[i][j] = max_ones
    path[i][j] = best_path
    return dp[i][j], path[i][j]

# Initialize the van Emde Boas tree for the column indices
vEB_tree = VanEmdeBoasTree(t)

# Insert all column indices into the van Emde Boas tree
for j in range(t):
    vEB_tree.insert(j)

# Start the recursion from all positions in the last row
max_ones = 0
best_path = []
dp = [[-1] * t for _ in range(s)]
path = [[[] for _ in range(t)] for _ in range(s)]
for j in range(t):
    for i in range(s):
        score, p = find_maximum_path(vEB_tree, s - 1, j, dp, path)
        if score > max_ones:
            max_ones = score
            best_path = p

# Output the results
print(f"Maximum number of 1s: {max_ones}")
print("Best path:")
for row, col in best_path:
    print(f"({row}, {col}) -> ", end="")
print("0")
