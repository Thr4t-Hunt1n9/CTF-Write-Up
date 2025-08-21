from Crypto.Cipher import AES

def final_key(kb: bytes) -> bytes:
    return (bin(kb[0])[2:].zfill(8) + bin(kb[1])[2:].zfill(8)).encode()

def mitm_find_k1k2(B: bytes, C: bytes):
    table = {}
    for k1 in range(65536):
        kb = bytes([k1>>8, k1&0xff])
        key = final_key(kb)
        mid = AES.new(key, AES.MODE_ECB).encrypt(C)
        table[mid] = kb
    for k2 in range(65536):
        kb2 = bytes([k2>>8, k2&0xff])
        key2 = final_key(kb2)
        cand = AES.new(key2, AES.MODE_ECB).decrypt(B)
        if cand in table:
            return table[cand], kb2
    return None, None

def mitm_find_k3k4(enc: bytes, enc2: bytes):
    table = {}
    for k3 in range(65536):
        kb3 = bytes([k3>>8, k3&0xff])
        key3 = final_key(kb3)
        mid = AES.new(key3, AES.MODE_ECB).encrypt(enc)
        table[mid] = kb3
    for k4 in range(65536):
        kb4 = bytes([k4>>8, k4&0xff])
        key4 = final_key(kb4)
        cand = AES.new(key4, AES.MODE_ECB).decrypt(enc2)
        if cand in table:
            return table[cand], kb4
    return None, None

if __name__ == "__main__":
    enc_hex = input("1) double-encrypted secret (hex): ").strip() #19574ac010cc9866e733adc616065e6c019d85dd0b46e5c2190c31209fc57727
    enc2_hex = input("2) quadriple-encrypted (server printed) (hex): ").strip() #0239bcea627d0ff4285a9e114b660ec0e97f65042a8ad209c35a091319541837
    dec_hex = input("3) user's decrypted value (hex): ").strip() #4b3d1613610143db984be05ef6f37b31790ad420d28e562ad105c7992882ff34

    enc = bytes.fromhex(enc_hex)
    enc2 = bytes.fromhex(enc2_hex)
    dec = bytes.fromhex(dec_hex)

    print("[*] Finding user keys k1,k2 ...")
    k1,k2 = mitm_find_k1k2(enc2, dec)
    print("[+] k1,k2:", k1, k2)

    print("[*] Finding server keys k3,k4 ...")
    k3,k4 = mitm_find_k3k4(enc, enc2)
    print("[+] k3,k4:", k3, k4)

    k1f = final_key(k1); k2f = final_key(k2)
    plain = AES.new(k1f, AES.MODE_ECB).decrypt(AES.new(k2f, AES.MODE_ECB).decrypt(enc))

    flag = plain + k1 + k2 + k3 + k4
    print("[+] Secret message:", plain)
    try:
        print("[+] Full flag:", flag.decode())
    except:
        print("[+] Full flag (hex):", flag.hex())