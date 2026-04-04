# 3766. Maximum Median Sum of Subsequences of Size 3

| Field | Value |
|---|---|
| **Difficulty** | Medium |
| **Pattern** | Greedy |
| **Time Complexity** | O(n log n) |
| **Space Complexity** | O(1) |
| **Language** | python3 |
| **Solved On** | 2026-03-29 |
| **Tags** | Array, Math, Greedy, Sorting, Game Theory |

## Key Insight

The solution sorts the array and selects every second element starting from the middle third of the sorted array to maximize the median of the subsequences of size 3.

## Review Tip

> Always consider the properties of medians and how sorting can help in optimizing the selection of elements.

## Solution

```python
class Solution:
    def maximumMedianSum(self, nums: List[int]) -> int:
        nums.sort()
        r = 0 
        n = len(nums)
        d = n // 3
        for i in range(d, n, 2):
            r += nums[i]
        return r
```
