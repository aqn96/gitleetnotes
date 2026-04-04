# 412. Fizz Buzz

| Field | Value |
|---|---|
| **Difficulty** | Easy |
| **Pattern** | Math |
| **Time Complexity** | O(n) |
| **Space Complexity** | O(n) |
| **Language** | python3 |
| **Solved On** | 2026-03-28 |
| **Tags** | Math, String, Simulation |

## Key Insight

The solution iterates through numbers from 1 to n, checking divisibility by 3 and 5 to determine the appropriate output for each number. This approach efficiently constructs the result list in a single pass.

## Review Tip

> Focus on understanding the problem requirements and edge cases before jumping into coding.

## Solution

```python
class Solution:
    def fizzBuzz(self, n: int) -> List[str]:
        res = []

        for i in range(1, n + 1):
            if i % 5 == 0 and i % 3 == 0:
                res.append("FizzBuzz")
            elif i % 5 == 0:
                res.append("Buzz")
            elif i % 3 == 0:
                res.append("Fizz")
            else:
                res.append(str(i))

        return res
```
