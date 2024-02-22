import os
import yaml
import hcl2
import glob  
import logging

# Setup basic configuration for logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# Constants
YAML_DIRECTORY_PATH = '/workspaces/TerraGrade/conformance_packs' 
TERRAFORM_DIRECTORY_PATH = '/workspaces/TerraGrade/terraform'

def get_yaml_file_paths(yaml_directory_path):
    """Get all YAML file paths in the specified directory."""
    paths = glob.glob(os.path.join(yaml_directory_path, '*.yaml')) + glob.glob(os.path.join(yaml_directory_path, '*.yml'))
    logging.info(f"Found {len(paths)} YAML files in {yaml_directory_path}")
    return paths

def parse_yaml(yaml_file_path):
    """Parse the YAML file containing the AWS Conformance Pack criteria."""
    try:
        with open(yaml_file_path, 'r') as file:
            return yaml.safe_load(file)
    except Exception as e:
        logging.error(f"Error parsing YAML file {yaml_file_path}: {e}")
        return None

def read_terraform_files(directory_path):
    """Read and parse Terraform files in the specified directory using python-hcl2."""
    terraform_configs = {}
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            if file.endswith('.tf'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r') as tf_file:
                        terraform_configs[file] = hcl2.load(tf_file)
                except Exception as e:
                    logging.error(f"Error parsing Terraform file {file_path}: {e}. Skipping file.")
    logging.info(f"Processed Terraform files from {directory_path}.")
    return terraform_configs

def evaluate_compliance(terraform_configs, yaml_criteria):
    """Evaluate the compliance of Terraform configurations against YAML criteria."""
    compliance_report = {}

    for tf_file, configs in terraform_configs.items():
        if not isinstance(configs, list):
            configs = [configs]  # Ensure configs is a list for consistent handling
        
        for config in configs:
            # Check if the structure includes 'resource' as a key and it's a dictionary
            if isinstance(config, dict) and 'resource' in config and isinstance(config['resource'], dict):
                for resource_type, resources in config['resource'].items():
                    for resource_name, resource_config in resources.items():
                        resource_id = f"{resource_type}.{resource_name}"
                        resource_details = {
                            'compliance_status': 'Compliant',
                            'non_compliant_properties': []
                        }
                        if resource_type in yaml_criteria['Resources']:
                            properties_to_check = yaml_criteria['Resources'][resource_type].get('Properties', {})
                            for property_name, expected_value in properties_to_check.items():
                                actual_value = resource_config.get(property_name)
                                if actual_value != expected_value:
                                    resource_details['compliance_status'] = 'Non-Compliant'
                                    resource_details['non_compliant_properties'].append(property_name)
                                    # No break to collect all non-compliant properties
                        compliance_report[resource_id] = resource_details
            else:
                logging.warning(f"Unexpected or complex structure in {tf_file}, which may not be fully supported by the script.")

    return compliance_report

def grade_compliance(compliance_report):
    """Assign a grade based on compliance percentage."""
    total_resources = len(compliance_report)
    compliant_resources = sum(status == 'Compliant' for status in compliance_report.values())

    if total_resources == 0:
        return "Grade: N/A (No resources found)"

    compliance_percentage = (compliant_resources / total_resources) * 100

    # Define grade thresholds
    if compliance_percentage == 100:
        grade = "A"
    elif 90 <= compliance_percentage < 100:
        grade = "B"
    elif 80 <= compliance_percentage < 90:
        grade = "C"
    elif 70 <= compliance_percentage < 80:
        grade = "D"
    else:
        grade = "F"

    # Return a detailed grade statement
    return f"Grade: {grade} ({compliance_percentage:.2f}% compliant - {compliant_resources}/{total_resources} resources)"

def main():
    yaml_file_paths = get_yaml_file_paths(YAML_DIRECTORY_PATH)
    terraform_configs = read_terraform_files(TERRAFORM_DIRECTORY_PATH)
    
    for yaml_file_path in yaml_file_paths:
        logging.info(f"Grading against: {yaml_file_path}")
        yaml_criteria = parse_yaml(yaml_file_path)
        if yaml_criteria:
            compliance_report = evaluate_compliance(terraform_configs, yaml_criteria)
            grade = grade_compliance(compliance_report)
            logging.info(grade)
        print(grade)
        
        # Print detailed compliance report
        for resource_id, details in compliance_report.items():
            print(f"\nResource ID: {resource_id}")
            print(f"Compliance Status: {details['compliance_status']}")
            if details['non_compliant_properties']:
                print("Non-Compliant Properties:")
                for property_name in details['non_compliant_properties']:
                    print(f"- {property_name}")
            else:
                print("All properties compliant.")
        else:
            logging.warning(f"Skipping grading for {yaml_file_path} due to parsing errors.")

if __name__ == "__main__":
    main()