# Lab 1: "Non-cooperative" Multithreading - Top 15 Questions (Bank Accounts)

## Question 1: Deadlock Prevention in Bank Transfers
In the Bank Accounts problem, you need to ensure transfers between accounts don't deadlock. One thread wants to transfer from account A to B, another wants to transfer from B to A. Explain:
- Why deadlock can occur in this scenario
- What locking strategy prevents deadlocks in the transfer operation
- Show the specific ordering rule you would use and why

### Answer:
**Why deadlock occurs:**
When Thread 1 locks A then tries to lock B, while Thread 2 locks B then tries to lock A, both threads wait indefinitely for locks the other holds.

**Locking strategy:**
Always acquire locks in a consistent order, independent of the transfer direction.

**Specific rule (from bank.py implementation):**
```python
if from_id < to_id:
    lock1, lock2 = self.locks[from_id], self.locks[to_id]
else:
    lock1, lock2 = self.locks[to_id], self.locks[from_id]

with lock1, lock2:
    # perform transfer
```

Always lock the account with the smaller ID first, then the larger ID. This constant ordering avoids circular waiting.

## Question 2: Fine-grained Locking vs. Coarse-grained Locking
For the Bank Accounts problem, compare two approaches:
- Approach A: One global mutex protecting all account operations
- Approach B: Per-account mutexes

Discuss:
- When would each approach perform better?
- Which provides more parallelism?
- What are the trade-offs in terms of complexity and performance?

### Answer:

**Performance comparison:**
- **Coarse-grained (A)**: Better for single-threaded environments; very low contention but zero parallelism
- **Fine-grained (B)**: Better for multi-threaded with independent work; allows parallel transfers between different account pairs

**Parallelism:**
Approach B provides more parallelism because:
- Transfer A→B and C→D can execute concurrently
- Only transfers involving the same accounts block each other

**Trade-offs:**

| Aspect | Global Mutex (A) | Per-Account Mutex (B) |
|--------|-----------------|---------------------|
| **Complexity** | Low - single lock | Higher - must manage lock order |
| **Deadlock Risk** | None | Must prevent with ordering |
| **Parallelism** | None | High for disjoint operations |
| **Lock Overhead** | Minimal | Per-lock acquisition cost |
| **Contention** | High under load | Lower with independent work |

The implementation uses Approach B for scalability at the cost of complexity.

## Question 3: Account Balance Invariant
The bank must maintain the invariant that the total balance across all accounts remains constant. Explain:
- What specific invariant must be preserved during concurrent transfers?
- Why can this invariant be violated without proper synchronization?
- How do transfers maintain this invariant?

### Answer:

**Invariant:**
The sum of all account balances must equal the initial total:
```
Σ(balance[account]) = initial_total
```
This ensures money is neither created nor destroyed—only moved between accounts.

**Why it can be violated:**
- Without locks, transfers might update only one account
- Race conditions between reading and writing balances can cause lost updates
- Partial transfers (withdraw succeeds, deposit fails) corrupt the total

**How transfers maintain it:**
Each transfer is atomic: it decreases one account by X and increases another by X:
- Lock both accounts to prevent concurrent modifications
- Verify sufficient funds before withdrawing
- Both operations execute or neither does (atomicity)

## Question 4: Lock Acquisition Order for Multiple Accounts
Explain the critical importance of acquiring locks in a consistent order:
- Show how inconsistent ordering leads to deadlocks with multiple concurrent transfers
- Demonstrate why the ordering rule works (locking by account ID)
- Give a concrete example of two transfers that would deadlock without ordering

### Answer:

**Deadlock scenario without ordering:**
Thread 1: Transfer from A (ID=0) → B (ID=1) → locks A then tries to lock B
Thread 2: Transfer from B (ID=1) → A (ID=0) → locks B then tries to lock A
Result: Circular wait → deadlock

**With consistent ordering (smaller ID first):**
Thread 1: Locks A (ID=0) then B (ID=1) → completes
Thread 2: Waits for A (ID=0) to be released, then locks it → completes

All threads acquire locks in the same order (0 → 1 → 2...), preventing circular dependencies.

**Example deadlock:**
```
Initial: Account 0 = 1000, Account 1 = 1000
Thread 1: Transfer 100 from account 0 → account 1
Thread 2: Transfer 100 from account 1 → account 0

Without ordering:
  Thread 1 locks 0, tries to lock 1
  Thread 2 locks 1, tries to lock 0
  Both block forever

With ordering (0 always before 1):
  Thread 1 locks 0, then 1 → completes
  Thread 2 waits for 0, gets 0, then 1 → completes
```

## Question 5: Parallelism in Bank Transfers
The requirement states: "Two transactions involving distinct accounts must be able to proceed independently."
- Which transfers CAN execute in parallel with your locking strategy?
- Which transfers MUST be serialized?
- Calculate the theoretical speedup with perfect parallelism

### Answer:

**Can execute in parallel:**
- Transfer from account 0 → account 1 while transfer from account 2 → account 3
- Transfer from account 0 → account 5 while transfer from account 1 → account 8
- Any transfers involving completely disjoint sets of accounts

These lock different accounts, so no contention occurs.

**Must be serialized:**
- Transfer from account 0 → account 1 while transfer from account 1 → account 2
- Transfer from account 3 → account 5 while transfer from account 5 → account 3
- Any transfers where at least one account overlaps

These compete for the same locks, requiring sequential execution.

**Theoretical speedup:**
With 10 accounts and random transfers:
- Conflict probability ≈ 19% (from Question 14)
- ~81% of transfers can run in parallel
- With 4 threads: up to ~3.2x speedup (limited by conflicts)
- Scaling decreases as thread count increases due to contention

## Question 6: Consistency Check Implementation
Consistency checks must run periodically while transfers execute. Explain:
- What race conditions exist between transfers and consistency checks?
- How should consistency checks be implemented to avoid incorrect failures?
- Show the complete locking strategy for get_total_balance()

### Answer:

**Race conditions:**
Without proper locking:
```
Consistency check reads account 0 balance = 1000
Transfer 0 → 1 executes: 0 now 900, 1 now 1100
Consistency check reads account 1 balance = 1100
Check calculates: 1000 + 1100 = 2100 (should be 2000)
Result: Incorrect failure despite valid state
```

**Correct implementation:**
From bank.py:
```python
def get_total_balance(self):
    for lock in self.locks:
        lock.acquire()  # Lock all accounts first
    total = sum(acc.get_balance() for acc in self.accounts)
    for lock in self.locks:
        lock.release()  # Release all
    return total
```

Acquire ALL locks before reading ANY balance to create a consistent snapshot.

**Why it works:**
- Prevents any transfers from modifying balances during the check
- Creates a point-in-time view of the entire bank
- Guarantees sums are calculated on consistent data

## Question 7: Transfer Atomicity
The transfer operation must be atomic: "happen completely or not at all."
- Show how locks ensure atomicity in the transfer operation
- What happens if there are insufficient funds in the source account?
- Demonstrate that no partial transfers can occur

### Answer:

**Atomicity with locks:**
From bank.py implementation:
```python
def transfer(self, from_id, to_id, amount):
    # ... validation ...
    
    if from_id < to_id:
        lock1, lock2 = self.locks[from_id], self.locks[to_id]
    else:
        lock1, lock2 = self.locks[to_id], self.locks[from_id]
    
    with lock1, lock2:  # Atomic region
        if self.accounts[from_id].get_balance() < amount:
            return False  # Abort before ANY changes
        self.accounts[from_id].withdraw(amount)   # Both operations
        self.accounts[to_id].deposit(amount)      # are atomic
        return True
```

**Insufficient funds:**
- Check happens BEFORE any modifications
- Return False without changing any balances
- No partial withdraw or deposit can occur

**Partial transfer prevention:**
With both locks held for the entire critical section:
- No other thread can observe intermediate states
- If a crash occurs during the operation, Python's exception handling releases locks
- The withdraw and deposit execute as a single indivisible unit

## Question 8: Performance Impact of Thread Count
As the number of threads increases from 1 to 16, performance changes significantly. Based on the test results:
- Why does total execution time increase with more threads?
- What is lock contention and how does it affect performance?
- Explain the relationship between thread count and throughput

### Answer:

**Performance degradation:**
From performance_test.py results:
- 1 thread: 0.0371s
- 4 threads: 0.1347s (3.6x slower)
- 16 threads: 0.4506s (12x slower)

**Why time increases:**
1. **Lock contention**: More threads compete for the same locks
2. **Context switching**: Frequent thread switches when waiting for locks
3. **Cache coherence**: Shared locks cause cache invalidations
4. **CPU starvation**: Threads spend more time waiting than working

**Lock contention defined:**
How often threads must wait for locks instead of proceeding immediately.

**Thread count vs throughput:**
Throughput initially increases (more parallelism), then plateaus or decreases:
- 1 thread: 269,595 ops/sec
- 16 threads: 355,110 ops/sec (only 1.3x better despite 16x threads)

Diminishing returns occur because:
- Conflicts become more frequent (19% of operations with 10 accounts)
- Lock wait time dominates execution time
- Perfect parallelism is not achievable

## Question 9: Thread Safety of Balance Queries
Consider the `get_account_balance()` method:
- Is it thread-safe? Why or why not?
- What happens if multiple threads query the same account concurrently?
- Could you optimize reads differently than writes?

### Answer:

**Thread safety:**
Yes, it's thread-safe from bank.py:
```python
def get_account_balance(self, account_id):
    if account_id < 0 or account_id >= len(self.accounts):
        return -1
    with self.locks[account_id]:
        return self.accounts[account_id].get_balance()
```

The lock ensures no concurrent modification during the read.

**Concurrent queries:**
Without locks:
```
Thread 1 reads balance during transfer
Thread 2 reads balance mid-update
Result: Corrupted or inconsistent balance values
```

With locks:
- Each read acquires the account's lock
- Queues requests if the lock is held
- Serializes access but guarantees correctness

**Optimization with read-write locks:**
- Use `threading.RLock` or `RWLock`
- Multiple readers can proceed concurrently
- Writer has exclusive access
- Better for read-heavy workloads

For the bank (mostly writes), regular mutexes are sufficient.

## Question 10: Starting Balance Initialization
The bank initializes with a fixed starting balance per account. How is the initial total computed and maintained?
- Show how the initial total is calculated
- Why must this value remain constant?
- How is it used in consistency checks?

### Answer:

**Initial total calculation:**
From bank.py constructor:
```python
def __init__(self, num_accounts, initial_balance_per_account):
    self.initial_total = num_accounts * initial_balance_per_account
    self.accounts = []
    self.locks = []
    
    for i in range(num_accounts):
        self.accounts.append(Account(i, initial_balance_per_account))
        self.locks.append(threading.Lock())
```

**Why it's constant:**
- Set once during initialization
- Never modified afterward (read-only)
- Serves as the ground truth for invariant checking

**Consistency check usage:**
From bank.py:
```python
def consistency_check(self):
    return self.get_total_balance() == self.initial_total
```

The check verifies:
```
current_total = Σ(balance[account])
invariant_holds = (current_total == initial_total)
```

This detects any money creation or destruction bugs.

## Question 11: Invalid Transfer Scenarios
The bank implementation handles several edge cases. Identify and explain:
- What happens when transferring from an account to itself?
- How are out-of-bounds account IDs handled?
- What prevents transferring negative amounts?

### Answer:

**Self-transfer prevention:**
```python
if from_id == to_id:
    return False
```
Transfers to the same account are immediately rejected—no lock acquisition needed.

**Out-of-bounds account IDs:**
```python
if from_id < 0 or from_id >= len(self.accounts) or to_id < 0 or to_id >= len(self.accounts):
    return False
```
Invalid account IDs return False before any operations.

**Negative amounts:**
Not explicitly checked in the current implementation, but:
- `random.randint(1, 100)` in main.py ensures amounts are positive
- Withdraw/deposit operations handle negative values (they would work, but it's semantically wrong)

**Additional validations not shown:**
- Zero amount transfers are allowed (wasteful but valid)
- Large amounts that cause overflow are not checked

## Question 12: Lock Hold Time Optimization
The `get_total_balance()` method holds ALL locks during the entire summation. Analyze:
- What is the lock hold time?
- Could we optimize this further?
- What are the trade-offs of different approaches?

### Answer:

**Current lock hold time:**
From bank.py:
```python
def get_total_balance(self):
    for lock in self.locks:
        lock.acquire()         # Starts holding all locks
    total = sum(acc.get_balance() for acc in self.accounts)  # Hold time
    for lock in self.locks:
        lock.release()         # Releases all locks
    return total
```

Lock hold time = time to sum N account balances (O(N) operation).

**Optimization approach:**
Quickly copy values, then release locks:

```python
def get_total_balance(self):
    # Acquire all locks
    for lock in self.locks:
        lock.acquire()
    
    # Copy all balances to local variables (fast)
    balances = [acc.get_balance() for acc in self.accounts]
    
    # Release all locks immediately
    for lock in self.locks:
        lock.release()
    
    # Compute sum without holding locks
    return sum(balances)
```

**Trade-offs:**

| Approach | Lock Hold Time | Complexity | Correctness |
|----------|---------------|------------|-------------|
| Current | O(N) | Low | Correct |
| Optimization | O(N) but faster | Higher | Correct |
| No locks | Instant | Low | WRONG |

**Why the optimization works:**
Copies are atomic (simple integer assignment), while summation is pure computation.

## Question 13: Failure Scenarios and Partial Updates
Consider what happens if an error occurs during a transfer:
- What happens if withdrawal succeeds but deposit fails?
- How does Python's exception handling interact with locks?
- Can the system reach an inconsistent state?

### Answer:

**Exception handling in Python:**
Python's `with` statement guarantees lock release even on exceptions:

```python
with lock1, lock2:  # Enters lock
    self.accounts[from_id].withdraw(amount)  # If this fails...
    self.accounts[to_id].deposit(amount)     # ...this won't execute
# Locks are automatically released here by __exit__
```

**Withdrawal succeeds, deposit fails:**
This scenario shouldn't occur because:
- Both operations are simple integer addition/subtraction
- No external dependencies (no network, file I/O, etc.)
- If it did fail, the exception propagates and locks release

**Partial update impossibility:**
Due to atomicity:
- Both operations are in the same critical section
- No external observer can see partial results
- Locks ensure no concurrent access

**Potential issue (not in current implementation):**
If `deposit()` raised an exception, the transfer would fail, locks would release, but the withdraw already occurred. The current implementation is safe because both are simple operations.

## Question 14: Random Operation Generation and Contention
The implementation uses random source/destination selection for transfers. Analyze:
- Why is randomness crucial for testing this system?
- What percentage of transfers will contend for locks with 10 accounts?
- How does account count affect contention?

### Answer:

**Why randomness matters:**
1. **Exploration**: Tests unpredictable interleavings
2. **Race condition exposure**: Timing-dependent bugs appear more reliably
3. **Realistic workload**: Simulates actual unpredictable access patterns
4. **Stress testing**: Increases chances of contention

From main.py:
```python
from_id = random.randint(0, num_accounts - 1)
to_id = random.randint(0, num_accounts - 1)
while from_id == to_id:
    to_id = random.randint(0, num_accounts - 1)
```

**Contention calculation:**
With 10 accounts, 90 valid transfer pairs:
- Two random transfers conflict if they share any account
- P(no conflict) = probability of selecting 4 distinct accounts = (90/90) × (72/89) ≈ 0.81
- P(conflict) = 1 - 0.81 = 0.19 = 19%

**Account count impact:**
| Accounts | Total Pairs | Conflict Rate | Parallelism |
|----------|-------------|---------------|-------------|
| 10 | 90 | ~19% | ~81% |
| 50 | 2,450 | ~4% | ~96% |
| 100 | 9,900 | ~2% | ~98% |

More accounts dramatically improve parallelism potential.

## Question 15: Complete Implementation Verification
Provide a complete verification that your implementation meets all requirements:
- Evidence of "many operations" per thread
- Proof of invariant preservation
- Documentation of mutex usage
- Performance analysis with different thread counts

### Answer:

**Evidence of many operations:**
From main.py:
- 10,000 operations per thread
- 4 transfer threads = 40,000 total transfers
- Rationale: Sufficient volume to stress test synchronization and expose race conditions

**Invariant preservation:**
From main.py and performance_test.py:
1. **Initial check** (line 44): `assert bank.consistency_check()`
2. **Periodic checks** (lines 19-24): 10 checks during execution
3. **Final check** (lines 71-74): Verification after all threads complete

All tests passed across all thread configurations (1, 2, 4, 8, 16).

**Mutex usage documentation:**
From DOCUMENTATION.md:
- **Per-account locks**: `self.locks[account_id]` protects each account balance
- **Consistent ordering**: Always lock smaller ID first
- **Atomicity**: Transfer locks both accounts for the entire operation
- **Invariant protection**: `get_total_balance()` locks all accounts

**Performance results:**
From DOCUMENTATION.md:

| Threads | Time (s) | Throughput (ops/s) | Speedup | Status |
|---------|----------|-------------------|---------|--------|
| 1 | 0.0371 | 269,595 | 1.00x | PASS |
| 4 | 0.1347 | 296,966 | 0.28x | PASS |
| 16 | 0.4506 | 355,110 | 0.08x | PASS |

**Interpretation:**
- Throughput increases but plateaus (diminishing returns)
- Per-thread performance degrades (contention overhead)
- Optimal: 2-4 threads for this workload
- System is memory-bound, not CPU-bound
- All consistency checks pass across all configurations
