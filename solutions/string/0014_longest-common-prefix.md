# 14. Longest Common Prefix

| Field | Value |
|---|---|
| **Difficulty** | Easy |
| **Pattern** | String |
| **Time Complexity** | O(n * m) |
| **Space Complexity** | O(1) |
| **Language** | python3 |
| **Solved On** | 2026-03-14 |
| **Tags** | Array, String, Trie |

## Key Insight

The solution iteratively reduces the prefix by checking if it is a prefix of each string in the list, ensuring that the final prefix is common to all strings.

## Review Tip

> Focus on edge cases, such as empty strings or strings with no common prefix, and be prepared to discuss the efficiency of your approach.

## Solution

```python
class Solution:
    def longestCommonPrefix(self, strs: List[str]) -> str:
        if len(strs) == 0:
            return ""
        prefix = strs[0]
        for i in range(1, len(strs)):
            while strs[i].find(prefix) != 0:
                prefix = prefix[0 : len(prefix) - 1]
                if prefix == "":
                    return ""

        return prefix
```
