# 899. Binary Gap

| Field | Value |
|---|---|
| **Difficulty** | Easy |
| **Pattern** | Bit Manipulation |
| **Time Complexity** | O(log n) |
| **Space Complexity** | O(1) |
| **Language** | python3 |
| **Solved On** | 2026-02-22 |
| **Tags** | Bit Manipulation |

## Key Insight

The solution uses bit manipulation to find the positions of '1's in the binary representation of the number, calculating the gaps between them efficiently.

## Review Tip

> Always consider edge cases, such as when there are fewer than two '1's in the binary representation.

## Solution

```python
class Solution:
    def binaryGap(self, n: int) -> int:
        last_index = -1
        current_index = 0
        max_gap = 0

        while n > 0:
            if n & 1:
                if last_index != -1:
                    max_gap = max(max_gap, current_index - last_index)
                last_index = current_index
            
            n >>= 1 

            current_index += 1

        return max_gap
```
