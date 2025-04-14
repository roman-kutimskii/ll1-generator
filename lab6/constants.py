LETTER_LOWER = '(a|b|c|d|e|f|g|h|i|j|k|l|m|n|o|p|q|r|s|t|u|v|w|x|y|z)'
LETTER_UPPER = '(A|B|C|D|E|F|G|H|I|J|K|L|M|N|O|P|Q|R|S|T|U|V|W|X|Y|Z)'
LETTER = f'({LETTER_LOWER}|{LETTER_UPPER})'
DIGIT_NO_ZERO = '(1|2|3|4|5|6|7|8|9)'
DIGIT = f'(0|{DIGIT_NO_ZERO})'
NUMBER = f'({DIGIT}|{DIGIT_NO_ZERO}{DIGIT}*)'
LETTER_OR_DIGIT = f'({LETTER}|{DIGIT})'
SPACE = '( |\n|\t|\r)'
DIVIDER = f'({SPACE}|\"|\\(|\\)|\\+|-|;|:|,|\\.|[|]|{{|}}|\\*|/|\'|\xa0|<|>|=)'
EXPONENT = f'(E(\\+|-|ε){DIGIT}+)'
