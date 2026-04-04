# 169. Majority Element

| Field | Value |
|---|---|
| **Difficulty** | Easy |
| **Pattern** | Sorting |
| **Time Complexity** | O(n log n) |
| **Space Complexity** | O(1) |
| **Language** | python3 |
| **Solved On** | 2025-12-20 |
| **Tags** | Array, Hash Table, Divide and Conquer, Sorting, Counting |

## Key Insight

The majority element in a sorted array will always be at the middle index, as it appears more than half the time. Sorting the array allows us to easily access this element.

## Review Tip

> Always consider the most efficient approach and be prepared to discuss trade-offs in time and space complexity.

## Solution

```python
class Solution:
    def majorityElement(self, nums: List[int]) -> int:
        nums.sort()

        return nums[len(nums) // 2]
```
