# 9. Palindrome Number

| Field | Value |
|---|---|
| **Difficulty** | Easy |
| **Pattern** | Two Pointers |
| **Time Complexity** | O(n) |
| **Space Complexity** | O(n) |
| **Language** | python3 |
| **Solved On** | 2026-03-29 |
| **Tags** | Math |

## Key Insight

The solution converts the integer to a string and uses two pointers to compare characters from both ends towards the center, checking for equality.

## Review Tip

> Always consider edge cases, such as negative numbers or single-digit inputs, when solving palindrome problems.

## Solution

```python
class Solution:
    def isPalindrome(self, x: int) -> bool:
        string = list(str(x))
        left = 0
        right = len(string) - 1

        while left < right:
            if string[left] != string[right]:
                return False
            left += 1
            right -= 1
        
        return True



```
