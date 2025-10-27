# Lab 2: Producer-Consumer Pattern

## Goal
Compute the scalar product of two vectors using two threads with a bounded queue.

## How It Works

**Producer Thread:**
- Computes product of each pair: v1[i] * v2[i]
- Puts results into a queue

**Consumer Thread:**
- Gets products from the queue
- Sums them up

**Queue:**
- Buffer between producer and consumer
- Has a maximum size
- Producer waits when queue is full
- Consumer waits when queue is empty

## Synchronization
- Mutex: protects the queue
- Condition variables: wake up waiting threads
- Producer waits on `not_full` condition
- Consumer waits on `not_empty` condition

## Files

- `queue.py` - BoundedQueue class
- `main.py` - Main program with producer and consumer threads
- `demo.py` - Simple demo with small vectors

## Run

Simple demo:
```bash
python lab2/demo.py
```

Performance test:
```bash
python lab2/main.py
```

The main program tests different queue sizes and shows which size is fastest.
