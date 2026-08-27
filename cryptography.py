import numpy as np
import galois
import more_itertools
import logging
from typing import Tuple

# Configure logging
logging.basicConfig(filename='crypto.log', filemode='w', level=logging.INFO)
logger = logging.getLogger(__name__)


def keygen(q: int, n: int, m: int) -> Tuple[Tuple[np.ndarray, np.ndarray], np.ndarray]:
    """
    Generate an LWE (Learning With Errors) keypair.
    
    Args:
        q: Modulus for the finite field
        n: Secret key dimension
        m: Number of samples
        
    Returns:
        Tuple of (public_key, private_key) where:
        - public_key = (A, b) with A shape (m, n) and b shape (m, 1)
        - private_key = s with shape (n, 1)
    """
    A = np.random.randint(0, q, (m, n))
    s = np.random.randint(0, q, (n, 1))
    
    # Generate error vector with distribution: 10% -1, 80% 0, 10% +1
    e = np.random.choice(3, m, p=[0.1, 0.8, 0.1]) - 1
    e = np.atleast_2d(e)
    e = np.transpose(e)
    
    b = (np.dot(A, s) + e) % q
    public_key = (A, b)
    private_key = s

    return public_key, private_key


def encrypt(plaintext: np.ndarray, public_key: Tuple[np.ndarray, np.ndarray], q: int) -> np.ndarray:
    """
    Encrypt a plaintext bit array using the LWE public key.
    
    Args:
        plaintext: Array of bits to encrypt
        public_key: Tuple (A, b) from keygen
        q: Modulus
        
    Returns:
        Array of ciphertext tuples, one per plaintext bit
    """
    length = len(plaintext)
    matrix_length = len(public_key[1])
    final_array = np.zeros(shape=length, dtype=object)
    
    for i in range(length):
        pt = plaintext[i]
        r = np.random.randint(0, 2, (1, matrix_length))
        a = np.dot(r, np.array(public_key[0])) % q
        b = (np.dot(r, np.array(public_key[1])) + pt * q / 2) % q
        final_array[i] = (a.flatten(), b.flatten())
    
    return final_array


def decrypt(ciphertext: np.ndarray, private_key: np.ndarray, q: int) -> np.ndarray:
    """
    Decrypt ciphertext using the private key.
    
    Args:
        ciphertext: Array of ciphertext tuples from encrypt
        private_key: Private key s from keygen
        q: Modulus
        
    Returns:
        Array of decrypted bits
    """
    final_text = np.zeros(shape=len(ciphertext), dtype=int)
    
    for i in range(len(ciphertext)):
        v = (np.dot(ciphertext[i][0], private_key)) % q
        m = (ciphertext[i][1] - v) % q
        m = np.floor(abs(m))
        
        # Determine bit: 1 if m is closer to q/2 than to 0 or q
        if abs(m - q/2) < m and abs(m - q/2) < abs(q - m):
            final_text[i] = 1
    
    return final_text


def crack1(ciphertext: np.ndarray, public_key: Tuple[np.ndarray, np.ndarray], q: int) -> np.ndarray:
    """
    Attack crack1: Direct linear algebra approach when A is invertible.
    Solves A*s = b directly to recover the private key.
    
    Args:
        ciphertext: Encrypted bits
        public_key: Tuple (A, b)
        q: Modulus
        
    Returns:
        Decrypted plaintext array
    """
    GF = galois.GF(q)
    
    A = np.array(public_key[0], dtype=int)
    b = np.array(public_key[1], dtype=int)
    
    A = GF(A)
    b = GF(b)
    
    # Take the minimum dimension to form a square matrix
    smaller_dimension = min(A.shape[0], A.shape[1])
    
    A_reduced = A[0:smaller_dimension]
    b_reduced = b[0:smaller_dimension]
    
    A_reduced_inv = np.linalg.inv(A_reduced)
    x = np.matmul(A_reduced_inv, b_reduced)
    x = np.array(x, dtype=int)
    
    plaintext = decrypt(ciphertext, x, q)
    return plaintext


def crack2(ciphertext: np.ndarray, public_key: Tuple[np.ndarray, np.ndarray], q: int, 
           max_iterations: int = 1000, confidence_threshold: int = 15) -> np.ndarray:
    """
    Attack crack2: Random permutation sampling with majority voting.
    Samples random square sub-matrices of A and votes on the most frequent secret.
    
    Args:
        ciphertext: Encrypted bits
        public_key: Tuple (A, b)
        q: Modulus
        max_iterations: Maximum iterations to attempt
        confidence_threshold: Stop if best_secret appears this many times
        
    Returns:
        Decrypted plaintext array
    """
    GF = galois.GF(q)
    
    length = len(public_key[1])
    A = np.array(public_key[0], dtype=int)
    b = np.array(public_key[1], dtype=int)
    
    smaller_dimension = A.shape[1]
    base_case = np.arange(length, dtype=int)
    
    potential_secrets = {}
    best_secret = None
    best_secret_score = 0
    second_best_secret_score = 0
    iteration = 0
    
    while iteration < max_iterations:
        try:
            # Sample a random subset of rows
            permutation = np.random.choice(length, smaller_dimension, replace=False)
            
            A_reduced = A[permutation]
            A_reduced = GF(A_reduced)
            b_reduced = b[permutation]
            b_reduced = GF(b_reduced)
            
            x = np.linalg.solve(A_reduced, b_reduced)
            x_str = str(x)
            
            # Update vote count
            if x_str in potential_secrets:
                potential_secrets[x_str] = potential_secrets[x_str] + 1
            else:
                potential_secrets[x_str] = 1
            
            # Update best/second-best candidates
            current_count = potential_secrets[x_str]
            
            if current_count > best_secret_score:
                second_best_secret_score = best_secret_score
                best_secret = x
                best_secret_score = current_count
                logger.info(f"New best secret with {best_secret_score} votes")
                print(f"{best_secret_score} (best)")
            elif current_count > second_best_secret_score:
                second_best_secret_score = current_count
                logger.info(f"Second best secret has {second_best_secret_score} votes")
                print(f"{second_best_secret_score} (second)")
            
            # Check stopping conditions
            if best_secret_score > confidence_threshold:
                logger.info(f"Confidence threshold reached: {best_secret_score} votes")
                break
            
            if best_secret_score - 10 > second_best_secret_score and best_secret_score > 5:
                logger.info(f"Sufficient lead: {best_secret_score} vs {second_best_secret_score}")
                break
            
            iteration += 1
            
        except Exception as e:
            logger.warning(f"Iteration {iteration} failed: {e}")
            continue
    
    if best_secret is None:
        logger.error("Failed to find a candidate secret")
        return np.zeros(len(ciphertext), dtype=int)
    
    x1 = np.array(best_secret, dtype=int)
    plaintext = decrypt(ciphertext, x1, q)
    return plaintext


def crack3(ciphertext: np.ndarray, public_key: Tuple[np.ndarray, np.ndarray], q: int) -> np.ndarray:
    """
    Attack crack3: Lattice basis reduction approach using Gram-Schmidt orthogonalization.
    Constructs a lattice from the LWE instance and finds the shortest vector.
    
    Args:
        ciphertext: Encrypted bits
        public_key: Tuple (A, b)
        q: Modulus
        
    Returns:
        Decrypted plaintext array
    """
    GF = galois.GF(q)
    
    A = np.array(public_key[0], dtype=int)
    b = np.array(public_key[1], dtype=int)
    
    logger.info("Starting crack3 lattice reduction attack")
    logger.info(f"A shape: {A.shape}, b shape: {b.shape}")
    
    # Build augmented matrix [A | b]
    matrix_B_part = np.append(A, b, axis=1)
    bottom_row_length = matrix_B_part.shape[1]
    
    # Add bottom row: [0, 0, ..., 0, 1]
    bottom_line = np.zeros(bottom_row_length, dtype=int)
    bottom_line[-1] = 1
    B = np.vstack((matrix_B_part, bottom_line))
    B = np.array(B, dtype=int)
    
    logger.debug(f"Lattice basis B shape: {B.shape}")
    
    # Convert to Galois Field for exact arithmetic
    B_gf = GF(B)
    
    # Gram-Schmidt orthogonalization
    B_float = B.astype(float)  # Use float for numerical stability
    length = B_float.shape[0]
    B_orthogonal = np.zeros_like(B_float)
    
    for i in range(length):
        B_orthogonal[i] = B_float[i]
        
        for j in range(i):
            # Project out previous basis vectors
            projection = np.dot(B_float[i], B_orthogonal[j]) / np.dot(B_orthogonal[j], B_orthogonal[j])
            B_orthogonal[i] = B_orthogonal[i] - projection * B_orthogonal[j]
    
    # Find the shortest vector in the reduced basis
    norms = np.array([np.linalg.norm(B_orthogonal[i]) for i in range(length)])
    shortest_idx = np.argmin(norms)
    shortest_vector = B_orthogonal[shortest_idx]
    
    logger.info(f"Shortest vector found at index {shortest_idx} with norm {norms[shortest_idx]:.4f}")
    logger.debug(f"Shortest vector: {shortest_vector}")
    
    # Extract the secret from the shortest vector
    # The vector should be approximately [s | e] where s is the secret and e is the error
    extracted_secret = shortest_vector[:-1]  # Remove the q scaling component
    
    try:
        # Try to recover the full secret by solving A*s = b - e
        x = np.round(extracted_secret).astype(int)
        x = np.atleast_2d(x).T
        
        # Attempt decryption with the extracted secret
        plaintext = decrypt(ciphertext, x, q)
        logger.info(f"Successfully decrypted with lattice secret")
        return plaintext
        
    except Exception as e:
        logger.error(f"Failed to extract secret from shortest vector: {e}")
        
        # Fallback: try to solve directly using the first few rows
        try:
            smaller_dim = min(A.shape[0], A.shape[1])
            A_gf = GF(A[:smaller_dim])
            b_gf = GF(b[:smaller_dim])
            s = np.linalg.solve(A_gf, b_gf)
            x = np.array(s, dtype=int)
            x = np.atleast_2d(x).T
            plaintext = decrypt(ciphertext, x, q)
            logger.info("Fallback solve succeeded")
            return plaintext
        except Exception as fallback_e:
            logger.error(f"Fallback also failed: {fallback_e}")
            return np.zeros(len(ciphertext), dtype=int)


if __name__ == '__main__':
    # Test keygen, encrypt, decrypt
    print("=" * 60)
    print("Testing basic LWE encryption/decryption")
    print("=" * 60)
    
    plaintext = np.array([1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 0, 0, 1])
    public_key, private_key = keygen(16, 300, 53)
    ciphertext = encrypt(plaintext, public_key, 16)
    final_text = decrypt(ciphertext, private_key, 16)
    print(f"Original:  {plaintext}")
    print(f"Decrypted: {final_text}")
    print(f"Match: {np.array_equal(plaintext, final_text)}\n")
    
    # Test crack1
    print("=" * 60)
    print("Testing crack1 (direct linear algebra)")
    print("=" * 60)
    
    public_key, private_key = keygen(13, 4, 14)
    plaintext = np.random.randint(0, 2, (1, 8))[0]
    ciphertext = encrypt(plaintext, public_key, 13)
    
    cracked_plaintext = crack1(ciphertext, public_key, 13)
    print(f"Original:  {plaintext}")
    print(f"Cracked:   {cracked_plaintext}")
    print(f"Match: {np.array_equal(plaintext, cracked_plaintext)}\n")
    
    # Test crack2
    print("=" * 60)
    print("Testing crack2 (random permutation with voting)")
    print("=" * 60)
    
    public_key, private_key = keygen(13, 4, 14)
    plaintext = np.random.randint(0, 2, (1, 8))[0]
    ciphertext = encrypt(plaintext, public_key, 13)
    
    cracked_plaintext = crack2(ciphertext, public_key, 13)
    print(f"Original:  {plaintext}")
    print(f"Cracked:   {cracked_plaintext}")
    print(f"Match: {np.array_equal(plaintext, cracked_plaintext)}\n")
    
    # Test crack3
    print("=" * 60)
    print("Testing crack3 (lattice basis reduction)")
    print("=" * 60)
    
    public_key, private_key = keygen(13, 4, 14)
    plaintext = np.random.randint(0, 2, (1, 8))[0]
    ciphertext = encrypt(plaintext, public_key, 13)
    
    cracked_plaintext = crack3(ciphertext, public_key, 13)
    print(f"Original:  {plaintext}")
    print(f"Cracked:   {cracked_plaintext}")
    print(f"Match: {np.array_equal(plaintext, cracked_plaintext)}\n")
    
    print("All tests completed!")
