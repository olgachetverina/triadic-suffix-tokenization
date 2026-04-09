from tst_converter import tst_transform_text

text = "Price: $123.45, discount: 23%, total: 1,234,567.89"

print("Original:", text)
print("Converted:", tst_transform_text(text, compact_suffix=True))