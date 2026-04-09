# triadic-suffix-tokenization
Official test implementation of TST - Triadic Suffix Tokenization Scheme formulated in https://doi.org/10.5281/zenodo.18999577 

## Citation

If you use this code or the TST scheme, please cite:

**Olga Chetverina (2025)**  
*"A Triadic Suffix Tokenization Scheme for Numerical Reasoning"*  
**DOI: 10.5281/zenodo.18999577**

```bibtex
@misc{chetverina2025tst,
  author       = {Olga Chetverina},
  title        = {A Triadic Suffix Tokenization Scheme for Numerical Reasoning},
  year         = {2025},
  doi          = {10.5281/zenodo.18999577},
  url          = {https://doi.org/10.5281/zenodo.18999577}
}

# TST (Triadic Suffix Tokenization) Number Format Converter

TST is a number format where digits are grouped with suffixes added to denote orders of magnitude.


In this implementation:

- Both cases are available - Option A and Option B - separated and concatenated suffixes.
- This is suffix notation, according to Section 4 of the paper. As noted there, prefixes are not much different, and there is no difference in the case of embedding in Option B.
- We assume that "." separates the decimal part.
- Zero padding (discussed in Section 6.2) was added since it was found that in the prompt it makes a big difference. However, when using an embedding with Option B the difference should disappear:
  0.19 -> 0 . 190p ; 0.9 -> 0 . 900p
- We split only into triads, though other splitting schemes could also be checked. This concerns the extra vocabulary size and the number of tokens in the sequence - should go along with best performance.
- We use letters, not special tokens.
  

## TST Format

### Integer Part (grouped right to left)
- 1st group (units): no suffix
- 2nd group (thousands): suffix `k`
- 3rd group (millions): suffix `m`
- 4th group (billions): suffix `b`
- 5th group (trillions): suffix `t`
- 6th group (quadrillions): suffix `q`

**Example:** `12,345,678` → `12m 345k 678`

### Fractional Part (grouped left to right)
- 1st group: suffix `p`
- 2nd group: suffix `pp`
- 3rd group: suffix `ppp`
- etc.

**Fractional part rules:**
- Each group is always padded with zeros to 3 digits
- `1` → `100p`
- `12` → `120p`
- `1234` → `234p` (truncated to last 3 digits)

**Example:** `0.0045` → `0 . 004p 500pp`

## Formatting Modes

### `compact_suffix=True` (default)
Digits and suffixes are concatenated without spaces:
- `12m 345k 678 . 123p 400pp`
- `$ 123 . 450p`

### `compact_suffix=False`
Space between digits and suffix:
- `12 m 345 k 678 . 123 p 400 pp`
- `$ 123 . 450 p`

## Number Processing Rules

### For numbers without currency (regular numbers)
- **Dot (.) is always the decimal separator** (separates integer from fractional part)
- Commas, spaces, and apostrophes are treated as thousand separators and removed
- This ensures unambiguous parsing: in regular numbers, dot is always fractional

**Examples:**
| Input | TST Result |
|-------|------------|
| `12345678.1234` | `12m 345k 678 . 123p 400pp` |
| `12,345,678.1234` | `12m 345k 678 . 123p 400pp` |
| `12 345 678.1234` | `12m 345k 678 . 123p 400pp` |
| `12'345'678.1234` | `12m 345k 678 . 123p 400pp` |

### Indian Format (without currency)
Indian numbering system uses grouping: first group 1-3 digits, then groups of 2 digits (lakhs and crores).

**Examples:**
| Input | Normalized | TST Result |
|-------|------------|------------|
| `12,34,567.89` | `1234567.89` | `1m 234k 567 . 890p` |
| `1,23,45,678.1234` | `12345678.1234` | `12m 345k 678 . 123p 400pp` |

### Chinese Format (without currency)
Chinese numbering system groups digits by 4 (万 - wàn = 10,000, 亿 - yì = 100,000,000).

**Examples:**
| Input | Normalized | TST Result |
|-------|------------|------------|
| `1234.5678.1234` | `123456781234` | `123b 456m 781k 234` |
| `1234,5678.1234` | `12345678.1234` | `12m 345k 678 . 123p 400pp` |

**Note:** For Chinese format, when decimal point (dot) is present, it serves as the decimal separator. Commas or dots between groups are thousand separators.

### For numbers with currency
Currencies are supported in their native formats:

| Currency | Symbol | Format | Example | TST Result |
|----------|--------|--------|---------|------------|
| US Dollar | `$` | Dot decimal, comma thousand | `$12,345.67` | `$ 12k 345 . 670p` |
| Euro | `€` | Comma decimal, dot thousand | `€12.345,67` | `€ 12k 345 . 670p` |
| Pound Sterling | `£` | Dot decimal, comma thousand | `£1,234.56` | `£ 1k 234 . 560p` |
| Japanese Yen | `¥` | Dot decimal, comma thousand | `¥123,456,789` | `¥ 123m 456k 789` |
| Indian Rupee | `₹` | Indian format (2+2+3 grouping) | `₹12,34,567.89` | `₹ 1m 234k 567 . 890p` |

### Percentages
Percentages are always separated by a space:
- `23%` → `23 %`
- `23.5%` → `23 . 500p %`
- `1234%` → `1k 234 %`

### Scientific Notation
Automatically converted to decimal format:
- `1.23e-4` → `0 . 000p 123pp`

### Negative Numbers
Minus sign is preserved before the number:
- `-123.45` → `-123 . 450p`

## Summary of Supported Formats

| Format Type | Example | Decimal Separator | Thousand Separator | TST Result |
|-------------|---------|-------------------|--------------------|------------|
| Standard | `12345678.1234` | dot (.) | none | `12m 345k 678 . 123p 400pp` |
| US/UK | `12,345,678.1234` | dot (.) | comma (,) | `12m 345k 678 . 123p 400pp` |
| European | `12.345.678,1234` | comma (,) | dot (.) | `12m 345k 678 . 123p 400pp` |
| Indian | `1,23,45,678.1234` | dot (.) | comma (,) | `12m 345k 678 . 123p 400pp` |
| Chinese | `1234,5678.1234` | dot (.) | comma (,) | `12m 345k 678 . 123p 400pp` |
| Space | `12 345 678.1234` | dot (.) | space | `12m 345k 678 . 123p 400pp` |
| Apostrophe | `12'345'678.1234` | dot (.) | apostrophe (') | `12m 345k 678 . 123p 400pp` |

## Installation and Requirements

- Python 3.6 or higher
- Standard library only (no external packages required)

## API Functions

### `tst_format_number(number_str, group_size=3, compact_suffix=True)`

Converts a single number string to TST format.

**Parameters:**
- `number_str` (str): Number string (may include currency, percent, separators)
- `group_size` (int): Number of digits per group (default 3)
- `compact_suffix` (bool): Suffix formatting mode

**Returns:** (str) Number in TST format

### `tst_transform_text(text, group_size=3, compact_suffix=True)`

Finds all numbers in text and replaces them with TST format.

**Parameters:**
- `text` (str): Input text
- `group_size` (int): Number of digits per group (default 3)
- `compact_suffix` (bool): Suffix formatting mode

**Returns:**  (str) Text with numbers converted to TST format

## Usage

```python
from tst_converter import tst_transform_text

text = "The price is $12,345.67 and 23.5%"
result = tst_transform_text(text, compact_suffix=True)
print(result)
# The price is $ 12k 345 . 670p and 23 . 500p %


