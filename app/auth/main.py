import js
from pyscript import document
from js import console, FileReader, console, localStorage
import hashlib
import json
import asyncio
import base64

# Simple state holding
state = {
    "config": {
        "lmstudio_url": "http://192.168.1.3:1234/v1",
        "model_name": "mistralai/ministral-3-14b-reasoning",
        "max_tokens": 1600
    },
    "auth_passed": False,
    "images": {
        1: None,
        2: None,
        3: None
    }
}

def show_loader(show=True, loading_text="Communicating with Model..."):
    el = document.getElementById("loading-overlay")
    text_el = document.getElementById("loading-text")
    if text_el:
        text_el.innerText = loading_text

    if show:
        el.classList.remove("hidden")
    else:
        el.classList.add("hidden")

def display_error(msg):
    err = document.getElementById("login-error")
    err.innerText = msg
    err.classList.remove("hidden")

async def load_config():
    try:
        from js import fetch
        response = await fetch("config.json")
        data = await response.json()
        state["config"]["lmstudio_url"] = str(data.lmstudio_url)
        state["config"]["model_name"] = str(data.model_name)
        state["config"]["max_tokens"] = int(data.get("max_tokens", 1600))
        console.log("Config loaded:", state["config"])
        document.getElementById("config-url").value = state["config"]["lmstudio_url"]
        document.getElementById("config-model").value = state["config"]["model_name"]
        document.getElementById("config-tokens").value = state["config"]["max_tokens"]
    except Exception as e:
        console.log(f"Error loading config: {e}")
        state["config"] = {
            "lmstudio_url": "http://192.168.1.3:1234/v1", 
            "model_name": "mistralai/ministral-3-14b-reasoning",
            "max_tokens": 1600
        }
        document.getElementById("config-url").value = state["config"]["lmstudio_url"]
        document.getElementById("config-model").value = state["config"]["model_name"]
        document.getElementById("config-tokens").value = state["config"]["max_tokens"]

async def check_credentials(username, password):
    try:
        from js import fetch
        response = await fetch("./data/users.txt")
        text = await response.text()
        
        # Hash user input
        pwd_hash = hashlib.sha256(password.encode()).hexdigest()
        
        for line in text.strip().split('\n'):
            if ':' in line:
                stored_user, stored_hash = line.split(':', 1)
                if stored_user.strip() == username and stored_hash.strip() == pwd_hash:
                    return True
        return False
    except Exception as e:
        console.error("Error reading users.txt", e)
        return False

async def attempt_login(event):
    username_input = document.getElementById("username").value
    password_input = document.getElementById("password").value
    
    if not username_input or not password_input:
        display_error("Please enter both username and password")
        return
        
    is_valid = await check_credentials(username_input, password_input)
    
    if is_valid:
        document.getElementById("login-error").classList.add("hidden")
        document.getElementById("login-container").classList.add("hidden")
        document.getElementById("app-container").classList.remove("hidden")
        document.getElementById("nav-actions").classList.remove("hidden")
        document.getElementById("user-display").innerText = f"Logged in as: {username_input}"
        state["auth_passed"] = True
        
        # Load config post-login
        await load_config()
        switch_tab('settings')
    else:
        display_error("Invalid credentials")

def logout(event):
    state["auth_passed"] = False
    document.getElementById("app-container").classList.add("hidden")
    document.getElementById("nav-actions").classList.add("hidden")
    document.getElementById("login-container").classList.remove("hidden")
    document.getElementById("username").value = ""
    document.getElementById("password").value = ""

def switch_tab(tab_name):
    settings_tab = document.getElementById("tab-settings")
    cctv_tab = document.getElementById("tab-cctv")
    blind_tab = document.getElementById("tab-blind")
    settings_view = document.getElementById("settings-view")
    cctv_view = document.getElementById("cctv-view")
    blind_view = document.getElementById("blind-view")
    
    settings_tab.className = "px-6 py-3 font-medium text-slate-500 hover:text-slate-300 transition-colors"
    cctv_tab.className = "px-6 py-3 font-medium text-slate-500 hover:text-slate-300 transition-colors"
    blind_tab.className = "px-6 py-3 font-medium text-slate-500 hover:text-slate-300 transition-colors"
    
    settings_view.classList.add("hidden")
    cctv_view.classList.add("hidden")
    blind_view.classList.add("hidden")
    
    if tab_name == 'settings':
        settings_tab.className = "px-6 py-3 font-medium text-emerald-400 border-b-2 border-emerald-400 transition-colors"
        settings_view.classList.remove("hidden")
    elif tab_name == 'cctv':
        cctv_tab.className = "px-6 py-3 font-medium text-indigo-400 border-b-2 border-indigo-400 transition-colors"
        cctv_view.classList.remove("hidden")
    else:
        blind_tab.className = "px-6 py-3 font-medium text-cyan-400 border-b-2 border-cyan-400 transition-colors"
        blind_view.classList.remove("hidden")

def switch_tab_settings(event):
    switch_tab('settings')

def switch_tab_cctv(event):
    switch_tab('cctv')

def switch_tab_blind(event):
    switch_tab('blind')

def toggle_api_key(event):
    checkbox = document.getElementById("use-api-key")
    container = document.getElementById("api-key-container")
    
    if checkbox.checked:
        container.classList.remove("hidden")
    else:
        container.classList.add("hidden")

async def verify_model(event):
    # Dynamically read current UI settings
    current_url = document.getElementById("config-url").value.strip()
    current_model = document.getElementById("config-model").value.strip()
    
    show_loader(True, "Verifying model connection...")
    from pyodide.http import pyfetch
    
    url = f"{current_url}/models"
    target_model = current_model
    
    verify_div = document.getElementById("verify-result")
    indicator = document.getElementById("verify-indicator")
    title = document.getElementById("verify-title")
    msg = document.getElementById("verify-message")
    
    verify_div.classList.remove("hidden")
    
    use_api_key = document.getElementById("use-api-key").checked
    api_key = document.getElementById("config-apikey").value.strip()
    
    headers = {}
    if use_api_key and api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    
    try:
        response = await pyfetch(url, method="GET", headers=headers)
        if not response.ok:
            raise Exception(f"HTTP Error {response.status}")
            
        data = await response.json()
        
        # 'data' should contain a list of models under the "data" key
        models = data.get("data", [])
        found = False
        
        # Iterate through Python list
        for model in models:
            if str(model.get("id")) == target_model:
                found = True
                break
                
        if found:
            indicator.className = "w-4 h-4 rounded-full bg-emerald-500"
            title.innerText = "Connection Successful"
            title.className = "text-lg font-semibold text-emerald-500"
            verify_div.className = "mt-6 p-6 rounded-lg bg-slate-900 border border-emerald-500/30"
            msg.innerText = f"Successfully connected to LMStudio. Model '{target_model}' is loaded and ready."
        else:
            indicator.className = "w-4 h-4 rounded-full bg-amber-500"
            title.innerText = "Model Not Found"
            title.className = "text-lg font-semibold text-amber-500"
            verify_div.className = "mt-6 p-6 rounded-lg bg-slate-900 border border-amber-500/30"
            msg.innerText = f"Connected to LMStudio, but model '{target_model}' was not found in the loaded models list."
            
    except Exception as e:
        indicator.className = "w-4 h-4 rounded-full bg-red-500 animate-pulse"
        title.innerText = "Connection Failed"
        title.className = "text-lg font-semibold text-red-500"
        verify_div.className = "mt-6 p-6 rounded-lg bg-red-900/20 border border-red-500 shadow-[0_0_15px_rgba(239,68,68,0.3)]"
        msg.innerText = f"Failed to connect to LMStudio at {url}. Is the server running? Error: {str(e)}"
        
    show_loader(False)

async def read_file_as_data_url(file):
    reader = FileReader.new()
    future = asyncio.Future()
    
    def on_load(event):
        future.set_result(event.target.result)
        
    def on_error(event):
        future.set_exception(Exception("File read error"))
        
    reader.onload = on_load
    reader.onerror = on_error
    reader.readAsDataURL(file)
    
    return await future

async def handle_image_upload(event, slot):
    files = event.target.files
    if files.length > 0:
        file = files.item(0)
        data_url = await read_file_as_data_url(file)
        
        # Save to state and show preview
        state["images"][slot] = data_url
        preview = document.getElementById(f"preview{slot}")
        preview.src = data_url
        preview.classList.remove("hidden")
        
        icon = document.getElementById(f"label-icon-{slot}")
        text = document.getElementById(f"label-text-{slot}")
        if icon:
            icon.classList.add("opacity-0")
        if text:
            text.classList.add("opacity-0")
            if slot == 1:
                text.innerText = "Change Image 1 (Before)"
            elif slot == 2:
                text.innerText = "Change Image 2 (After)"
            elif slot == 3:
                text.innerText = "Change Reference Image"
        
        # Enable buttons if ready
        if slot in (1, 2) and state["images"][1] and state["images"][2]:
            btn = document.getElementById("analyse-cctv-btn")
            btn.disabled = False
            btn.classList.remove("button-disabled", "opacity-50", "cursor-not-allowed")
            
        if slot == 3 and state["images"][3]:
            btn = document.getElementById("analyse-access-btn")
            btn.disabled = False
            btn.classList.remove("button-disabled", "opacity-50", "cursor-not-allowed")
            
        # Reset input value to allow re-selection of same file if needed
        event.target.value = ""

async def handle_image_upload_1(event):
    await handle_image_upload(event, 1)

async def handle_image_upload_2(event):
    await handle_image_upload(event, 2)

async def handle_image_upload_3(event):
    await handle_image_upload(event, 3)

async def call_lmstudio_vision(messages):
    from pyodide.http import pyfetch
    import json
    
    # Read fresh config parameters directly from UI inputs
    current_url = document.getElementById("config-url").value.strip()
    current_model = document.getElementById("config-model").value.strip()
    try:
        current_tokens = int(document.getElementById("config-tokens").value.strip())
    except:
        current_tokens = 1600
    
    url = f"{current_url}/chat/completions"
    
    payload = {
        "model": current_model,
        "messages": messages,
        "temperature": 0.2,
        "max_tokens": current_tokens
    }
    
    use_api_key = document.getElementById("use-api-key").checked
    api_key = document.getElementById("config-apikey").value.strip()
    
    req_headers = {"Content-Type": "application/json"}
    if use_api_key and api_key:
        req_headers["Authorization"] = f"Bearer {api_key}"
    
    try:
        response = await pyfetch(
            url,
            method="POST",
            headers=req_headers,
            body=json.dumps(payload)
        )
        
        if not response.ok:
            raise Exception(f"HTTP Error {response.status}")
        
        data_dict = await response.json()
        console.log("LMStudio API Raw Dct:", data_dict)
        
        if 'error' in data_dict:
            return f"LMStudio API returned an error: {data_dict['error']}"
            
        if 'choices' not in data_dict:
            console.error("Missing 'choices' in response:", data_dict)
            return f"Unexpected API response format. Missing 'choices' key."
            
        return data_dict['choices'][0]['message']['content']
    except Exception as e:
        console.error("LMStudio API Error:", e)
        return f"Error communicating with model: {str(e)}"

async def analyse_cctv(event):
    if not state["images"][1] or not state["images"][2]:
        return
        
    model_name = document.getElementById("config-model").value.strip()
    show_loader(True, f"Communicating with Model '{model_name}'...")
    
    messages = [
        {
            "role": "system",
            "content": "You are a cutting-edge security AI designed for temporal reasoning on CCTV frames. You will receive two sequential images. Analyse the state change (delta) between them. If you detect an unauthorized entry, breach, or significant event, output your response starting with 'RED (Significant Event) - ' followed by a brief analytical explanation. If the change is ambiguous, obscured, or uncertain, output 'AMBER (Uncertain) - ' followed by your reasoning. Otherwise, output 'GREEN (Nominal) - ' followed by a brief description of the normal change."
        },
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Image 1 (Before):"},
                {"type": "image_url", "image_url": {"url": state["images"][1]}},
                {"type": "text", "text": "Image 2 (After):"},
                {"type": "image_url", "image_url": {"url": state["images"][2]}},
                {"type": "text", "text": "Perform temporal reasoning and describe the critical event delta between these two images."}
            ]
        }
    ]
    
    result_text = await call_lmstudio_vision(messages)
    
    show_loader(False)
    
    result_div = document.getElementById("cctv-result")
    result_div.classList.remove("hidden")
    
    indicator = document.getElementById("status-indicator")
    title = document.getElementById("status-title")
    
    # Simple parsing logic based on model prompt
    result_upper = result_text.upper()[:20]
    if "RED" in result_upper:
        indicator.className = "w-4 h-4 rounded-full bg-red-500 animate-pulse"
        title.innerText = "Critical Event Detected"
        title.className = "text-lg font-semibold text-red-500"
        result_div.className = "mt-6 p-6 rounded-lg bg-red-900/20 border border-red-500 shadow-[0_0_15px_rgba(239,68,68,0.3)]"
    elif "ERROR" in result_upper or "AMBER" in result_upper:
        indicator.className = "w-4 h-4 rounded-full bg-amber-500 animate-pulse"
        title.innerText = "Uncertain State"
        title.className = "text-lg font-semibold text-amber-500"
        result_div.className = "mt-6 p-6 rounded-lg bg-amber-900/20 border border-amber-500 shadow-[0_0_15px_rgba(245,158,11,0.3)]"
    else:
        indicator.className = "w-4 h-4 rounded-full bg-green-500"
        title.innerText = "Nominal State"
        title.className = "text-lg font-semibold text-green-500"
        result_div.className = "mt-6 p-6 rounded-lg bg-slate-900 border border-slate-700"
        
    # Render markdown via marked.js
    import js
    html_output = js.marked.parse(result_text)
    document.getElementById("cctv-analysis-text").innerHTML = html_output

async def analyse_accessibility(event):
    if not state["images"][3]:
        return
        
    model_name = document.getElementById("config-model").value.strip()
    show_loader(True, f"Communicating with Model '{model_name}'...")
    
    messages = [
        {
            "role": "system",
            "content": "You are a high-detail spatial describer assisting visually impaired users. When given an image (like a software UI or physical room), provide an extremely detailed, logically structured spatial description. Use relative positioning (top-left, center, bottom-right). Example: 'There is a large blue Submit button in the bottom right corner'."
        },
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Provide a high-detail spatial description of this image to help me navigate it."},
                {"type": "image_url", "image_url": {"url": state["images"][3]}}
            ]
        }
    ]
    
    result_text = await call_lmstudio_vision(messages)
    
    show_loader(False)
    
    result_div = document.getElementById("access-result")
    result_div.classList.remove("hidden")
    
    # Render markdown via marked.js
    import js
    html_output = js.marked.parse(result_text)
    document.getElementById("access-analysis-text").innerHTML = html_output

# Initial bindings that PyScript might not catch via py-click immediately
# Since we use py-click in HTML, PyScript 2024.1.1 automatically binds global functions.
# However, to be completely safe against 'Cannot read properties of undefined (reading 'call')',
# we can explicitly bind these to the global `window` object.
import pyodide.ffi
js.window.attempt_login = pyodide.ffi.create_proxy(attempt_login)
js.window.logout = pyodide.ffi.create_proxy(logout)
js.window.switch_tab_settings = pyodide.ffi.create_proxy(switch_tab_settings)
js.window.switch_tab_cctv = pyodide.ffi.create_proxy(switch_tab_cctv)
js.window.switch_tab_blind = pyodide.ffi.create_proxy(switch_tab_blind)
js.window.verify_model = pyodide.ffi.create_proxy(verify_model)
js.window.handle_image_upload_1 = pyodide.ffi.create_proxy(handle_image_upload_1)
js.window.handle_image_upload_2 = pyodide.ffi.create_proxy(handle_image_upload_2)
js.window.handle_image_upload_3 = pyodide.ffi.create_proxy(handle_image_upload_3)
js.window.analyse_cctv = pyodide.ffi.create_proxy(analyse_cctv)
js.window.analyse_accessibility = pyodide.ffi.create_proxy(analyse_accessibility)
js.window.toggle_api_key = pyodide.ffi.create_proxy(toggle_api_key)
