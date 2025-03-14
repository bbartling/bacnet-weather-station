# /opt/web_app/network_form.py

HTML_FORM = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Network Config</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f5f5f5;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
        }
        .form-container {
            background-color: #fff;
            padding: 20px 40px;
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            width: 350px;
            text-align: center;
        }
        h2 {
            color: #004aad;
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 10px;
            color: #333;
        }
        input[type="text"] {
            width: 100%;
            padding: 8px;
            margin-top: 5px;
            margin-bottom: 15px;
            border: 1px solid #ccc;
            border-radius: 4px;
        }
        button {
            padding: 10px 15px;
            background-color: #28a745;
            color: #fff;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }
        button:hover {
            background-color: #218838;
        }
        input[type="radio"] {
            margin-right: 5px;
        }
        #static-fields {
            display: none;
        }
    </style>
</head>
<body>
    <div class="form-container">
        <h2>Configure Network Settings</h2>
        <form method="POST" action="/network/config">
            <label>
                <input type="radio" name="mode" value="dhcp" checked> DHCP
            </label>
            <label>
                <input type="radio" name="mode" value="static"> Static
            </label>

            <div id="static-fields">
                <label>IP Address:
                    <input type="text" name="ip_address" placeholder="192.168.1.100">
                </label>
                <label>Netmask:
                    <input type="text" name="netmask" placeholder="255.255.255.0">
                </label>
                <label>Gateway:
                    <input type="text" name="gateway" placeholder="192.168.1.1">
                </label>
            </div>

            <button type="submit">Submit</button>
        </form>
    </div>

    <script>
        document.querySelectorAll('input[name="mode"]').forEach((elem) => {
            elem.addEventListener('change', function(event) {
                document.getElementById('static-fields').style.display = event.target.value === 'static' ? 'block' : 'none';
            });
        });
    </script>
</body>
</html>
"""
