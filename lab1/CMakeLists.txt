cmake_minimum_required(VERSION 3.10)
project(BankConcurrency)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Add executable
add_executable(bank
    main.cpp
    bank.cpp
    account.cpp
    account.h
    bank.h
)

# Enable threads
find_package(Threads REQUIRED)
target_link_libraries(bank PRIVATE Threads::Threads)

