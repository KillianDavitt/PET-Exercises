# Killian Davitt, Amer Joudiah
#####################################################
# GA17 Privacy Enhancing Technologies -- Lab 01
#
# Basics of Petlib, encryption, signatures and
# an end-to-end encryption system.
#
# Run the tests through:
# $ py.test-2.7 -v Lab01Tests.py 

###########################
# Group Members: Killian Davitt, Amer Joudiah
###########################


#####################################################
# TASK 1 -- Ensure petlib is installed on the System
#           and also pytest. Ensure the Lab Code can 
#           be imported.

import petlib
import time

#####################################################
# TASK 2 -- Symmetric encryption using AES-GCM 
#           (Galois Counter Mode)
#
# Implement a encryption and decryption function
# that simply performs AES_GCM symmetric encryption
# and decryption using the functions in petlib.cipher.

from os import urandom
from petlib.cipher import Cipher

def encrypt_message(K, message):
    """ Encrypt a message under a key K """

    plaintext = message.encode("utf8")
    
    ## YOUR CODE HERE
    iv = urandom(16)
    
    aes = Cipher("aes-128-gcm")
    
    ciphertext, tag = aes.quick_gcm_enc(K,iv, plaintext)       

    return (iv, ciphertext, tag)

def decrypt_message(K, iv, ciphertext, tag):
    """ Decrypt a cipher text under a key K 
        In case the decryption fails, throw an exception.
    """
    ## YOUR CODE HERE
    try:
        aes = Cipher("aes-128-gcm")
        plain = aes.quick_gcm_dec(K,iv, ciphertext, tag)
    except: 
        raise Exception("decryption failed")

    return plain.encode("utf8")

#####################################################
# TASK 3 -- Understand Elliptic Curve Arithmetic
#           - Test if a point is on a curve.
#           - Implement Point addition.
#           - Implement Point doubling.
#           - Implement Scalar multiplication (double & add).
#           - Implement Scalar multiplication (Montgomery ladder).
#
# MUST NOT USE ANY OF THE petlib.ec FUNCIONS. Only petlib.bn!

from petlib.bn import Bn


def is_point_on_curve(a, b, p, x, y):
    """
    Check that a point (x, y) is on the curve defined by a,b and prime p.
    Reminder: an Elliptic Curve on a prime field p is defined as:

              y^2 = x^3 + ax + b (mod p)
                  (Weierstrass form)

    Return True if point (x,y) is on curve, otherwise False.
    By convention a (None, None) point represents "infinity".
    """
    assert isinstance(a, Bn)
    assert isinstance(b, Bn)
    assert isinstance(p, Bn) and p > 0
    assert (isinstance(x, Bn) and isinstance(y, Bn)) \
           or (x == None and y == None)

    if x is None and y is None:
        return True

    lhs = (y*y) % p
    rhs = (x*x*x + a*x + b) % p
    on_curve = (lhs == rhs)

    return on_curve


def point_add(a, b, p, x0, y0, x1, y1):
    """Define the "addition" operation for 2 EC Points.

    Reminder: (xr, yr) = (xq, yq) + (xp, yp)
    is defined as:
        lam = (yq - yp) * (xq - xp)^-1 (mod p)
        xr  = lam^2 - xp - xq (mod p)
        yr  = lam * (xp - xr) - yp (mod p)

    Return the point resulting from the addition. Raises an Exception if the points are equal.
    """


    ## Curve: y^2 = x^3 + ax + b
    
    # ADD YOUR CODE BELOW
    assert isinstance(p, Bn) and p > 0
    assert Bn.is_prime(p)

    
    if (x0 is None) and (y0 is None):
        if x1 is None and y1 is None:
            return None, None
        else:
            return x1,y1
    elif x1 is None and y1 is None:
        return x0,y0

    if x0 == x1 and y0 == y1:
        raise Exception('EC Points must not be equal')


    xr, yr = None, None


    try:
        lam = ((y0 - y1) * (Bn.mod_inverse((x0 - x1),p))) % p
        xr = (lam**2 - x0 - x1) % p
        yr = (lam * (x0 - xr) - y0) % p
        return (xr, yr)
    except Exception:
        return (None, None)

def point_double(a, b, p, x, y):
    """Define "doubling" an EC point.
     A special case, when a point needs to be added to itself.

     Reminder:
        lam = (3 * xp ^ 2 + a) * (2 * yp) ^ -1 (mod p)
        xr  = lam ^ 2 - 2 * xp
        yr  = lam * (xp - xr) - yp (mod p)

    Returns the point representing the double of the input (x, y).
    """  
    assert Bn.is_prime(p)
   
    # Point at infinity 
    if x is None and y is None:
        return (None, None)
    
    xr, yr = None, None
    lam = ((3 * (x*x) + a) * Bn.mod_inverse((2 * y),p)) % p
    xr = ((lam * lam) -2 * x) % p 
    yr = (lam * (x-xr) - y ) % p
    return xr, yr

def point_scalar_multiplication_double_and_add(a, b, p, x, y, scalar):
    """
    Implement Point multiplication with a scalar:
        r * (x, y) = (x, y) + ... + (x, y)    (r times)

    Reminder of Double and Multiply algorithm: r * P
        Q = infinity
        for i = 0 to num_bits(P)-1
            if bit i of r == 1 then
                Q = Q + P
            P = 2 * P
        return Q

    """
    assert Bn.is_prime(p)
    Q = (None, None)
    P = (x, y)

    for i in range(scalar.num_bits()):
        if scalar.is_bit_set(i):
            Q = point_add(a, b, p, P[0], P[1], Q[0], Q[1])
        else:
            # Wasteful point addition, added to prevent side channel attack
            W = point_add(a, b, p, P[0], P[1], Q[0], Q[1])
        P = point_double(a,b,p,P[0],P[1])
    return Q

def point_scalar_multiplication_montgomerry_ladder(a, b, p, x, y, scalar):
    """
    Implement Point multiplication with a scalar:
        r * (x, y) = (x, y) + ... + (x, y)    (r times)

    Reminder of Double and Multiply algorithm: r * P
        R0 = infinity
        R1 = P
        for i in num_bits(P)-1 to zero:
            if di = 0:
                R1 = R0 + R1
                R0 = 2R0
            else
                R0 = R0 + R1
                R1 = 2 R1
        return R0

    """
    R0 = (None, None)
    R1 = (x, y)

    for i in reversed(range(0,scalar.num_bits())):
        if not scalar.is_bit_set(i):
            R1 = point_add(a,b,p,R0[0], R0[1],R1[0],R1[1])
            R0 = point_double(a,b,p,R0[0],R0[1])
        else:
            R0 = point_add(a,b,p,R0[0], R0[1],R1[0],R1[1])
            R1 = point_double(a,b,p,R1[0],R1[1])

    return R0


#####################################################
# TASK 4 -- Standard ECDSA signatures
#
#          - Implement a key / param generation 
#          - Implement ECDSA signature using petlib.ecdsa
#          - Implement ECDSA signature verification 
#            using petlib.ecdsa

from hashlib import sha256
from petlib.ec import EcGroup
from petlib.ecdsa import do_ecdsa_sign, do_ecdsa_verify
from hashlib import sha1


def ecdsa_key_gen():
    """ Returns an EC group, a random private key for signing 
        and the corresponding public key for verification"""
    G = EcGroup()
    priv_sign = G.order().random()
    pub_verify = priv_sign * G.generator()
    return (G, priv_sign, pub_verify)


def ecdsa_sign(G, priv_sign, message):
    """ Sign the SHA256 digest of the message using ECDSA and return a signature """

    plaintext =  message.encode("utf8")
    digest = sha256(plaintext).digest()
    sig = do_ecdsa_sign(G, priv_sign, digest)

    return sig


def ecdsa_verify(G, pub_verify, message, sig):
    """ Verify the ECDSA signature on the message """
    plaintext =  message.encode("utf8")
    digest = sha256(plaintext).digest()
    res = do_ecdsa_verify(G, pub_verify, sig, digest)

    return res

#####################################################
# TASK 5 -- Diffie-Hellman Key Exchange and Derivation
#           - use Bob's public key to derive a shared key.
#           - Use Bob's public key to encrypt a message.
#           - Use Bob's private key to decrypt the message.
#
# NOTE: 

def dh_get_key():
    """ Generate a DH key pair """
    G = EcGroup()
    priv_dec = G.order().random()
    pub_enc = priv_dec * G.generator()
    return (G, priv_dec, pub_enc)


def dh_encrypt(pub, message, aliceSig = None):
    """ Assume you know the public key of someone else (Bob), 
    and wish to Encrypt a message for them.
        - Generate a fresh DH key for this message.
        - Derive a fresh shared key.
        - Use the shared key to AES_GCM encrypt the message.
        - Optionally: sign the message with Alice's key.
    """
    ## Step 1. Generate new DH key
    G, priv_dec, pub_enc =dh_get_key()

    ## Step 2. Create new Shared Key
    shared_key = pub.pt_mul(priv_dec)
    
    #change it to bits using export()
    shared_key = shared_key.export()
    digest_of_key = sha256(shared_key).digest() #too big
    digest_of_key = digest_of_key[:16]
    
    ## Step 3. Encrypt message with AES_GCM
    iv,ciphertext,tag = encrypt_message(digest_of_key,message)

    ## Step 4. Sign the message
    signature = None
    if aliceSig is not None:
        signature = ecdsa_sign(G, aliceSig, message)

    return (iv, ciphertext, tag, pub_enc, signature)



def dh_decrypt(priv, ciphertext_and_pub, aliceVer = None):
    """ Decrypt a received message encrypted using your public key, 
    of which the private key is provided. Optionally verify 
    the message came from Alice using her verification key."""

    G = EcGroup()
    
    # Ciphertext_and_pub should be a 5-tuple of iv, c, tag, public_key, signature 
 
    shared_key = ciphertext_and_pub[3].pt_mul(priv)
    #change it to bits using export()
    shared_key = shared_key.export()
    
    ## decrypt_message(K, iv, ciphertext, tag):
    digest_of_key = sha256(shared_key).digest() # reduce size of hash
    digest_of_key = digest_of_key[:16]

    plaintext = decrypt_message(digest_of_key,ciphertext_and_pub[0],ciphertext_and_pub[1],ciphertext_and_pub[2])


    if aliceVer is not None: 
        result = ecdsa_verify(G, aliceVer, plaintext, ciphertext_and_pub[4])
        if result == False:
            raise Exception("Signature not valid")
    else:
        result = None

    return (plaintext,result)


## NOTE: populate those (or more) tests
#  ensure they run using the "py.test filename" command.
#  What is your test coverage? Where is it missing cases?
#  $ py.test-2.7 --cov-report html --cov Lab01Code Lab01Code.py 


def test_encrypt():
    from os import urandom
    
    G, priv, pub = dh_get_key()
    sig_key = G.order().random()
    ver_key = sig_key * G.generator()
    message = b"Hello World!"
    iv , ciphertext, tag, pub_enc, signature = dh_encrypt(pub,
                                                          message, sig_key)

    assert len(iv) == 16
    assert len(tag) == 16
    assert len(ciphertext) == len(message)
    assert ecdsa_verify(G, ver_key, message, signature)




def test_decrypt():
    from os import urandom

    G, priv, pub = dh_get_key()
    sig_key = G.order().random()
    ver_key = sig_key * G.generator()

    message = b"Hello World!"

    
    iv ,ciphertext, tag, pub_enc, signature = dh_encrypt(pub, message,
                                                         sig_key)
    ciphertext = (iv, ciphertext, tag, pub_enc, signature, G)
    decrypted_message,signature  = dh_decrypt(priv, ciphertext, ver_key)

    assert len(iv) == 16
    assert len(tag) == 16
    assert message == decrypted_message
    assert signature

def test_fails():

    from pytest import raises

    from os import urandom
    G, priv, pub = dh_get_key()
    sig_key = G.order().random()
    ver_key = sig_key * G.generator()
    message = b"Hello World!"

    iv , ciphertext, tag, pub_enc, signature = dh_encrypt(pub,
                                                          message, sig_key)
    

    with raises(Exception) as excinfo:
        # Add 7 to the private key to ensure it's invalid
        dh_decrypt(priv+7, (iv, ciphertext, tag, pub_enc, signature), ver_key)
    assert 'decryption failed' in str(excinfo.value)
 
    with raises(Exception) as excinfo:
        ## Adding arbritrary values to iv to ensure decryption fails
        dh_decrypt(priv, ([chr(ord(x)+3) for x in iv if ord(x)<200],
                          ciphertext, tag, pub_enc, signature), ver_key)
    assert 'decryption failed' in str(excinfo.value)

    with raises(Exception) as excinfo:
        ## Concat to ciphertext to ensure decryption fails
        dh_decrypt(priv, (iv, ciphertext+"d", tag, pub_enc,
                          signature), ver_key)
    assert 'decryption failed' in str(excinfo.value)

    
    with raises(Exception) as excinfo:
        ## Add to public key to ensure decryption fails
        dh_decrypt(priv, (iv, ciphertext, tag, pub_enc+88, signature),
ver_key        )
    assert 'EC exception' in str(excinfo.value)


    with raises(Exception) as excinfo:
        ## Adding arbritrary values to signature to make verification fail
        dh_decrypt(priv, (iv, ciphertext, tag, pub_enc,
                          (signature[0]+44, signature[1]-44)), ver_key)
    assert 'Signature not valid' in str(excinfo.value)


#####################################################
# TASK 6 -- Time EC scalar multiplication
#             Open Task.
#           
#           - Time your implementations of scalar multiplication
#             (use time.clock() for measurements)for different 
#              scalar sizes)
#           - Print reports on timing dependencies on secrets.
#           - Fix one implementation to not leak information.


def time_scalar_mul():
    # setup curve 
    G = EcGroup(713) # NIST curve
    d = G.parameters()
    a, b, p = d["a"], d["b"], d["p"]
    g = G.generator()
    gx0, gy0 = g.get_affine()
    order = G.order()
    
    r = order.random()

    gx2, gy2 = (r*g).get_affine()

    # First a value with low hamming weight
    scalar_1 = Bn.from_hex('11111111111111111111111111111111111111111')

    # The second scalar value with a much higher hamming weight
    scalar_2 = Bn.from_hex('FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF')
    # Scalar values with higher hamming weight will take longer to
    # compute the multiplication of.
    t1 = time.clock()
    x2, y2 = point_scalar_multiplication_double_and_add(a, b, p, gx0,
                                                        gy0, scalar_1)
    t2 = time.clock()
    runtime = t2-t1
    print("Runtime for scalar 1: " + str(runtime))


    t1 = time.clock()
    x2, y2 = point_scalar_multiplication_double_and_add(a, b, p, gx0, gy0, scalar_2)
    t2 = time.clock()
    runtime = t2-t1
    print("Runtime for scalar 2: " + str(runtime))

        
    ## There is an effective side channel attack when using double and
    ## add ec algorithm (without the fix I have applied) if an attacker can
    ## observe the time taken for different multiplications. They can
    ## determine which of the private keys has higher hamming
    ## weight. This is of course, not a full leakage of the key but it
    ## is a leakage nonetheless
    ## This leakage does not occur with montgomerry ladder multiplication


test_encrypt()
test_decrypt()
test_fails()
time_scalar_mul()
