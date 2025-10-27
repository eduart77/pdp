import threading
import random
import time
from bank import Bank


def transfer_worker(bank, num_accounts, num_operations, min_amount, max_amount):
    for i in range(num_operations):
        from_id = random.randint(0, num_accounts - 1)
        to_id = random.randint(0, num_accounts - 1)
        while from_id == to_id:
            to_id = random.randint(0, num_accounts - 1)
        amount = random.randint(min_amount, max_amount)
        bank.transfer(from_id, to_id, amount)


def test_performance(num_threads, num_accounts, num_operations_per_thread):
    bank = Bank(num_accounts, 1000)
    
    print(f"\nTesting with {num_threads} threads...")
    print(f"Operations per thread: {num_operations_per_thread}")
    print(f"Total operations: {num_threads * num_operations_per_thread}")
    
    threads = []
    start_time = time.time()
    
    for i in range(num_threads):
        thread = threading.Thread(
            target=transfer_worker,
            args=(bank, num_accounts, num_operations_per_thread, 1, 100)
        )
        thread.start()
        threads.append(thread)
    
    for thread in threads:
        thread.join()
    
    end_time = time.time()
    elapsed = end_time - start_time
    
    consistent = bank.consistency_check()
    
    print(f"Time consumed: {elapsed:.4f} seconds")
    print(f"Throughput: {num_threads * num_operations_per_thread / elapsed:.2f} ops/sec")
    print(f"Consistency check: {'PASSED' if consistent else 'FAILED'}")
    print(f"Total balance: {bank.get_total_balance()}")
    
    return elapsed, consistent


def main():
    print("=" * 60)
    print("PERFORMANCE TEST RESULTS")
    print("=" * 60)
    print("\nTest Configuration:")
    print("- Accounts: 10")
    print("- Initial balance per account: 1,000")
    print("- Operations per thread: 10,000")
    print("- Transfer amount range: 1-100")
    
    results = []
    
    # Test different thread counts
    for num_threads in [1, 2, 4, 8, 16]:
        elapsed, consistent = test_performance(num_threads, 10, 10000)
        results.append({
            'threads': num_threads,
            'time': elapsed,
            'consistent': consistent
        })
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"{'Threads':<10} {'Time (s)':<12} {'Throughput (ops/s)':<20} {'Status':<10}")
    print("-" * 60)
    
    for r in results:
        throughput = (r['threads'] * 10000) / r['time']
        status = "PASS" if r['consistent'] else "FAIL"
        print(f"{r['threads']:<10} {r['time']:<12.4f} {throughput:<20.2f} {status:<10}")
    
    print("\nAnalysis:")
    baseline = results[0]['time']
    for r in results:
        speedup = baseline / r['time']
        print(f"{r['threads']} threads: {speedup:.2f}x speedup vs baseline")


if __name__ == "__main__":
    main()

