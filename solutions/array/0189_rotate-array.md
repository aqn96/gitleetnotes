# 189. Rotate Array

| Field | Value |
|---|---|
| **Difficulty** | Medium |
| **Pattern** | Array |
| **Time Complexity** | O(n) |
| **Space Complexity** | O(1) |
| **Language** | python3 |
| **Solved On** | 2026-01-17 |
| **Tags** | Array, Math, Two Pointers |

## Key Insight

The solution uses the reverse method to rotate the array in three steps: reverse the entire array, then reverse the first k elements, and finally reverse the remaining elements. This effectively achieves the desired rotation in-place.

## Review Tip

> Always consider in-place algorithms to optimize space complexity when modifying arrays.

## Solution

```python
class Solution:
    def rotate(self, nums: List[int], k: int) -> None:
        """
        Do not return anything, modify nums in-place instead.
        """
        k = k % len(nums)

        def reverse(left, right):
            while left < right:
                nums[left], nums[right] = nums[right], nums[left]
                left += 1
                right -= 1

        reverse(0, len(nums) - 1)
        reverse(0, k - 1)
        reverse(k, len(nums) - 1)


```
