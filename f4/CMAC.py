from flask import Flask, request, render_template_string

app = Flask(__name__)

# --- CORE CMAC LOGIC STEPS ---

def xor_bytes(a, b):
    return bytes(x ^ y for x, y in zip(a, b))

def left_shift(data):
    res = bytearray(data)
    carry = 0
    for i in range(15, -1, -1):
        next_carry = res[i] >> 7
        res[i] = ((res[i] << 1) | carry) & 0xFF
        carry = next_carry
    return bytes(res), carry

def mock_aes_encrypt(key, block):
    """Placeholder for AES.Encrypt. In production, use 'cryptography' library."""
    return bytes((b ^ k) for b, k in zip(block, key))

def cmac_implementation(message, key_text):
    logs = []
    block_size = 16
    Rb = bytes([0]*15 + [0x87])
    
    # 1. Key Preparation
    key = key_text.encode().ljust(16, b'\0')[:16]
    logs.append(f"Step 1: Key used (16-byte): {key.hex().upper()}")
    
    # 2. Derive 'L'
    L = mock_aes_encrypt(key, bytes([0]*16))
    logs.append(f"Step 2: L = Enc(0) = {L.hex().upper()}")
    
    # 3. Subkey Generation
    def derive_subkey(block, name):
        shifted, carry = left_shift(block)
        res = xor_bytes(shifted, Rb) if carry else shifted
        logs.append(f"Step 3: {name} derived as {res.hex().upper()}")
        return res

    k1 = derive_subkey(L, "K1")
    k2 = derive_subkey(k1, "K2")

    # 4. Message Processing
    msg_bytes = message.encode()
    n_blocks = (len(msg_bytes) + block_size - 1) // block_size
    if n_blocks == 0: n_blocks = 1
    
    blocks = [msg_bytes[i*block_size : (i+1)*block_size] for i in range(n_blocks)]
    last_block = blocks[-1]
    is_complete = len(last_block) == block_size
    
    # 5. CBC-MAC Chain & Intermediate XORs
    state = bytes([0]*16)
    logs.append(f"Step 4: Starting CBC-MAC Chain (Initial State: {state.hex()})")

    # Process all but the last block
    for i in range(n_blocks - 1):
        xor_result = xor_bytes(state, blocks[i])
        state = mock_aes_encrypt(key, xor_result)
        logs.append(f"Block {i+1} [{blocks[i].hex().upper()}]: XORed and Encrypted -> {state.hex().upper()}")

    # 6. Final Block Special Processing
    if is_complete:
        logs.append(f"Last Block is complete. XORing with K1.")
        processed_last = xor_bytes(last_block, k1)
    else:
        padding = b'\x80' + b'\x00' * (block_size - len(last_block) - 1)
        padded_block = last_block + padding
        logs.append(f"Last Block incomplete. Padded: {padded_block.hex().upper()}")
        logs.append(f"XORing padded block with K2.")
        processed_last = xor_bytes(padded_block, k2)

    # 7. Final Output
    final_xor = xor_bytes(state, processed_last)
    logs.append(f"Step 5: Final XOR before last encryption: {final_xor.hex().upper()}")
    
    final_tag = mock_aes_encrypt(key, final_xor)
    logs.append(f"Step 6: Final Tag (Encrypted Result): {final_tag.hex().upper()}")
    
    return final_tag.hex().upper(), logs


# --- Web Interface ---
HTML = """
<!DOCTYPE html><html><body style="font-family:sans-serif; padding:40px; line-height:1.6; max-width:800px; margin:auto;">
    <h2 style="color:#2c3e50;">CMAC Step-by-Step Implementation</h2>
    <form method="POST" style="background:#ecf0f1; padding:20px; border-radius:8px;">
        <label><b>Plain Text Input:</b></label><br>
        <input type="text" name="msg" style="width:100%; padding:10px; margin:10px 0; border:1px solid #ccc;" placeholder="Enter message here..." value="{{ msg or '' }}" required><br>
        <label><b>Secret Key:</b></label><br>
        <input type="text" name="key" style="width:100%; padding:10px; margin:10px 0; border:1px solid #ccc;" value="{{ key or 'my_secure_key_12' }}" required><br>
        <button type="submit" style="background:#2980b9; color:white; border:none; padding:10px 20px; cursor:pointer; border-radius:4px;">Generate CMAC</button>
    </form>
    
    {% if res %}
    <div style="margin-top:30px;">
        <h3 style="color:#27ae60;">Final CMAC Tag:</h3>
        <code style="font-size:1.5em; font-weight:bold; background:#eee; padding:15px; display:block; border-left:5px solid #27ae60;">{{ res }}</code>
        
        <h3>Detailed Implementation Steps:</h3>
        <div style="background:#2c3e50; color:#ecf0f1; padding:20px; border-radius:5px; font-family:monospace; font-size:0.9em;">
            {% for s in logs %}
                <p style="border-bottom:1px solid #34495e; padding-bottom:5px; margin:5px 0;">> {{ s }}</p>
            {% endfor %}
        </div>
    </div>
    {% endif %}
</body></html>
"""

@app.route("/", methods=["GET", "POST"])
def run_app():
    res, logs, msg, key = None, [], None, None
    if request.method == "POST":
        msg, key = request.form.get("msg"), request.form.get("key")
        res, logs = cmac_implementation(msg, key)
    return render_template_string(HTML, res=res, logs=logs, msg=msg, key=key)

if __name__ == "__main__":
    app.run(debug=True)
