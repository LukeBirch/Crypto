import numpy as np
import galois
import scipy
import itertools
import more_itertools
import logging

def keygen(q,n,m):

    A = np.random.randint(0, q, (m,n))
    s = np.random.randint(0, q, (n,1))
    e = np.random.randint(-1, 2, (m,1))
    print(e.transpose(),"e")
    #e = np.random.choice(3,m,p=[0.1,0.8,0.1])
    #e = e - 1
    #e = np.atleast_2d(e)
    #e = np.transpose(e)
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

    length = len(public_key[1])
    base_case = np.zeros((length),dtype=int)
    for i in range(length):
        base_case[i] = i 
    correct = 0
    while correct == 0:
        try:
            permutation = np.random.permutation(base_case)[0:smaller_dimension]
            #A_reduced = A[0:smaller_dimension]
            A_reduced = A[permutation]
            A_reduced = GF(A_reduced)
            A_reduced_inv = np.linalg.inv(A_reduced)
            b_reduced = b[permutation]
            #b_reduced = b[0:smaller_dimension]
            A_reduced_inv = GF(A_reduced_inv)
            b_reduced = GF(b_reduced)
            x = np.matmul(A_reduced_inv,b_reduced) 
            x = np.array(x, dtype=int)
            correct = 1
        except:
            continue
    plaintext = decrypt(ciphertext,x,q)
    return plaintext

#public_key, private_key = keygen(13,4,14)
#plaintext = np.random.randint(0,2,(1,8))[0] 
#ciphertext = encrypt(plaintext, public_key, 13)

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
                #print(x,"x")
                #print(x.data,"x.data")
                if str(x) in potential_secrets:
                    potential_secrets[str(x)] = potential_secrets[str(x)] + 1
                    
                else:
                    potential_secrets[str(x)] = 1  
                check = 1
                if potential_secrets[str(x)] > best_secret_score:
                    best_secret = x
                    best_secret_score = best_secret_score + 1
                 

                elif potential_secrets[str(x)] > second_best_secret_score:
                    second_best_secret_score = second_best_secret_score + 1
            
                if best_secret_score - 10 > second_best_secret_score:
                    condition = 1

                if best_secret_score > 20:
                    condition = 1   
                iteration = iteration + 1
                error = error + 1
                #if error > 100:
                #    condition = 1

            except:
                #print("error")
                error1 = error1 + 1
                if error1 > 100:
                    condition = 1
                continue
    print(best_secret_score, "best_secret_score")
    print(second_best_secret_score, "second_best_secret_score")
    
    x1 = best_secret
    print(x1,"x1")
    x1 = np.array(x1,dtype=int)
    plaintext = decrypt(ciphertext,x1,q)
    return plaintext

#plaintext = np.array([0, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1, 0, 0, 0, 1, 1])
#public_key, private_key = keygen(29,12,20)
#ciphertext = encrypt(plaintext, public_key, 29)

public_key, private_key = keygen(13,4,14)
plaintext = np.random.randint(0,2,(1,8))[0] 
ciphertext = encrypt(plaintext, public_key, 13)

def check_length(vector, q):
    vector_nonGF = np.array(vector.tolist()) 
    vector_adjusted = np.where(vector_nonGF < np.floor(q/2), vector_nonGF, q - vector_nonGF)
    norm = np.sqrt(np.sum(vector_adjusted ** 2))
    return norm



print(plaintext,"plaintext")
print("crack3")
#crack3_lattice(ciphertext,public_key,13)

def crack3(ciphertext, public_key, q):
    # Creating a Latice basis 
    GF = galois.GF(q)
    A = np.array(public_key[0],dtype=int)
    b = np.array(public_key[1],dtype=int)
    matrix_B_part = np.column_stack((A,b))
    bottom_row_length = matrix_B_part[0].shape[0]
    bottom_line = np.zeros(bottom_row_length, dtype=int)
    bottom_line[bottom_row_length-1] = 1
    B = np.vstack((matrix_B_part,bottom_line))
    B = np.array(B,dtype=int)
    B = GF(np.array(B,dtype=int))
    length_B = len(B)   
    # enumeration
    B_transposed = np.transpose(B)
    length_B_transposed = len(B_transposed)
    #e_1 = np.zeros(length_B, dtype=int)
    shortest_length = check_length(B_transposed[0],q)
    #shortest_length = check_length(B_transposed[0], q)
    shortest_vector = B_transposed[0]
    #list_for_combination = []
    # q = 19 , 14 works
    if q == 19:
        n = q - 3
    else:
        n = q 
    B_transposed_0 = B_transposed[0]
    B_transposed_end = B_transposed[-1]
    # 
    #list_for_combination = []
    #for i in range(n):
    #    list_for_combination = list_for_combination + [i]
    combinations = itertools.product(range(n),repeat = (length_B_transposed-1))
    B_section = B_transposed[0:length_B_transposed-1]
    for combination in combinations:
        combination = GF(np.array(combination)).reshape((length_B_transposed-1,1))
        point = combination[0] * B_transposed_0
        combination_section = combination[0:].transpose()
        point += GF(np.dot(combination_section,B_section))
        point -= B_transposed_end
        point_length = check_length(point, q)
        if point_length < shortest_length and point_length != 0 and point_length != 1:
            shortest_length = point_length
            shortest_vector = point

    print(shortest_vector,"shortest_vector")
    shortest_vector_nonGF = np.array(shortest_vector.tolist()) 
    shortest_vector_nonGF = shortest_vector_nonGF.flatten()
    print(shortest_vector_nonGF,"shortest_vector_nonGF")
    for i in range(length_B):
        if shortest_vector_nonGF[i] > q/2:
            shortest_vector_nonGF[i] = shortest_vector_nonGF[i] - q
    print(shortest_vector_nonGF,"shortest_vector_nonGF")
    if shortest_vector_nonGF[-1] == -1:
        shortest_vector_nonGF = -shortest_vector_nonGF
    shortest_vector = shortest_vector_nonGF[:-1]
    print(shortest_vector,"shortest_vector")
    #print(b,"b")
    b_nonGF = np.array(b.tolist()) 
    b_nonGF = b_nonGF.transpose()

    b_nonGF = (b_nonGF - shortest_vector) % q
    #print("ok")
    public_key = (A,b)
    plaintext = crack1(ciphertext,public_key,q)
    print(plaintext,"plaintext")
    return plaintext

#print("crack3 enumeration")
#crack3(ciphertext,public_key,13)
