### Intro
- This week my team played scriptCTF, and here is the writeup for `Crypto/EaaS` (The remaining 4 chall first have been officially writeup by the organizers)

    - [Link for official writeup](https://github.com/scriptCTF/scriptCTF2025-OfficialWriteups/tree/main/Crypto)


![alt text](/ScriptCTF%202025/Crypto/imgs/image.png)

### Description

```Email as a Service! Have fun...```

- [Source](/ScriptCTF%202025/Crypto/eaas/)

![alt text](/ScriptCTF%202025/Crypto/imgs/image-1.png)


### TL;DR

- The EaaS challenge involves exploiting a vulnerability in an `AES-CBC` (Cipher Block Chaining) encryption system to retrieve the flag. The server provides an email service with a randomly generated email and requires a password encrypted with `AES-CBC`. The goal is to obtain the flag by manipulating the encrypted email.

### Analysis

- Mechanism:

    - The server generates a random email (e.g., `dyoebgrllz@notscript.sorcerer`) along with a random key and IV for AES-CBC.
    - The user inputs a password in hex format, which must be a multiple of 16 bytes and must not contain `@script.sorcerer` or the user's email.
    - The password is encrypted and returned as a hex string for later use.
    - There are two options: [1] Check for new messages, [2] Send an email.
    - To retrieve the flag, the sent email must end with `@script.sorcerer` and match the user's email during the sending process.


- Vulnerability:

    - `AES-CBC` allows data manipulation by modifying the ciphertext blocks to affect the plaintext during decryption.
    - The vulnerability lies in the email validation: if the email is altered correctly, it’s possible to inject the original email and append `@script.sorcerer` to trigger the flag.


- Exploitation Idea:

    - Use the bit-flipping technique in `AES-CBC` to alter the plaintext without knowing the key.
    - Modify the first block of the password to influence the decrypted email, injecting the original email and appending `@script.sorcerer`.


### Solution

- Preparation:

    - Connect to the server via `nc play.scriptsorcerers.xyz PORT`.
    - Retrieve the random email from the server.

- Create Password:

    - Create a password consisting of 5 blocks (80 bytes), where:

        - Block 1 (P1): 16 bytes of `0x00`.
        - Block 2 (P2): Contains the modified original email using XOR with delta_j (`\x00\x01` + 14 bytes `0x00`).
        - Block 3 (P3): The remaining email portion + a comma + a dummy character.
        - Block 4 (P4) and Block 5 (P5): 16 bytes of `0x00` each.


    - Send the password in hex format.


- Modify Ciphertext:

    - Retrieve the encrypted password from the server.
    - Split it into 4 blocks (C1, C2, C3, C4).
    - Modify C1 by XORing with delta_j and C4 by XORing with `@script.sorcerer` to shape the desired decrypted email.


- Send Encrypted Email:

    - Select option [2] and input the modified encrypted email.
    - The server will send the email and trigger the flag if the email is valid.


- Retrieve Flag:

    - Select option [1] to check for messages and receive the flag.


- [Script](/ScriptCTF%202025/Crypto/solve.py)

    - Based on the provided script, it executes the above steps using the pwntools library. The result is the flag: 
    
    ![alt text](/ScriptCTF%202025/Crypto/imgs/image-2.png)

    - Flag: `scriptCTF{CBC_1s_s3cur3_r1ght?_c726878f0479}`

### My solve for another chal (have official wu)

- [Secure Server 2](/ScriptCTF%202025/Crypto/Secure%20Server%202.py)