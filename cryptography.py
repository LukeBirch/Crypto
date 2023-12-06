
import numpy as np
import galois
import scipy
import itertools
import more_itertools

def keygen(q,n,m):

    A = np.random.randint(0, q, (m,n))
    s = np.random.randint(0, q, (n,1))
    e = np.random.randint(-1, 2, (m,1))
    e = np.random.choice(3,m,p=[0.1,0.8,0.1])
    e = e - 1
    e = np.atleast_2d(e)
    e = np.transpose(e)
    
    print(e,"e")
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


plaintext = np.array([1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 0, 0, 1])
public_key, private_key = keygen(16,300,53)
ciphertext = encrypt(plaintext, public_key, 16)
final_text = decrypt(ciphertext,private_key,16)


def crack1(ciphertext, public_key, q):
    GF = galois.GF(q)

    A = np.array(public_key[0], dtype = int)
    b = np.array(public_key[1], dtype = int)

    A = GF(A)
    b = GF(b)

    if A.shape[0] < A.shape[1]:
        smaller_dimension = A.shape[0]
    else:
        smaller_dimension = A.shape[1]  

    A_reduced = A[0:smaller_dimension]
    A_reduced = GF(A_reduced)
    A_reduced_inv = np.linalg.inv(A_reduced)
    b_reduced = b[0:smaller_dimension]
    A_reduced_inv = GF(A_reduced_inv)
    b_reduced = GF(b_reduced)
    x = np.matmul(A_reduced_inv,b_reduced) 
    x = np.array(x, dtype=int)
    plaintext = decrypt(ciphertext,x,q)
    return plaintext

#plaintext = crack1(ciphertext,public_key,53)

public_key, private_key = keygen(13,4,14)
plaintext = np.random.randint(0,2,(1,8))[0] 
ciphertext = encrypt(plaintext, public_key, 13)
#crack1(ciphertext,public_key,13)
print(private_key,"correct key")
# crack2 is to crack where there is a non-zero distribution where it is 1 or -1 with low probablity 
# and is otherwise 0

def crack2(ciphertext, public_key, q):
    GF = galois.GF(q)

    length = len(public_key[1])
    A = GF(np.array(public_key[0],dtype=int))
    b = GF(np.array(public_key[1],dtype=int))

    smaller_dimension = A.shape[1]
    copy = smaller_dimension
    shape_needed = (1,smaller_dimension)
    e = np.zeros(length)
    i = 0
    potential_secrets = np.zeros((length - smaller_dimension, smaller_dimension),dtype=int)
    while smaller_dimension < length: 
        A_reduced = A[i:smaller_dimension]
        A_reduced = GF(A_reduced)
        try:
            A_reduced_inv = np.linalg.inv(A_reduced)
            b_reduced = b[i:smaller_dimension]
            A_reduced_inv = GF(A_reduced_inv)
            b_reduced = GF(b_reduced)
            x = np.matmul(A_reduced_inv,b_reduced) 
            x = np.array(x, dtype=int)
        except:
            x = np.zeros(copy)
        potential_secrets[i] = x.flatten()
        smaller_dimension = smaller_dimension + 1
        i = i + 1
    #print(potential_secrets.flatten())
    #np.delete(potential_secrets, np.zeros(copy))
    print(potential_secrets)
    potential_secrets = potential_secrets[~np.all(potential_secrets == 0, axis=1)]
    print(potential_secrets)
    #for i in potential_secrets:
    #    if np.all(0) == True:
    #        potential_secrets.
    mode = scipy.stats.mode(potential_secrets)
    x = mode[0]
    x = np.transpose(x)
    print(x,"x")
    plaintext = decrypt(ciphertext,x,q)


    # We want all array = 0 all array = 1 all array = -1
    #while 0 in e:
    #    permutations  = more_itertools.distinct_permutations(e)
    #    for possible_e in permutations:
    #        print(possible_e)
    #    e[i] = 1
    #    i = i + 1
    #for numbers in itertools.product([0, 1], repeat=5):
    #    print(numbers)
    
    #shortest_vector =  np.array([[e],[1]])

    return plaintext

crack2(ciphertext,public_key,13)

#crack3 is with an appropiate distribution

def crack3(ciphertext, public_key, q):
    GF = galois.GF(q)
    A = np.array(public_key[0],dtype=int)
    b = np.array(public_key[1],dtype=int)

    print(A)
    print(b)
    matrix_B_part = np.append(A,b,axis=1)
    bottom_row_length = matrix_B_part[0].shape[0]
    bottom_line = np.zeros(bottom_row_length)
    bottom_line[bottom_row_length-1] = 1
    B = np.vstack((matrix_B_part,bottom_line))
    B = GF(np.array(B,dtype=int))
    print(B)
    
    return 0

#crack3(ciphertext,public_key,13)