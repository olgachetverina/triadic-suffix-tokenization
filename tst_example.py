# ============================================================================
# TST Number Format Converter
# Triadic Suffix Tokenization scheme for numerical reasoning
#
# Author: Olga Chetverina (2026)
# Article: "A Triadic Suffix Tokenization Scheme for Numerical Reasoning"
# DOI: 10.5281/zenodo.18999577
# License: MIT (or your chosen license)
#
# If you use this code or the TST scheme, please cite the article:
# https://doi.org/10.5281/zenodo.18999577
# ============================================================================

import re

def pad_fraction_group(group: str, target_length: int = 3) -> str:
    if len(group) > target_length:
        group = group[-target_length:]
    return group.ljust(target_length, '0')

def normalize_number(number_str: str) -> str:
    """
    Normalize number to standard decimal format (dot as decimal, no thousand separators).
    Default: dot is decimal, comma is thousand separator.
    """
    original = number_str.strip()
    
    # Handle sign
    sign = ''
    if original.startswith('-'):
        sign = '-'
        original = original[1:]
    
    # Check if it's European format (comma as decimal, dot as thousand)
    # European format: 12.345.678,90
    is_european = False
    if ',' in original and '.' in original:
        # If comma appears after dots, it's European
        last_comma = original.rfind(',')
        last_dot = original.rfind('.')
        if last_comma > last_dot:
            is_european = True
    
    if is_european:
        # European: comma is decimal, dot is thousand
        # Replace comma with dot, remove dots
        original = original.replace('.', '')  # remove thousand separators
        original = original.replace(',', '.') # comma becomes decimal
    else:
        # Standard: dot is decimal, comma is thousand
        if '.' in original:
            # Split at the last dot
            parts = original.split('.')
            int_part = ''.join(parts[:-1])  # all parts before last dot
            frac_part = parts[-1]           # last part after dot
            # Remove commas from integer part
            int_part = int_part.replace(',', '')
            original = int_part + '.' + frac_part
        else:
            # No decimal point - just remove commas
            original = original.replace(',', '')
    
    return sign + original


def tst_format_number(number_str, group_size=3, compact_suffix=True):
    """
    Convert a single number string to TST format.
    """
    try:
        # Запоминаем процент
        percent = ''
        if number_str.endswith('%'):
            percent = '%'
            number_str = number_str[:-1]
        
        # Запоминаем валюту и знак
        currency = ''
        plus_sign = ''
        
        # Отделяем знак плюс
        if number_str.startswith('+'):
            plus_sign = '+'
            number_str = number_str[1:]
        
        # Отделяем валюту
        for sym in ['$', '€', '£', '¥', '₹']:
            if number_str.startswith(sym):
                currency = sym
                number_str = number_str[1:]
                break
        
        # Удаляем пробелы и апострофы
        number_str = number_str.replace(' ', '')
        number_str = number_str.replace("'", '')
        
        # Определяем формат по валюте
        # Евро: запятая десятичная, точка разделитель тысяч
        if currency == '€':
            if ',' in number_str:
                number_str = number_str.replace('.', '')
                number_str = number_str.replace(',', '.')
            else:
                number_str = number_str.replace('.', '')
        
        # Доллар, йена, фунт: точка десятичная, запятая разделитель тысяч
        elif currency in ['$', '£', '¥']:
            if '.' in number_str:
                parts = number_str.split('.')
                int_part = ''.join(parts[:-1]).replace(',', '')
                number_str = int_part + '.' + parts[-1]
            else:
                number_str = number_str.replace(',', '')
        
        # Рупия: индийский формат - просто удаляем запятые
        elif currency == '₹':
            number_str = number_str.replace(',', '')
        
        # Без валюты: стандартный формат
        else:
            if '.' in number_str:
                parts = number_str.split('.')
                int_part = ''.join(parts[:-1]).replace(',', '')
                number_str = int_part + '.' + parts[-1]
            else:
                number_str = number_str.replace(',', '')
        
        # Знак минус
        sign = ''
        if number_str.startswith('-'):
            sign = '-'
            number_str = number_str[1:]
        
        # Научная нотация
        if 'e' in number_str or 'E' in number_str:
            value = float(number_str)
            number_str = format(value, 'f')
        
        # Целая и дробная часть
        if '.' in number_str:
            int_part, frac_part = number_str.split('.')
        else:
            int_part, frac_part = number_str, ''
        
        # Обработка целой части
        suffixes_int = ['', 'k', 'm', 'b', 't', 'q']
        int_groups = []
        pos = 0
        while int_part:
            group = int_part[-group_size:] if len(int_part) >= group_size else int_part
            int_part = int_part[:-len(group)]
            
            if pos == 0:
                suffix = ''
            else:
                suffix = suffixes_int[pos] if pos < len(suffixes_int) else f'e{3*pos}'
            
            if compact_suffix:
                int_groups.append(group + suffix if suffix else group)
            else:
                int_groups.append(group + (' ' + suffix if suffix else ''))
            
            pos += 1
        
        int_groups.reverse()
        int_str = ' '.join(int_groups)
        
        # Обработка дробной части
        if frac_part:
            frac_groups = []
            pos = 1
            while frac_part:
                group = frac_part[:group_size] if len(frac_part) >= group_size else frac_part
                frac_part = frac_part[len(group):]
                group = pad_fraction_group(group, target_length=3)
                suffix = 'p' * pos
                
                # FIX: всегда добавляем группу с суффиксом
                if compact_suffix:
                    # Для компактного режима: группа + суффикс (без пробела между цифрой и суффиксом)
                    frac_groups.append(group + suffix)
                else:
                    # Для некомпактного: группа + пробел + суффикс
                    frac_groups.append(group + ' ' + suffix)
                
                pos += 1
            
            # FIX: между группами ВСЕГДА пробел
            frac_str = ' '.join(frac_groups)
            
            # Если целая часть пустая или "0", добавляем 0
            if not int_str or int_str == '0':
                result = sign + '0 . ' + frac_str
            else:
                result = sign + int_str + ' . ' + frac_str
        else:
            result = sign + int_str
        
        # Собираем префикс
        full_prefix = plus_sign + currency
        if full_prefix:
            result = full_prefix + ' ' + result
        
        # Добавляем процент
        if percent:
            result = result + ' %'
        
        return result
    except Exception as e:
        return number_str

def tst_transform_text(text, group_size=3, compact_suffix=True):
    """
    Find all numbers in the text and replace them with TST format.
    """
    pattern = r'([-+]?\s*[$€£¥₹]?\s*)(\d+(?:[.,\'\s]\d+)*(?:[.,]\d+)?(?:[eE][-+]?\d+)?%?)'
    
    def repl(match):
        full_num = match.group(0)
        # Сохраняем пробелы вокруг
        leading_spaces = len(full_num) - len(full_num.lstrip())
        trailing_spaces = len(full_num) - len(full_num.rstrip())
        num_clean = full_num.strip()
        
        try:
            converted = tst_format_number(num_clean, group_size, compact_suffix)
            # Возвращаем с теми же пробелами
            return ' ' * leading_spaces + converted + ' ' * trailing_spaces
        except:
            return full_num
    
    result = re.sub(pattern, repl, text)
    
    # Убираем лишние пробелы
    result = re.sub(r' +', ' ', result)
    result = result.strip()
    
    return result


if __name__ == '__main__':
    
    test_cases = [
        ("Dollar", "$123.45"),
        ("Dollar plus", "+$123.45"),
        ("Yen", "¥123,456,789"),
        ("Euro", "€12.345,67"),
        ("Rupee", "₹12,34,567.89"),
    ]
    print("\n" + "=" * 80)
        
    for name, num in test_cases:
        result = tst_format_number(num, compact_suffix=True)
        print(f"{name:15} : {num:25} -> {result}")
    
    print("\n" + "=" * 80)
    
    text = "0.0045  and 23%  and 1.23e-4 and 1234%"
    print("Original:", text)
    print("Converted:", tst_transform_text(text, compact_suffix=True))
 
    print("\n" + "=" * 80)    
    
    test_cases = [
        ("Standard format", "12345678.1234"),
        ("Standard with commas", "12,345,678.1234"),
        ("Indian format (1,23,45,678.1234)", "1,23,45,678.1234"),
        ("Chinese format (comma groups, dot decimal)", "1234,5678.1234"),
        ("Currency USD", "$12,345,678.1234"),
        ("Currency EUR", "€12.345.678,1234"),
        ("Currency GBP", "£12345678.1234"),
        ("Currency JPY", "¥12345678.1234"),
        ("Currency INR (1,23,45,678.1234)", "₹1,23,45,678.1234"),
        ("Apostrophe separator", "12'345'678.1234"),
        ("Space separator", "12 345 678.1234"),
        ("Plus sign", "+12345678.1234"),
        ("Negative", "-12345678.1234"),
        ("Scientific notation", "1.23456781234e7"),
    ]
    
    for format_name, number_str in test_cases:
        try:
            result = tst_format_number(number_str, compact_suffix=True)
            print(f"{format_name:45} : {number_str:35} -> {result}")
            print()
        except Exception as e:
            print(f"{format_name:45} : {number_str:35} -> ERROR: {e}")
            print()
