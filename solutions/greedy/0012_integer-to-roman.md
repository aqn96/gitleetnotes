# 12. Integer to Roman

| Field | Value |
|---|---|
| **Difficulty** | Medium |
| **Pattern** | Greedy |
| **Time Complexity** | O(1) |
| **Space Complexity** | O(1) |
| **Language** | python3 |
| **Solved On** | 2026-03-28 |
| **Tags** | Hash Table, Math, String |

## Key Insight

The solution uses a greedy approach by iterating through predefined Roman numeral values and subtracting them from the input number while building the resulting string.

## Review Tip

> Focus on understanding how to map values to symbols and efficiently construct the output string.

## Solution

```python
class Solution:
    def intToRoman(self, num: int) -> str:
        digits = [
            (1000, "M"),
            (900, "CM"),
            (500, "D"),
            (400, "CD"),
            (100, "C"),
            (90, "XC"),
            (50, "L"),
            (40, "XL"),
            (10, "X"),
            (9, "IX"),
            (5, "V"),
            (4, "IV"),
            (1, "I"),
        ]

        roman_digits = []
        for value, symbol in digits:

            if num == 0:
                break
            count, num = divmod(num, value)
            roman_digits.append(symbol * count)
        
        return "".join(roman_digits)


        
```
