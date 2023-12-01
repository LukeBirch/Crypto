
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
    #print(len(public_key[1]))
    #dimensions = np.shape(public_key[1])
    matrix_length = len(public_key[1])
    #print(dimensions)
    # Encryption of first bit
    pt = plaintext[0]
    r = np.random.randint(0, 2, (1,matrix_length))
    a_complete = np.dot(r,public_key[0]) % 13
    b_complete =  ((np.dot(r,public_key[1]) + pt * q/2 )) % 13 

    #print(a_complete.dtype)
    #print(b_complete.dtype)
    #print(a_complete[0])
    #print(len(a_complete[0]))
    #print(matrix_length)
    
    #final_array = np.empty((a_complete,b_complete),shape=(len(a_complete[0]),1),dtype=np.object)
    #final_array = np.empty(((a_complete, b_complete)),dtype=np.object)
    #final_array = np.ndarray((a_complete, b_complete),shape=(len(a_complete[0]),1),dtype=np.object)
    #final_array = np.array(a_complete,b_complete)
    final_array = np.zeros(shape=length, dtype=object)

    #final_array = np.empty((3,0))
    #object = [(a_complete),(a_complete)]
    entry = ((a_complete),(b_complete))
    final_array[0] = entry
    # Encryption of remaining bits
    for i in range(length - 1):
        pt = plaintext[i+1]
        r = np.random.randint(0, 2, (1,matrix_length))
        a = [np.dot(r,public_key[0]) % 13]
        b =  ((np.dot(r,public_key[1]) + pt * q/2 )) % 13 
        final_array[i+1] = ((a),(b))
    #print(final_array)
    return (final_array)

# keygen(q,n,m)
public_key, private_key = keygen(13,4,14)

#plaintext = np.random.randint(0,2,(8,1))
plaintext = np.random.randint(0,2,(1,8))[0] 
#plaintext = [0,0,0,1,0,1,1,1]
print(plaintext.dtype)
print(plaintext)

ciphertext = encrypt(plaintext, public_key, 13)

#print(ciphertext.dtype())

def decrypt(ciphertext, private_key, q):
    text = []
    #print(ciphertext)
    #print(ciphertext[0])
    #print(ciphertext[0][1])
    print(ciphertext[0][0].shape,"cipherhspae")
    print("provate key",(private_key))
    print((private_key.dtype))
    print(private_key.shape,"private shape")
    final_text = np.zeros(shape=len(ciphertext))
    for i in range(len(ciphertext)):
        v = (np.dot(ciphertext[i][0], private_key)) % 13
        m = (ciphertext[i][1] - v) % 13
        m = np.floor(abs(m))
        #print(m,"m")
        # if m is closer to 0 then pt = 0 or q/2 then pt = 1
        #print(len(ciphertext))
        #print(final_text)
        # if all([bool(abs(m - q/2) < m) and bool(abs(m - q/2) < abs(q - m))]):
        if abs(m - q/2) < m and abs(m - q/2) < abs(q - m):
            text = text + [1]
            final_text[i] = 1
        else:
            text = text + [0]
        #if abs(m - q/2) > m:
        #    text = text + [0]
        #elif abs(m - q/2) > abs(q - m):
        #    text = text + [0]
        #else:
        #    text = text + [1]     
        #if all([(abs(m - q/2) < m), (abs(m - q/2) < abs(q - m))]):
        #    text = text + [1]
        #else:
        #    text = text + [0]
    print(final_text)
    return final_text
decrypt(ciphertext, private_key, 13)


#Testing with n =  16 , m =  300 , and q =  53 .
#True Plaintext:  [1 0 1 1 1 1 1 0 1 1 0 1 0 0 1 1 0 0 0 1]
plaintext1 = np.array([1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 0, 0, 1])

public_key1, private_key1 = keygen(16,300,53)

ciphertext1 = encrypt(plaintext, public_key1, 53)

decrypt(ciphertext1, public_key1, 53)

encrypt(plaintext1)



encrypt()

def crack1(ciphertext, public_key, q):

    return 0

def crack2(ciphertext, public_key, q):

    return 0

def crack3(ciphertext, public_key, q):

    return 0
