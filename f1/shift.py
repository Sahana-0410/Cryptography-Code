def shift_cipher(plaintext, shift):
    encrypted = ""
    decrypted = ""

    print("\n--- Encryption Steps ---")
    for char in plaintext:
        if char.isalpha():
            # Encryption
            shifted_encryption = ord(char) + shift
            if char.islower() and shifted_encryption > ord('z'):
                shifted_encryption -= 26
            elif char.isupper() and shifted_encryption > ord('Z'):
                shifted_encryption -= 26
            encrypted_char = chr(shifted_encryption)
            encrypted += encrypted_char
            print(f"Encrypting '{char}' to '{encrypted_char}'")
        else:
            encrypted += char
            print(f"Non-alphabetic character '{char}' remains unchanged.")

    print(f"Final Shift Cipher Output: {encrypted}")

    print("\n--- Decryption Steps ---")
    for char in encrypted:
        if char.isalpha():
            # Decryption
            shifted_decryption = ord(char) - shift
            if char.islower() and shifted_decryption < ord('a'):
                shifted_decryption += 26
            elif char.isupper() and shifted_decryption < ord('A'):
                shifted_decryption += 26
            decrypted_char = chr(shifted_decryption)
            decrypted += decrypted_char
            print(f"Decrypting '{char}' to '{decrypted_char}'")
        else:
            decrypted += char
            print(f"Non-alphabetic character '{char}' remains unchanged.")

    print(f"Final Shift Cipher Decrypted Output: {decrypted}\n")
    return encrypted, decrypted

# Input
text = input("Enter the plaintext for Shift Cipher: ")
shift = int(input("Enter the shift value: "))
shift_cipher(text, shift)
