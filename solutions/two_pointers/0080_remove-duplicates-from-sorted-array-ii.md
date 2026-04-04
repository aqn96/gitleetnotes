# 80. Remove Duplicates from Sorted Array II

| Field | Value |
|---|---|
| **Difficulty** | Medium |
| **Pattern** | Two Pointers |
| **Time Complexity** | O(n) |
| **Space Complexity** | O(1) |
| **Language** | python3 |
| **Solved On** | 2026-01-05 |
| **Tags** | Array, Two Pointers |

## Key Insight

The solution uses a two-pointer technique to overwrite duplicates while maintaining the allowed count of two duplicates in a sorted array.

## Review Tip

> Always consider edge cases, such as arrays with fewer than three elements, when implementing solutions.

## Solution

```python
class Solution:
    def removeDuplicates(self, nums: List[int]) -> int:
        if len(nums) <= 2:
            return len(nums)

        w = 2

        for i in range(2, len(nums)):
            if nums[i] != nums[w-2]:
                nums[w] = nums[i]
                w += 1

        return w
```
