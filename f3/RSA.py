from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import random

app = Flask(__name__)
CORS(app)  # Enable CORS for all domains

# --- MANUAL RSA LOGIC ---
def gcd(a, b):
    while b: 
        a, b = b, a % b
    return a

def is_prime(n):
    if n < 2: 
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0: 
            return False
    return True

def modular_inverse(e, phi):
    d_old, d_new = 0, 1
    phi_old, phi_new = phi, e
    while phi_new > 0:
        quotient = phi_old // phi_new
        phi_old, phi_new = phi_new, phi_old - quotient * phi_new
        d_old, d_new = d_new, d_old - quotient * d_new
    return d_old % phi

# Global keys for the demo
primes = [i for i in range(100, 300) if is_prime(i)]
p, q = random.sample(primes, 2)
n, phi = p * q, (p - 1) * (q - 1)
e = 65537 if gcd(65537, phi) == 1 else 3
d = modular_inverse(e, phi)

# --- ROUTES ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/encrypt', methods=['POST'])
def encrypt_route():
    data = request.json
    print(data)  # Log incoming request data for debugging
    text = data.get("text", "")
    cipher = [pow(ord(c), e, n) for c in text]
    return jsonify({"cipher": cipher, "public_key": [e, n]})

if __name__ == '__main__':
    app.run(debug=True)
