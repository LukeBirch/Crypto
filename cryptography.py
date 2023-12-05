
import numpy as np
import galois
import sympy

# Plaintext Numpy Integer Arrays
# Public key - (A,b) NumPy Integer Arrays
# Ciphertext - Numpy Object-type Array with entries pair of numpy integer arrays and integer b 

# Hardcode n, m, q ???
# Create matrix 

def keygen(q,n,m):

    A = np.random.randint(0, q, (m,n))
    s = np.random.randint(0, q, (n,1))
    e = np.random.randint(-1, 2, (m,1))
    
    #delete this !!!
    e = np.zeros(shape=(m,1))

    b = (np.dot(A,s) + e) % q
    public_key = (A,b)
    private_key = s

    return public_key, private_key

def encrypt(plaintext, public_key, q):
    length = len(plaintext)
    matrix_length = len(public_key[1])
    final_array = np.zeros(shape=length, dtype=object)
    # Encryption of bits
    for i in range(length):
        pt = plaintext[i]
        r = np.random.randint(0, 2, (1,matrix_length))
        a = np.dot(r,np.array(public_key[0])) % q
        b =  ((np.dot(r,np.array(public_key[1])) + pt * q/2 )) % q 
        final_array[i] = ((a.flatten()),(b.flatten()))
    return (final_array)

def decrypt(ciphertext, private_key, q):
    final_text = np.zeros(shape=len(ciphertext),dtype=int)
    for i in range(len(ciphertext)):
        v = (np.dot(ciphertext[i][0], private_key)) % q
        m = (ciphertext[i][1] - v) % q
        m = np.floor(abs(m))
        if abs(m - q/2) < m and abs(m - q/2) < abs(q - m):
            final_text[i] = 1
    return final_text

# crack1 is to crack where the cryptosystem has error distribution to always be 0

plaintext = np.array([1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 0, 0, 1])
public_key, private_key = keygen(16,300,53)
ciphertext = encrypt(plaintext, public_key, 16)
final_text = decrypt(ciphertext,private_key,16)
#print(plaintext)
#print(final_text)

def crack1(ciphertext, public_key, q):
    GF = galois.GF(q)

    A = np.array(public_key[0], dtype = int)
    b = np.array(public_key[1], dtype = int)

    A = GF(A)
    b = GF(b)

    length = len(public_key[1])
    
    print(A)
    print(A.shape)
    if A.shape[0] < A.shape[1]:
        smaller_dimension = A.shape[0]
    else:
        smaller_dimension = A.shape[1]
    A_reduced = A[0:smaller_dimension,0:smaller_dimension]
    A_reduced = GF(A_reduced)
    A_reduced_inv = np.linalg.inv(A_reduced)
    print(b.dtype,"b")
    b_reduced = b[0:smaller_dimension,0:smaller_dimension]

    A_reduced_inv = GF(A_reduced_inv)
    b_reduced = GF(b_reduced)
    print(A_reduced_inv,"inv")
    print(b_reduced , "b reducved")
    x = np.matmul(A_reduced_inv,b_reduced) 
    print(x, "private key sol")

    print(A_reduced,"dimension")

    #x = np.matmul(A_reduced,b_reduced) % 13

    #print(padding_needed,"padding")
    # A^-1 * b = x
    #print(np.pad(A,pad_width = padding_needed))

    
    print(A.shape)

    #print(np.matmul(b,A_inverse))
  
    #B = np.array([[A,b],[0,1]])

    #e = np.zeros(shape=(length,1))
    #shortest_vector =  np.array([[e],[1]])
    #print(shortest_vector.shape)
    #result = np.matmul(B,shortest_vector)
    #print(result,"result")
    #print(A.shape)
    #result = result.flatten()
    #print(result)
    #print(result)
    #print(A.shape)
    #print(b.shape)
    #print(np.linalg.svd(A))
    #A_pinv = np.linalg.pinv(A)
    #x = np.dot(A_pinv,b)
    #print("x",x)

    #print(A.sympy.solve(b))
    #print((A)*b,"sdvfb")
    #print(np.linalg.solve(A,b))
    #print(np.matmul(A,result[0]))
    return 0

crack1(ciphertext,public_key,53)
print(private_key)

public_key, private_key = keygen(13,4,14)
plaintext = np.random.randint(0,2,(1,8))[0] 
ciphertext = encrypt(plaintext, public_key, 13)
crack1(ciphertext,public_key,13)
print(private_key, "private key")

# crack2 is to crack where there is a non-zero distribution where it is 1 or -1 with low probablity 
# and is otherwise 0

def crack2(ciphertext, public_key, q):
    GF = galois.GF(q)

    length = len(public_key[1])
    A = GF(public_key[0])
    b = GF(public_key[1])
    
    B = np.array([[A,b],[0,1]])

    #e = np.zeros(shape=(length,1))
    #shortest_vector =  np.array([[e],[1]])

    return 0

#crack3 is with an appropiate distribution

def crack3(ciphertext, public_key, q):

    return 0
