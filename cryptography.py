
import numpy as np
import galois
import scipy
import itertools
import more_itertools
import logging

#logging.basicConfig(filename='crack2.log', filemode='w', level=logging.INFO)

def keygen(q,n,m):

    A = np.random.randint(0, q, (m,n))
    s = np.random.randint(0, q, (n,1))
    e = np.random.randint(-1, 2, (m,1))
    e = np.random.choice(3,m,p=[0.1,0.8,0.1])
    e = e - 1
    e = np.atleast_2d(e)
    e = np.transpose(e)
    
   # print(e,"e")
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

public_key, private_key = keygen(13,4,14)
plaintext = np.random.randint(0,2,(1,8))[0] 
ciphertext = encrypt(plaintext, public_key, 13)

def crack2(ciphertext, public_key, q):
    GF = galois.GF(q)

    length = len(public_key[1])
    A = np.array(public_key[0],dtype=int)
    b = np.array(public_key[1],dtype=int)

    smaller_dimension = A.shape[1]
    base_case = np.zeros((length),dtype=int)
    for i in range(length):
        base_case[i] = i    
    potential_secrets = dict()
    condition = 0
    error = 0
    error1 = 0
    best_secret = 0
    best_secret_score = 0
    second_best_secret_score = 0
    iteration = 0
    
    while condition == 0:
        check = 0
        while check == 0:
            try:
                permutation = np.random.permutation(base_case)[0:smaller_dimension]
                A_reduced = A[permutation]
                A_reduced = GF(A_reduced)
                b_reduced = b[permutation]
                b_reduced = GF(b_reduced)
                x = np.linalg.solve(A_reduced,b_reduced)
                   
                if str(x) in potential_secrets:
                    potential_secrets[str(x)] = potential_secrets[str(x)] + 1
                else:
                    potential_secrets[str(x)] = 1  
                check = 1
                if potential_secrets[str(x)] > best_secret_score:
                    best_secret = x
                    best_secret_score = best_secret_score + 1
                    print(best_secret_score,"best_secret_score")
                elif potential_secrets[str(x)] > second_best_secret_score:
                    second_best_secret_score = second_best_secret_score + 1
                    print(second_best_secret_score,"second_best_secret_score")

                if best_secret_score - 10 > second_best_secret_score:
                    condition = 1
                if best_secret_score > 15:
                    condition = 1

                iteration = iteration + 1
            except:
                continue
    
    x1 = best_secret
    x1 = np.array(x1,dtype=int)
    plaintext = decrypt(ciphertext,x1,q)
    return plaintext

plaintext = np.array([0, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1, 0, 0, 0, 1, 1])
public_key, private_key = keygen(29,12,20)
ciphertext = encrypt(plaintext, public_key, 29)

public_key, private_key = keygen(13,4,14)
plaintext = np.random.randint(0,2,(1,8))[0] 
ciphertext = encrypt(plaintext, public_key, 13)

print(crack2(ciphertext,public_key,13))
print(plaintext)

#crack3 is with an appropiate distribution

def crack3(ciphertext, public_key, q):
    # Creating a Latice basis 
    GF = galois.GF(q)
    A = np.array(public_key[0],dtype=int)
    b = np.array(public_key[1],dtype=int)

    print(A)
    print(b)
    matrix_B_part = np.append(A,b,axis=1)
    bottom_row_length = matrix_B_part[0].shape[0]
    bottom_line = np.zeros(bottom_row_length, dtype=int)
    bottom_line[bottom_row_length-1] = 1
    B = np.vstack((matrix_B_part,bottom_line))
    B = np.array(B,dtype=int)
    print(B.dtype,"B dtype")
    B = GF(np.array(B,dtype=int))
    #
    base_case = np.zeros((length),dtype=int)
    for i in range(length):
        base_case[i] = i   
    smaller_dimension = A.shape[1]
    list_permutations = np.array(more_itertools.distinct_permutations(base_case,smaller_dimension))
    print(list_permutations,"list_permutations")
    potential_secrets = np.zeros((len(list_permutations), smaller_dimension),dtype=int)
    #
    # Perform Gram-Schmidt on B / Proabably wrong currently
    length = B.shape[1]
    B_transposed = B.transpose()
    #np.linalg.norm(B[:,0]) = np.linalg.norm(B[:,0]) / np.linalg.norm(B[:,0])
    norm = np.linalg.norm(B_transposed[0])
    norm = np.floor(abs(norm) % q)
    norm = int(norm)
    #print(norm.dtype,"norm dtpye")
    norm = GF(norm)
    B_transposed[0] = B_transposed[0] / norm
    #print(B_transposed[0],"B_transposed[0]")
    i = 1 
    copy = 0
    print(length,"length")
    while i < length - 1:
        e = B_transposed[i]
        if copy == i:
            i = i + 1
            copy = 0
        while copy < i:
            #print(copy,"copy")
            #print(i,"i")
            e = e - B_transposed[copy]*(np.dot(B_transposed[copy],B_transposed[i]))
            copy = copy + 1
            if copy == i:
                B_transposed[i] = e
                #print(B_transposed[i],"B_transposed[i]",i)

            #print(copy,"copy")
    B = B_transposed.transpose()

    norms = np.zeros(length)
    for k in range(length):
        norms[k] = np.linalg.norm(B[:,k])
    shortest = np.argmin(norms)
    shortest_vector = B[:,shortest]
    print(shortest_vector,"shortest_vector")
    x = shortest_vector[0:(len(shortest_vector)-1)]
    x = GF(x)
    x = np.transpose(x)
    # b - e = A * s
    b = GF(b)
    
    #   
    x = np.atleast_2d(x)
    x = np.transpose(x)

    #print(b,"b")
    #print(x,"x")
    #print(b - x,"b - x")    
    # b - x = A * s
    b_x = b - x
    A = GF(A)
    s = np.linalg.solve(A[:4],(b_x[:4]))
    print(s,"s")

    return 0

#crack3(ciphertext,public_key,13)