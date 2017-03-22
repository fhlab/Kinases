"""
Stuff to do with emitting output. Pretty-printers and so on. Things not to do
with actually solving the problem.
"""

from termcolor import colored

def printErrors(errors, readMatch, refMatch, colouredDiff):
    """
    Output the errors for this read. Either as a coloured diff, or in a text summary.

    @param errors A list of error objects.
    @param readMatch The read, post-alignment.
    @param refMatch The reference, post-alignment.
    @param colouredDiff If true, will print a fancy coloured diff instead of a concise error summary.
    """
    for e in errors:
        print("%s %s -> %s; " % (e['position'], e['expected'], e['actual']), end='');

    print()

    if colouredDiff:
        print()
        # Print a coloured diff :D
        for i in range(0, 100, 5):
            print(str(i) + "   ", end='')
            if len(str(i)) == 1:
                print(" ", end='')

        print()
        print("|...." * 20);

        for i in range(0, len(refMatch)):
            if i > 0 and i % 100 == 0:
                print(); # Add a newline after each 100 symbols.

            refChar = refMatch[i];
            readChar = readMatch[i];

            if refChar != "-":
                if refChar == readChar:
                    print(colored(refChar, 'green'), end='');
                elif readChar != "-":
                    # Substitution
                    print(colored(readChar, 'red'), end='');
                else:
                    print(refChar, end='');
            else:
                print(colored(readChar, 'red'), end='');
