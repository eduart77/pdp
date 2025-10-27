#include "bank.h"
#include <thread>
#include <vector>
#include <random>
#include <iostream>
#include <chrono>
#include <cassert>

// Thread function to perform random transfers
void transfer_worker(Bank& bank, int num_accounts, int num_operations, int min_amount, int max_amount) {
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_int_distribution<> account_dist(0, num_accounts - 1);
    std::uniform_int_distribution<> amount_dist(min_amount, max_amount);
    
    for (int i = 0; i < num_operations; i++) {
        int from = account_dist(gen);
        int to = account_dist(gen);
        
        // Make sure from and to are different
        while (from == to) {
            to = account_dist(gen);
        }
        
        int amount = amount_dist(gen);
        bank.transfer(from, to, amount);
    }
}

// Thread function to perform consistency checks
void consistency_checker(Bank& bank, int num_checks, int check_interval_ms) {
    for (int i = 0; i < num_checks; i++) {
        std::this_thread::sleep_for(std::chrono::milliseconds(check_interval_ms));
        
        bool consistent = bank.consistency_check();
        if (!consistent) {
            std::cout << "WARNING: Consistency check failed!" << std::endl;
        } else {
            std::cout << "Consistency check passed. Total: " << bank.get_total_balance() << std::endl;
        }
    }
}

int main() {
    const int NUM_ACCOUNTS = 10;
    const int INITIAL_BALANCE = 1000;
    const int NUM_OPERATIONS = 10000;
    const int MIN_AMOUNT = 1;
    const int MAX_AMOUNT = 100;
    const int NUM_TRANSFER_THREADS = 4;
    const int NUM_CONSISTENCY_CHECKS = 5;
    const int CHECK_INTERVAL_MS = 200;
    
    // Create bank with initial state
    Bank bank(NUM_ACCOUNTS, INITIAL_BALANCE);
    
    std::cout << "Initial bank state:" << std::endl;
    std::cout << "Total balance: " << bank.get_total_balance() << std::endl;
    std::cout << "Expected total: " << bank.get_initial_total() << std::endl;
    std::cout << std::endl;
    
    // Verify initial consistency
    assert(bank.consistency_check());
    
    // Create transfer worker threads
    std::vector<std::thread> threads;
    
    // Start transfer worker threads
    for (int i = 0; i < NUM_TRANSFER_THREADS; i++) {
        threads.emplace_back(transfer_worker, std::ref(bank), NUM_ACCOUNTS, 
                            NUM_OPERATIONS, MIN_AMOUNT, MAX_AMOUNT);
    }
    
    // Start consistency checker thread
    std::thread checker_thread(consistency_checker, std::ref(bank), 
                              NUM_CONSISTENCY_CHECKS, CHECK_INTERVAL_MS);
    
    // Wait for all transfer threads to complete
    for (auto& thread : threads) {
        thread.join();
    }
    
    // Wait for consistency checker thread
    checker_thread.join();
    
    std::cout << std::endl;
    std::cout << "Final bank state:" << std::endl;
    std::cout << "Total balance: " << bank.get_total_balance() << std::endl;
    std::cout << "Expected total: " << bank.get_initial_total() << std::endl;
    
    // Final consistency check
    bool final_consistent = bank.consistency_check();
    
    if (final_consistent) {
        std::cout << "SUCCESS: Final consistency check passed!" << std::endl;
    } else {
        std::cout << "FAILURE: Final consistency check failed!" << std::endl;
    }
    
    // Print individual account balances
    std::cout << std::endl;
    std::cout << "Individual account balances:" << std::endl;
    for (int i = 0; i < NUM_ACCOUNTS; i++) {
        std::cout << "Account " << i << ": " << bank.get_account_balance(i) << std::endl;
    }
    
    return final_consistent ? 0 : 1;
}

