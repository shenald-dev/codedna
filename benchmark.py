import time
import re
from pathlib import Path
from codedna.analyzers.code_smell_detector import CodeSmellDetector

def benchmark_count_methods():
    detector = CodeSmellDetector()

    py_content = "def func1():\n    pass\n\ndef func2():\n    pass\n" * 100
    js_content = "function func1() {}\nconst func2 = () => {};\nclass A { method() {} }" * 100
    java_content = "public void method1() {}\nprivate int method2() {}" * 100

    n_iterations = 1000

    start = time.perf_counter()
    for _ in range(n_iterations):
        detector._count_methods(py_content, ".py")
        detector._count_methods(js_content, ".js")
        detector._count_methods(java_content, ".java")
    end = time.perf_counter()

    print(f"Time taken for {n_iterations} iterations: {end - start:.4f}s")
    return end - start

if __name__ == "__main__":
    benchmark_count_methods()
