#include "bank.h"
#include <algorithm>
#include <iostream>

Bank::Bank(int num_accounts, int initial_balance_per_account) 
    : initial_total(num_accounts * initial_balance_per_account) {
    
    accounts.resize(num_accounts);
    account_mutexes.resize(num_accounts);
    
    for (int i = 0; i < num_accounts; i++) {
        accounts[i] = std::make_unique<Account>(i, initial_balance_per_account);
        account_mutexes[i] = std::make_unique<std::mutex>();
    }
}

int Bank::get_account_balance(int account_id) {
    if (account_id < 0 || account_id >= static_cast<int>(accounts.size())) {
        return -1;
    }
    std::lock_guard<std::mutex> lock(*account_mutexes[account_id]);
    return accounts[account_id]->get_balance();
}

std::mutex& Bank::get_mutex(int account_id) {
    return *account_mutexes[account_id];
}

bool Bank::transfer(int from_id, int to_id, int amount) {
    if (from_id == to_id) {
        return false;
    }
    
    if (from_id < 0 || from_id >= static_cast<int>(accounts.size()) ||
        to_id < 0 || to_id >= static_cast<int>(accounts.size())) {
        return false;
    }
    
    // Deadlock prevention: always lock in order of account_id
    if (from_id < to_id) {
        std::lock_guard<std::mutex> lock1(*account_mutexes[from_id]);
        std::lock_guard<std::mutex> lock2(*account_mutexes[to_id]);
        
        try {
            accounts[from_id]->withdraw(amount);
            accounts[to_id]->deposit(amount);
            return true;
        } catch (const std::exception&) {
            // Rollback
            accounts[from_id]->deposit(amount);
            return false;
        }
    } else {
        std::lock_guard<std::mutex> lock1(*account_mutexes[to_id]);
        std::lock_guard<std::mutex> lock2(*account_mutexes[from_id]);
        
        try {
            accounts[from_id]->withdraw(amount);
            accounts[to_id]->deposit(amount);
            return true;
        } catch (const std::exception&) {
            // Rollback
            accounts[from_id]->deposit(amount);
            return false;
        }
    }
}

int Bank::get_total_balance() const {
    int total = 0;
    // Lock all accounts to get a consistent snapshot
    std::vector<std::lock_guard<std::mutex>> locks;
    for (auto& mtx : account_mutexes) {
        locks.emplace_back(*mtx);
    }
    
    for (const auto& account : accounts) {
        total += account->get_balance();
    }
    
    return total;
}

bool Bank::consistency_check() const {
    int current_total = get_total_balance();
    return current_total == initial_total;
}

int Bank::get_num_accounts() const {
    return accounts.size();
}

int Bank::get_initial_total() const {
    return initial_total;
}

