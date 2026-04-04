# 560. Subarray Sum Equals K

| Field | Value |
|---|---|
| **Difficulty** | Medium |
| **Pattern** | Hash Map |
| **Time Complexity** | O(n) |
| **Space Complexity** | O(n) |
| **Language** | python3 |
| **Solved On** | 2026-03-29 |
| **Tags** | Array, Hash Table, Prefix Sum |

## Key Insight

The solution uses a hash map to store the frequency of prefix sums, allowing for efficient lookup of how many times a certain sum has occurred, which helps in determining the number of subarrays that sum to k.

## Review Tip

> Understand how prefix sums can simplify the problem of finding subarray sums and how hash maps can be leveraged for efficient counting.

## Solution

```python
class Solution:
    def subarraySum(self, nums: List[int], k: int) -> int:
        res = 0
        curSum = 0
        prefixsum = { 0 : 1 }

        for n in nums:
            curSum += n
            diff = curSum - k

            res += prefixsum.get(diff, 0)
            prefixsum[curSum] = 1 + prefixsum.get(curSum, 0)

        return res

```
