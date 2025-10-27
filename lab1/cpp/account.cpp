#include "account.h"
#include <stdexcept>

Account::Account(int id, int initial_balance) : account_id(id), balance(initial_balance) {}

int Account::get_balance() const {
    return balance;
}

int Account::get_id() const {
    return account_id;
}

void Account::deposit(int amount) {
    if (amount < 0) {
        throw std::invalid_argument("Deposit amount must be positive");
    }
    balance += amount;
}

void Account::withdraw(int amount) {
    if (amount < 0) {
        throw std::invalid_argument("Withdraw amount must be positive");
    }
    if (balance < amount) {
        throw std::runtime_error("Insufficient funds");
    }
    balance -= amount;
}

