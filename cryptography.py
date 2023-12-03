
import numpy as np
import math
import galois

# Plaintext Numpy Integer Arrays
# Public key - (A,b) NumPy Integer Arrays
# Ciphertext - Numpy Object-type Array with entries pair of numpy integer arrays and integer b 

# Hardcode n, m, q ???
# Create matrix 

def keygen(q,n,m):

    A = np.random.randint(0, q, (m,n))
    s = np.random.randint(0, q, (n,1))
    e = np.random.randint(-1, 2, (m,1))

    # Change to galois
    # Change dot product to galois
    b = (np.dot(A,s) + e) % q
    public_key = (A,b)
    private_key = s

    return public_key, private_key

# Plain text will be a NumPy integer array consist of 0s and 1s which is a sequence of bits
# Public key is a pair (A, b) of NumPy integer arrays
def encrypt(plaintext, public_key, q):
    length = len(plaintext)
    matrix_length = len(public_key[1])
    r = np.random.randint(0, 2, (1,matrix_length))
    final_array = np.zeros(shape=length, dtype=object)
    # Encryption of bits
    for i in range(length):
        pt = plaintext[i]
        r = np.random.randint(0, 2, (1,matrix_length))
        a = [np.dot(r,public_key[0]) % 13]
        b =  ((np.dot(r,public_key[1]) + pt * q/2 )) % 13 
        final_array[i] = ((a),(b))
    return (final_array)

# keygen(q,n,m)
public_key, private_key = keygen(13,4,14)

#plaintext = np.random.randint(0,2,(8,1))
plaintext = np.random.randint(0,2,(1,8))[0] 
#plaintext = [0,0,0,1,0,1,1,1]
print(plaintext.dtype)
print(plaintext)

ciphertext = encrypt(plaintext, public_key, 13)

def decrypt(ciphertext, private_key, q):
    final_text = np.zeros(shape=len(ciphertext),dtype=int)
    for i in range(len(ciphertext)):
        v = (np.dot(ciphertext[i][0], private_key)) % q
        m = (ciphertext[i][1] - v) % q
        m = np.floor(abs(m))
        if abs(m - q/2) < m and abs(m - q/2) < abs(q - m):
            final_text[i] = 1
    return final_text

decrypt(ciphertext, private_key, 13)


#Testing with n =  16 , m =  300 , and q =  53 .
#True Plaintext:  [1 0 1 1 1 1 1 0 1 1 0 1 0 0 1 1 0 0 0 1]
plaintext1 = np.array([1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 0, 0, 1])

print(plaintext1)

public_key1, private_key1 = keygen(16,300,53)

ciphertext1 = encrypt(plaintext1, public_key1, 53)

decrypt(ciphertext1, private_key1, 53)

#encrypt(plaintext1)

def crack1(ciphertext, public_key, q):

    return 0

def crack2(ciphertext, public_key, q):

    return 0

def crack3(ciphertext, public_key, q):

    return 0
