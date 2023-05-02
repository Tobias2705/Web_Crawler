from input_validator.input_validator import InputValidator


def main():
    input_validator = InputValidator('input.txt')

    data, errors = input_validator.validate_input()

    for r in data:
        print(r)

    print(25*"~")

    for e in errors:
        print((e[0], e[1]), "-", e[2])


if __name__ == '__main__':
    main()
