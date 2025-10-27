import threading
from account import Account


class Bank:
    def __init__(self, num_accounts, initial_balance_per_account):
        self.initial_total = num_accounts * initial_balance_per_account
        self.accounts = []
        self.locks = []
        
        for i in range(num_accounts):
            self.accounts.append(Account(i, initial_balance_per_account))
            self.locks.append(threading.Lock())
    
    def get_account_balance(self, account_id):
        if account_id < 0 or account_id >= len(self.accounts):
            return -1
        with self.locks[account_id]:
            return self.accounts[account_id].get_balance() 
    
    def transfer(self, from_id, to_id, amount):
        if from_id == to_id:
            return False
        if from_id < 0 or from_id >= len(self.accounts) or to_id < 0 or to_id >= len(self.accounts):
            return False
        
        if from_id < to_id:
            lock1, lock2 = self.locks[from_id], self.locks[to_id]
        else:
            lock1, lock2 = self.locks[to_id], self.locks[from_id]
        
        with lock1, lock2:
            if self.accounts[from_id].get_balance() < amount:
                return False
            self.accounts[from_id].withdraw(amount)
            self.accounts[to_id].deposit(amount)
            return True
    
    def get_total_balance(self):
        for lock in self.locks:
            lock.acquire()
        total = sum(acc.get_balance() for acc in self.accounts)
        for lock in self.locks:
            lock.release()
        return total
    
    def consistency_check(self):
        return self.get_total_balance() == self.initial_total
    
    def get_initial_total(self):
        return self.initial_total
