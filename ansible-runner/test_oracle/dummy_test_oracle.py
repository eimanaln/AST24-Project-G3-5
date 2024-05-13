from .deployment_data import DeploymentData
from host_manager.host import Host
from .test_oracle import TestOracle
from .test_result import TestResult
import subprocess


class DummyTestOracle(TestOracle):
    def verify_deployment(self, host: Host, deployment_data: DeploymentData) -> TestResult:

        # Construct the curl command to send a HEAD request to check server status
        curl_command = f"curl -I http://{host.IP_addr}:8080 -o /dev/null -w '%{{http_code}}' -s"

        try:
            # Execute the curl command
            http_status = subprocess.run(curl_command, shell=True, check=True, text=True, capture_output=True).stdout.strip()
            # Check if the HTTP status code is '200', indicating success
            if http_status == "200":
                return TestResult(True, "Deployment verified successfully")
            else:
                return TestResult(False, f"Server response with status code: {http_status}")
        
        except subprocess.CalledProcessError as e:
            # Handle cases where the curl command fails
            return TestResult(False, f"Failed to connect to the server: {e}")
        
    def vulnerability_scan(self, host: Host, deployment_data: DeploymentData) -> TestResult:

        nmap_command = f"nmap -sV {host.container_ip}"
        try:
            result = subprocess.run(nmap_command, shell=True, check=True, text=True, capture_output=True)
    
            lines = result.stdout.split('\n')
            open_ports = []
            for line in lines:
                if "open" in line and not line.startswith('Nmap'):  
                    open_ports.append(line.strip())
            
            if open_ports:
                return TestResult(False, "Open ports found", open_ports)

            else:
                # Test is passed if no ports are open
                return TestResult(True, "No open ports found")
        
        except subprocess.CalledProcessError as e:
            return TestResult(False, f"Failed to execute nmap: {e}") 