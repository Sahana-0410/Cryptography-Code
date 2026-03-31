def get_table(name, size):
    print(f"Enter {name} ({size} values, space-separated):")
    return list(map(int, input().split()))
P10 = get_table("P10", 10)
P8  = get_table("P8", 8)
IP  = get_table("IP", 8)
IP_INV = get_table("IP-1", 8)
EP  = get_table("EP", 8)
P4  = get_table("P4", 4)
print("\nEnter S0 (4x4 matrix row-wise):")
S0 = [list(map(int, input().split())) for _ in range(4)]
print("\nEnter S1 (4x4 matrix row-wise):")
S1 = [list(map(int, input().split())) for _ in range(4)]
def permute(bits, table):
    return "".join(bits[i-1] for i in table)
def shift(bits, n):
    return bits[n:] + bits[:n]
def xor(a, b):
    return "".join('0' if a[i]==b[i] else '1' for i in range(len(a)))
def encrypt(plain, key):
    print("\n===== KEY GENERATION =====")
    key_p10 = permute(key, P10)
    print("After P10:", key_p10)
    left = key_p10[:5]
    right = key_p10[5:]
    left = shift(left, 1)
    right = shift(right, 1)
    K1 = permute(left + right, P8)
    print("K1:", K1)
    left = shift(left, 2)
    right = shift(right, 2)
    K2 = permute(left + right, P8)
    print("K2:", K2)
    print("\n===== ENCRYPTION =====")
    ip = permute(plain, IP)
    left = ip[:4]
    right = ip[4:]
    # ROUND 1
    ep = permute(right, EP)
    xor1 = xor(ep, K1)
    row = int(xor1[0] + xor1[3], 2)
    col = int(xor1[1] + xor1[2], 2)
    s0 = format(S0[row][col], '02b')
    row = int(xor1[4] + xor1[7], 2)
    col = int(xor1[5] + xor1[6], 2)
    s1 = format(S1[row][col], '02b')
    p4 = permute(s0 + s1, P4)
    left = xor(left, p4)
    # SWAP
    left, right = right, left
    # ROUND 2
    ep = permute(right, EP)
    xor2 = xor(ep, K2)
    row = int(xor2[0] + xor2[3], 2)
    col = int(xor2[1] + xor2[2], 2)
    s0 = format(S0[row][col], '02b')
    row = int(xor2[4] + xor2[7], 2)
    col = int(xor2[5] + xor2[6], 2)
    s1 = format(S1[row][col], '02b')
    p4 = permute(s0 + s1, P4)
    left = xor(left, p4)
    combined = left + right
    cipher = permute(combined, IP_INV)
    print("\nFinal Cipher:", cipher)
while True:
    print("\n===== S-DES MENU =====")
    print("1. Encrypt")
    print("2. Exit")
    ch = int(input("Enter choice: "))
    if ch == 1:
        plain = input("Enter 8-bit plaintext: ")
        key = input("Enter 10-bit key: ")
        if len(plain) != 8 or len(key) != 10:
            print("Invalid length!")
        elif not (set(plain) <= {'0','1'} and set(key) <= {'0','1'}):
            print("Only binary allowed!")
        else:
            encrypt(plain, key)
    elif ch == 2:
        break
    else:
        print("Invalid choice!")
