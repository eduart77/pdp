#ifndef ACCOUNT_H
#define ACCOUNT_H

class Account {
private:
    int balance;
    int account_id;
    
public:
    Account(int id, int initial_balance);
    
    int get_balance() const;
    int get_id() const;
    
    void deposit(int amount);
    void withdraw(int amount);
};

#endif // ACCOUNT_H

