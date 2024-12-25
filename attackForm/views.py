import os
from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
def portScanner(request):
    return render(request, "portScanner.html")

def attacks(request):
    return render(request, "attacks.html")

def nmap(request):
    return render(request, "nmap.html")

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
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({"logs": logs})

    # For non-AJAX requests, render logs to a template
    return render(request, "log_viewer.html", {"logs": logs})