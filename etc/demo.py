"""
Simple demo showing how producer-consumer works with small vectors.
"""
import threading
from queue import BoundedQueue


def producer(vector1, vector2, queue):
    """Producer: computes products and puts them in queue."""
    for i in range(len(vector1)):
        product = vector1[i] * vector2[i]
        print(f"Producer: {vector1[i]} * {vector2[i]} = {product}")
        queue.put(product)
    
    queue.mark_done()
    print("Producer: Done!")


def consumer(queue):
    """Consumer: sums products from queue."""
    total = 0
    while True:
        product = queue.get()
        if product is None:
            break
        total += product
        print(f"Consumer: Got {product}, sum = {total}")
    
    print(f"Consumer: Final sum = {total}")
    return total


def main():
    print("=" * 50)
    print("Producer-Consumer Demo")
    print("=" * 50)
    
    vector1 = [1, 2, 3, 4, 5]
    vector2 = [6, 7, 8, 9, 10]
    
    expected = sum(a * b for a, b in zip(vector1, vector2))
    
    print(f"\nVector 1: {vector1}")
    print(f"Vector 2: {vector2}")
    print(f"Expected result: {expected}")
    print()
    
    queue = BoundedQueue(2)  # Small queue to show synchronization
    result = []
    
    consumer_thread = threading.Thread(target=lambda: result.append(consumer(queue)))
    producer_thread = threading.Thread(target=producer, args=(vector1, vector2, queue))
    
    consumer_thread.start()
    producer_thread.start()
    
    producer_thread.join()
    consumer_thread.join()
    
    print(f"\nResult: {result[0]}")
    print(f"Match: {'Yes' if result[0] == expected else 'No'}")


if __name__ == "__main__":
    main()

