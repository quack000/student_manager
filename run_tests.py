"""
Script helper để chạy tests dễ dàng
"""
import subprocess
import sys
import os

def run_tests():
    print("=" * 60)
    print("🧪 ĐANG CHẠY TEST...")
    print("=" * 60)
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "-v"],
        capture_output=False
    )
    print("\n" + "=" * 60)
    if result.returncode == 0:
        print("✅ TẤT CẢ TEST ĐÃ PASS!")
    else:
        print("❌ CÓ TEST BỊ FAIL!")
    print("=" * 60)
    return result.returncode
if __name__ == "__main__":
    exit_code = run_tests()
    sys.exit(exit_code)

