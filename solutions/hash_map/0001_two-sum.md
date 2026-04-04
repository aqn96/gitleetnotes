# 1. Two Sum

| Field | Value |
|---|---|
| **Difficulty** | Easy |
| **Pattern** | Hash Map |
| **Time Complexity** | O(n) |
| **Space Complexity** | O(n) |
| **Language** | python3 |
| **Solved On** | 2026-03-14 |
| **Tags** | Array, Hash Table |

## Key Insight

The solution uses a hash map to store the indices of the numbers, allowing for constant time lookups to find the complement of the current number with respect to the target.

## Review Tip

> Always consider using a hash map for problems involving pairs or lookups to optimize time complexity.

## Solution

```python
class Solution:
    def twoSum(self, nums: List[int], target: int) -> List[int]:
        map = {}
        for i in range(len(nums)):
            complement = target - nums[i]
            if complement in map:
                return [map[complement], i]
            map[nums[i]] = i
        
        return []
            
```
