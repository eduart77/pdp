class Account:
    def __init__(self, account_id, initial_balance):
        self.account_id = account_id
        self.balance = initial_balance
    
    def get_balance(self):
        return self.balance
    
    def deposit(self, amount):
        self.balance += amount
    
    def withdraw(self, amount):
        if self.balance < amount:
            raise RuntimeError("Insufficient funds")
        self.balance -= amount

