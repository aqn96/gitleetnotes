# 20. Valid Parentheses

| Field | Value |
|---|---|
| **Difficulty** | Easy |
| **Pattern** | Stack |
| **Time Complexity** | O(n) |
| **Space Complexity** | O(n) |
| **Language** | python3 |
| **Solved On** | 2026-03-14 |
| **Tags** | String, Stack |

## Key Insight

The solution uses a stack to keep track of opening parentheses and ensures that each closing parenthesis matches the most recent unmatched opening parenthesis.

## Review Tip

> Always consider edge cases, such as an empty string or unmatched parentheses, when discussing your solution.

## Solution

```python
class Solution:
    def isValid(self, s: str) -> bool:
        # Initiate a stack
        stack = []
        
        mapping = {
        ")" : "(",
        "]" : "[",
        "}" : "{"
        }

        for char in s:
            if char in mapping.values():
                stack.append(char)
            elif char in mapping.keys():
                if not stack or stack.pop() != mapping[char]:
                    return False

        return not stack
```
