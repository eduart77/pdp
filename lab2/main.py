import threading
import time
import random
from queue import BoundedQueue


def producer(vector1, vector2, queue):
    for i in range(len(vector1)):
        product = vector1[i] * vector2[i]
        queue.put(product)
    
    queue.mark_done()


def consumer(queue):
    total = 0
    while True:
        product = queue.get()
        if product is None:
            break
        total += product
    return total


def compute_scalar_product(vector1, vector2, queue_size):
    queue = BoundedQueue(queue_size)
    result_container = []
    
    consumer_thread = threading.Thread(
        target=lambda: result_container.append(consumer(queue))
    )
    producer_thread = threading.Thread(
        target=producer,
        args=(vector1, vector2, queue)
    )
    
    start_time = time.time()
    
    consumer_thread.start()
    producer_thread.start()
    
    producer_thread.join()
    consumer_thread.join()
    
    end_time = time.time()
    
    return result_container[0], end_time - start_time


def main():
    VECTOR_SIZE = 1000000  
    QUEUE_SIZES = [10, 100, 1000, 10000, 100000]
    
    print("Generating random vectors...")
    vector1 = [random.randint(-1000, 1000) for _ in range(VECTOR_SIZE)]
    vector2 = [random.randint(-1000, 1000) for _ in range(VECTOR_SIZE)]
    
    expected_result = sum(a * b for a, b in zip(vector1, vector2))
    print(f"Expected scalar product: {expected_result}")
    print()
    
    print(f"Vector size: {VECTOR_SIZE}")
    print(f"Testing different queue sizes...\n")
    
    results = []
    
    for queue_size in QUEUE_SIZES:
        result, elapsed_time = compute_scalar_product(vector1, vector2, queue_size)
        
        correct = (result == expected_result)
        status = "[OK]" if correct else "[FAIL]"
        
        print(f"Queue size: {queue_size:6d} | Time: {elapsed_time:.4f}s | Result: {result} {status}")
        results.append((queue_size, elapsed_time, correct))
    
    print()
    print("Summary:")
    print("-" * 60)
    
    fastest = min(results, key=lambda x: x[1])
    print(f"Fastest: Queue size {fastest[0]} ({fastest[1]:.4f}s)")
    
    all_correct = all(result[2] for result in results)
    if all_correct:
        print("[OK] All results are correct!")
    else:
        print("[FAIL] Some results are incorrect!")
    
    print()
    
    print("Performance Analysis:")
    for queue_size, elapsed_time, correct in results:
        relative_to_fastest = elapsed_time / fastest[1]
        print(f"Queue size {queue_size:6d}: {relative_to_fastest:.2f}x slower than fastest")

if __name__ == "__main__":
    main()

