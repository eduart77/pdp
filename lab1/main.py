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


def consistency_checker(bank, num_checks, check_interval_ms):
    for i in range(num_checks):
        time.sleep(check_interval_ms / 1000.0)
        if bank.consistency_check():
            print(f"Consistency check passed. Total: {bank.get_total_balance()}")
        else:
            print("WARNING: Consistency check failed!")


def main():
    NUM_ACCOUNTS = 10
    INITIAL_BALANCE = 1000
    NUM_OPERATIONS = 20000
    MIN_AMOUNT = 1
    MAX_AMOUNT = 100
    NUM_TRANSFER_THREADS = 4
    NUM_CONSISTENCY_CHECKS = 10
    CHECK_INTERVAL_MS = 200
    
    bank = Bank(NUM_ACCOUNTS, INITIAL_BALANCE)
    
    print("Initial bank state:")
    print(f"Total balance: {bank.get_total_balance()}")
    print(f"Expected total: {bank.get_initial_total()}")
    print()
    
    assert bank.consistency_check()
    
    threads = []
    for i in range(NUM_TRANSFER_THREADS):
        thread = threading.Thread(
            target=transfer_worker,
            args=(bank, NUM_ACCOUNTS, NUM_OPERATIONS, MIN_AMOUNT, MAX_AMOUNT)
        )
        thread.start()
        threads.append(thread)
    
    checker_thread = threading.Thread(
        target=consistency_checker,
        args=(bank, NUM_CONSISTENCY_CHECKS, CHECK_INTERVAL_MS)
    )
    checker_thread.start()
    
    for thread in threads:
        thread.join()
    
    checker_thread.join()
    
    print()
    print("Final bank state:")
    print(f"Total balance: {bank.get_total_balance()}")
    print(f"Expected total: {bank.get_initial_total()}")
    
    if bank.consistency_check():
        print("SUCCESS: Final consistency check passed!")
    else:
        print("FAILURE: Final consistency check failed!")
    
    print()
    print("Individual account balances:")
    for i in range(NUM_ACCOUNTS):
        print(f"Account {i}: {bank.get_account_balance(i)}")


if __name__ == "__main__":
    main()
