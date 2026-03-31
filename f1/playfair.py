def playfair_cipher(plaintext, key):
    def create_matrix(key):
        seen = set()
        key = key.replace("j", "i")  # Treat 'i' and 'j' as same
        matrix = []

        for char in key + "abcdefghiklmnopqrstuvwxyz":
            if char not in seen and char.isalpha():
                seen.add(char)
                matrix.append(char)

        return [matrix[i:i+5] for i in range(0, 25, 5)]

    def prepare_text(text):
        text = text.replace("j", "i").replace(" ", "").lower()
        prepared = ""
        i = 0
        
        while i < len(text):
            char1 = text[i]
            char2 = text[i + 1] if i + 1 < len(text) else 'x'

            if char1 == char2:
                prepared += char1 + 'x'
                i += 1
            else:
                prepared += char1 + char2
                i += 2
        
        return prepared

    matrix = create_matrix(key)
    prepared_text = prepare_text(plaintext)
    result = ""

    print("Playfair Matrix:")
    for row in matrix:
        print(" ".join(row))

    for i in range(0, len(prepared_text), 2):
        row1, col1 = [(r, c) for r in range(5) for c in range(5) if matrix[r][c] == prepared_text[i]][0]
        row2, col2 = [(r, c) for r in range(5) for c in range(5) if matrix[r][c] == prepared_text[i + 1]][0]

        if row1 == row2:  # Same row
            result += matrix[row1][(col1 + 1) % 5] + matrix[row2][(col2 + 1) % 5]
            print(f"Same row: Encrypt '{prepared_text[i]}{prepared_text[i + 1]}' to '{matrix[row1][(col1 + 1) % 5]}{matrix[row2][(col2 + 1) % 5]}'")
        elif col1 == col2:  # Same column
            result += matrix[(row1 + 1) % 5][col1] + matrix[(row2 + 1) % 5][col2]
            print(f"Same column: Encrypt '{prepared_text[i]}{prepared_text[i + 1]}' to '{matrix[(row1 + 1) % 5][col1]}{matrix[(row2 + 1) % 5][col2]}'")
        else:  # Rectangle
            result += matrix[row1][col2] + matrix[row2][col1]
            print(f"Rectangle: Encrypt '{prepared_text[i]}{prepared_text[i + 1]}' to '{matrix[row1][col2]}{matrix[row2][col1]}'")

    print(f"Final Playfair Cipher Output: {result}\n")
    return result

# Input
text = input("Enter the plaintext for Playfair Cipher: ")
key = input("Enter the key: ")
playfair_cipher(text, key)
