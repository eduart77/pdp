# Bank Concurrency Problem Solution

This project solves the concurrent bank transfer problem with the following requirements:

## Problem Requirements

1. Multiple concurrent transfer operations between bank accounts
2. Each transfer moves money from one account to another
3. Consistency checks verify total money remains constant
4. **Key constraint**: Transfers involving distinct accounts must proceed independently

## Solution Design

### Fine-Grained Locking
- Each account has its own mutex
- Transfers lock both involved accounts simultaneously
- **Deadlock prevention**: Always lock accounts in order of account ID (ascending)

### Key Classes

#### `Account`
- Represents a single bank account with balance
- Thread-safe operations using atomic operations
- `withdraw()` and `deposit()` methods

#### `Bank`
- Manages multiple accounts
- `transfer()` method performs atomic transfers between accounts
- `consistency_check()` verifies total balance hasn't changed
- Fine-grained locking ensures independent transfers on distinct accounts

## Building and Running

### Option 1: Using Make (if you have MinGW/MSYS)
```bash
make
./bank
```

### Option 2: Using Batch File (Windows)
```bash
build.bat
bank.exe
```

### Option 3: Using CMake (if installed)
```bash
mkdir build
cd build
cmake ..
make
./bank
```

### Option 4: Manual Compilation
```bash
# Using g++ (MinGW)
g++ -std=c++17 -Wall -Wextra -pthread main.cpp bank.cpp account.cpp -o bank.exe

# Or using MSVC
cl /EHsc /std:c++17 main.cpp bank.cpp account.cpp
```

## Features

1. **Concurrent Transfers**: Multiple threads perform transfers simultaneously
2. **Independent Operation**: Transfers between different account pairs don't block each other
3. **Consistency Checks**: Periodic checks verify system integrity
4. **Deadlock-Free**: Consistent locking order prevents deadlocks
5. **Atomicity**: Each transfer is atomic - either both accounts update or neither

## Test Results

The program creates:
- 10 accounts with 1000 initial balance each
- 4 transfer worker threads, each performing 10000 random transfers
- 1 consistency checker thread that runs 5 checks during execution

Expected behavior:
- All consistency checks pass (including final check)
- Individual account balances may vary, but total always equals initial total
- No deadlocks occur even with high concurrency

