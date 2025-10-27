#ifndef BANK_H
#define BANK_H

#include <vector>
#include <memory>
#include <mutex>
#include "account.h"

class Bank {
private:
    std::vector<std::unique_ptr<Account>> accounts;
    mutable std::vector<std::unique_ptr<std::mutex>> account_mutexes;
    const int initial_total;
    
public:
    Bank(int num_accounts, int initial_balance_per_account);
    
    int get_account_balance(int account_id);
    bool transfer(int from_id, int to_id, int amount);
    int get_total_balance() const;
    bool consistency_check() const;
    int get_num_accounts() const;
    int get_initial_total() const;
    
    // Helper function to get mutexes for deadlock prevention
    std::mutex& get_mutex(int account_id);
};

#endif // BANK_H

