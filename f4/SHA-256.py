from flask import Flask, request, render_template_string

app = Flask(__name__)

# --- Manual SHA-256 Implementation ---
def rotate_right(n, d):
    return ((n >> d) | (n << (32 - d))) & 0xFFFFFFFF

def sha256_manual(message):
    # 1. Initial Chaining Values (IVs)
    h = [
        0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
        0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19
    ]

    # 2. Round Constants (K)
    k = [
        0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
        0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
        0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
        0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
        0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
        0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
        0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
        0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2
    ]

    # 3. Preprocessing (Padding)
    msg_bits = ''.join(format(ord(c), '08b') for c in message)
    orig_len_bits = len(msg_bits)
    
    msg_bits += '1'
    while len(msg_bits) % 512 != 448:
        msg_bits += '0'
    msg_bits += format(orig_len_bits, '064b')

    # Logging the padded message
    logs = [f"<b>System:</b> Message padded to {len(msg_bits)} bits."]
    logs.append(f"<b>Full Padded Message (Binary):</b>")
    formatted_bin = ' '.join([msg_bits[j:j+8] for j in range(0, len(msg_bits), 8)])
    logs.append(f"<div style='color: #10b981; word-wrap: break-word; font-size: 11px; font-family: monospace;'>{formatted_bin}</div>")

    # 4. Processing Blocks
    for i in range(0, len(msg_bits), 512):
        chunk = msg_bits[i:i+512]
        w = [int(chunk[j:j+32], 2) for j in range(0, 512, 32)]

        # Message Schedule (Expansion)
        for j in range(16, 64):
            s0 = rotate_right(w[j-15], 7) ^ rotate_right(w[j-15], 18) ^ (w[j-15] >> 3)
            s1 = rotate_right(w[j-2], 17) ^ rotate_right(w[j-2], 19) ^ (w[j-2] >> 10)
            w.append((w[j-16] + s0 + w[j-7] + s1) & 0xFFFFFFFF)

        a, b, c, d, e, f, g, h_reg = h
        logs.append(f"<b>--- Processing Block {i//512 + 1} ---</b>")
        
        # Compression Loop (All 64 Rounds)
        for j in range(64):
            S1 = rotate_right(e, 6) ^ rotate_right(e, 11) ^ rotate_right(e, 25)
            ch = (e & f) ^ ((~e) & g)
            t1 = (h_reg + S1 + ch + k[j] + w[j]) & 0xFFFFFFFF
            S0 = rotate_right(a, 2) ^ rotate_right(a, 13) ^ rotate_right(a, 22)
            maj = (a & b) ^ (a & c) ^ (b & c)
            t2 = (S0 + maj) & 0xFFFFFFFF
            
            h_reg, g, f, e, d, c, b, a = g, f, e, (d + t1) & 0xFFFFFFFF, c, b, a, (t1 + t2) & 0xFFFFFFFF
            
            logs.append(f"Round {j:02d}: A={a:08x} B={b:08x} C={c:08x} D={d:08x} E={e:08x} F={f:08x} G={g:08x} H={h_reg:08x}")

        h = [(x + y) & 0xFFFFFFFF for x, y in zip(h, [a, b, c, d, e, f, g, h_reg])]

    final_hash = ''.join(format(x, '08x') for x in h)
    return final_hash, logs

# --- Web Interface ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>SHA-256 Visualizer</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f0f2f5; padding: 40px; color: #333; }
        .container { max-width: 1000px; margin: auto; background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.08); }
        h2 { color: #1a73e8; margin-top: 0; }
        input[type="text"] { width: 75%; padding: 12px; border: 2px solid #ddd; border-radius: 6px; font-size: 16px; outline: none; }
        button { padding: 12px 24px; background: #1a73e8; color: white; border: none; border-radius: 6px; font-size: 16px; cursor: pointer; }
        .hash-box { background: #e8f0fe; border-left: 5px solid #1a73e8; padding: 20px; margin-top: 25px; border-radius: 4px; }
        .hash-box code { font-size: 1.3em; font-weight: bold; color: #1557b0; word-break: break-all; }
        .log-container { background: #202124; color: #e8eaed; padding: 20px; border-radius: 8px; height: 500px; overflow-y: auto; font-family: 'Consolas', 'Monaco', monospace; font-size: 13px; line-height: 1.6; margin-top: 20px; }
        .log-entry { border-bottom: 1px solid #3c4043; padding: 5px 0; }
        b { color: #8ab4f8; }
    </style>
</head>
<body>
    <div class="container">
        <h2>SHA-256 Step-by-Step Visualization</h2>
        <form method="POST">
            <input type="text" name="message" placeholder="Type a message..." value="{{ request_val }}" required>
            <button type="submit">Generate Hash</button>
        </form>

        {% if result %}
            <div class="hash-box">
                <strong>Final Resulting Hash:</strong><br>
                <code>{{ result }}</code>
            </div>
            
            <h3>Internal Process & 64 Rounds</h3>
            <div class="log-container">
                {% for log in logs %}
                    <div class="log-entry">{{ log|safe }}</div>
                {% endfor %}
            </div>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def home():
    result, logs, request_val = None, [], ""
    if request.method == "POST":
        request_val = request.form.get("message", "")
        result, logs = sha256_manual(request_val)
    return render_template_string(HTML_TEMPLATE, result=result, logs=logs, request_val=request_val)

if __name__ == "__main__":
    app.run(debug=True)
