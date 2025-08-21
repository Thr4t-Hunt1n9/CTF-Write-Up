from pwn import *

def xor_bytes(a, b):
    return bytes([x ^ y for x, y in zip(a, b)])

conn = remote('play.scriptsorcerers.xyz', 10416)

conn.recvuntil(b'Your Email is: ')
email = conn.recvline().decode().strip()
E = email.encode()
print(f"Email: {email}")

D = b'@script.sorcerer'

delta_j = b'\x00' + b'\x01' + b'\x00'*14

desired_P2 = b',' + E[0:15]
desired_P3 = E[15:] + b',' + b'a'  
original_P2 = xor_bytes(desired_P2, delta_j)

P1 = b'\x00' * 16
P3 = desired_P3
P4 = b'\x00' * 16
P5 = b'\x00' * 16

password = P1 + original_P2 + P3 + P4 + P5

conn.recvuntil(b'Enter secure password (in hex): ')
conn.sendline(password.hex().encode())

conn.recvuntil(b'Please use this key for future login: ')
encrypted_pass_hex = conn.recvline().decode().strip()
encrypted_pass = bytes.fromhex(encrypted_pass_hex)

C_blocks = [encrypted_pass[i:i+16] for i in range(0, len(encrypted_pass), 16)]

delta_n = D

C_blocks[0] = xor_bytes(C_blocks[0], delta_j)  # C1 xor delta_j
C_blocks[3] = xor_bytes(C_blocks[3], delta_n)  # C4 xor delta_n

encrypted_email = b''.join(C_blocks)

conn.recvuntil(b'Enter your choice: ')
conn.sendline(b'2')

conn.recvuntil(b'Enter encrypted email (in hex): ')
conn.sendline(encrypted_email.hex().encode())

conn.recvuntil(b'Email sent!')

conn.recvuntil(b'Enter your choice: ')
conn.sendline(b'1')

flag = conn.recvuntil(b'}', drop=False).decode()
print(flag)

conn.close()