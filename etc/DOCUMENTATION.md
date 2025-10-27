# Bank Concurrency Lab Documentation

## Requirements Checklist

✅ Execute independent operations on shared data  
✅ Launch several threads at the beginning  
✅ Each thread executes many operations (10,000 per thread)  
✅ Operations randomly chosen with random parameters  
✅ The main thread waits for all threads to complete  
✅ Invariant checking after all threads finish  
✅ Operations properly synchronized with mutexes  
✅ Documentation of mutex rules and invariants  
✅ Performance testing with different thread counts  
✅ Lock granularity analysis  

## Mutex Rules and Invariants

### Mutex Strategy

**Per-Account Mutex Locking**: Each account has its own mutex lock stored in `self.locks[account_id]`.

**Invariant Protected**: The balance of each account must remain consistent. No two threads can simultaneously read or modify the same account's balance.

### Lock Acquisition Rules

1. **Single Account Access** (`get_account_balance`):
   - Acquires only the specific account's lock
   - Reads balance atomically

2. **Transfer Operations** (`transfer`):
   - Always locks in ascending order of account IDs to prevent deadlocks
   - If `from_id < to_id`: locks `from_id` then `to_id`
   - If `from_id > to_id`: locks `to_id` then `from_id`
   - Ensures atomic transfer: both withdrawal and deposit happen or neither happens

3. **Total Balance** (`get_total_balance`):
   - Acquires ALL account locks before reading any balance
   - Provides consistent snapshot of the entire bank state
   - Critical for consistency checks

### Invariants

1. **Account Balance Invariant**: Each account's balance must be non-negative
2. **Total Balance Invariant**: Sum of all account balances must equal the initial total (10,000)
3. **Atomic Transfer Invariant**: A transfer either completes fully or doesn't happen at all

## Performance Analysis

### Test Configurations

**Hardware Platform:**
- OS: Windows 10
- CPU: Standard PC
- Python: 3.x

**Test Parameters:**
- Data Size: 10 accounts × 1,000 initial balance = 10,000 total
- Operations per thread: 10,000 random transfers
- Transfer amount range: 1-100
- Thread configurations: 1, 2, 4, 8, 16 threads

### Performance Results

| Threads | Time (seconds) | Throughput (ops/sec) | Speedup vs Baseline | Status |
|---------|---------------|---------------------|---------------------|--------|
| 1       | 0.0371        | 269,594.93          | 1.00x               | PASS   |
| 2       | 0.0680        | 294,030.71          | 0.55x               | PASS   |
| 4       | 0.1347        | 296,965.53          | 0.28x               | PASS   |
| 8       | 0.2305        | 347,127.62          | 0.16x               | PASS   |
| 16      | 0.4506        | 355,110.18          | 0.08x               | PASS   |

### Observations

1. **Lock Contention**: As more threads are added, lock contention increases, causing overhead
2. **Throughput**: Maximum throughput achieved with 16 threads (355,110 ops/sec)
3. **Per-Thread Performance**: Each thread gets slower with more threads due to waiting for locks
4. **All tests passed**: All consistency checks passed for all thread configurations

### Lock Granularity Analysis

**Current approach**: Fine-grained locking (per-account mutex)
- Pros: Allows parallel transfers between different account pairs
- Cons: Lock acquisition overhead increases with thread count
- Best for: Mixed workload with low contention

**Alternative**: Coarse-grained locking (single global mutex)
- Pros: Simpler, no deadlock risk
- Cons: No parallelism - only one operation at a time
- Best for: Very small workload or simple scenarios

