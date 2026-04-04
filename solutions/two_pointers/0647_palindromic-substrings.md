# 647. Palindromic Substrings

| Field | Value |
|---|---|
| **Difficulty** | Medium |
| **Pattern** | Two Pointers |
| **Time Complexity** | O(n^2) |
| **Space Complexity** | O(1) |
| **Language** | python3 |
| **Solved On** | 2026-03-29 |
| **Tags** | Two Pointers, String, Dynamic Programming |

## Key Insight

The solution uses a two-pointer technique to expand around each character and each pair of characters to count palindromic substrings efficiently.

## Review Tip

> Focus on understanding how to identify and expand potential palindromes using two pointers.

## Solution

```python
class Solution:
    def countSubstrings(self, s: str) -> int:
        res = 0

        for i in range(len(s)):

            l = r = i
            res += self.countpali(l,r,s)

            l = i
            r = i + 1
            res += self.countpali(l,r,s)

        return res

    def countpali(self, l, r, s):
        res = 0
        while l >= 0 and r < len(s) and s[l] == s[r]:
            res += 1
            l -= 1
            r += 1
        return res
```
