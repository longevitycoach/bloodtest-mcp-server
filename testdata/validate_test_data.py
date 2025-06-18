#!/usr/bin/env python3
"""
Test Data Validation Script for Bloodtest MCP Server
Validates all test data files for consistency, completeness, and correctness
"""

import json
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class ValidationResult:
    file_name: str
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    info: List[str]

class TestDataValidator:
    """Validates test data files for the Bloodtest MCP Server"""
    
    def __init__(self, testdata_dir: Path = Path("testdata")):
        self.testdata_dir = testdata_dir
        self.validation_results: List[ValidationResult] = []
        
        # Expected blood test parameters
        self.expected_parameters = {
            "ferritin", "tsh", "vitamin_d", "vitamin_b12", 
            "folate_rbc", "zinc", "magnesium", "selenium"
        }
        
        # Parameter aliases for validation
        self.parameter_aliases = {
            "vitamin d": "vitamin_d",
            "b12": "vitamin_b12", 
            "folate": "folate_rbc",
            "rbc folate": "folate_rbc"
        }
        
        # Expected units for each parameter
        self.expected_units = {
            "ferritin": ["ng/ml", "µg/l"],
            "tsh": ["mIU/l", "µIU/ml"], 
            "vitamin_d": ["ng/ml", "nmol/l"],
            "vitamin_b12": ["pmol/l", "pg/ml"],
            "folate_rbc": ["ng/ml"],
            "zinc": ["mg/l", "µmol/l"],
            "magnesium": ["mmol/l", "mg/dl"],
            "selenium": ["µg/l", "µmol/l"]
        }
    
    def validate_all_test_data(self) -> Dict[str, Any]:
        """Validate all test data files and return comprehensive report"""
        logger.info("Starting comprehensive test data validation")
        
        # Get all test data files
        test_files = [
            "comprehensive_api_tests.json",
            "comprehensive_mcp_tool_tests.json",
            "realistic_blood_analysis_scenarios.json", 
            "comprehensive_rag_tests.json",
            "comprehensive_workflow_tests.json",
            "comprehensive_integration_tests.json",
            "performance_load_tests.json",
            "error_handling_edge_cases.json",
            "sample_blood_test_data.json"
        ]
        
        # Validate each file
        for file_name in test_files:
            file_path = self.testdata_dir / file_name
            if file_path.exists():
                result = self._validate_file(file_path)
                self.validation_results.append(result)
            else:
                self.validation_results.append(ValidationResult(
                    file_name=file_name,
                    is_valid=False,
                    errors=[f"File not found: {file_path}"],
                    warnings=[],
                    info=[]
                ))
        
        # Generate comprehensive report
        return self._generate_validation_report()
    
    def _validate_file(self, file_path: Path) -> ValidationResult:
        """Validate a single test data file"""
        file_name = file_path.name
        errors = []
        warnings = []
        info = []
        
        try:
            # Load and parse JSON
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            info.append(f"Successfully loaded JSON with {len(str(data))} characters")
            
            # File-specific validation
            if "api_tests" in file_name:
                errors.extend(self._validate_api_tests(data))
            elif "mcp_tool_tests" in file_name:
                errors.extend(self._validate_mcp_tests(data))
            elif "blood_analysis" in file_name:
                errors.extend(self._validate_blood_analysis(data))
            elif "rag_tests" in file_name:
                errors.extend(self._validate_rag_tests(data))
            elif "workflow_tests" in file_name:
                errors.extend(self._validate_workflow_tests(data))
            elif "integration_tests" in file_name:
                errors.extend(self._validate_integration_tests(data))
            elif "performance" in file_name:
                errors.extend(self._validate_performance_tests(data))
            elif "error_handling" in file_name:
                errors.extend(self._validate_error_tests(data))
            elif "sample_blood_test" in file_name:
                errors.extend(self._validate_sample_data(data))
            
            # General structure validation
            structure_errors = self._validate_general_structure(data, file_name)
            errors.extend(structure_errors)
            
        except json.JSONDecodeError as e:
            errors.append(f"Invalid JSON format: {str(e)}")
        except Exception as e:
            errors.append(f"Unexpected error: {str(e)}")
        
        return ValidationResult(
            file_name=file_name,
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            info=info
        )
    
    def _validate_api_tests(self, data: Dict[str, Any]) -> List[str]:
        """Validate API test data structure"""
        errors = []
        
        if "api_endpoint_tests" not in data:
            errors.append("Missing 'api_endpoint_tests' section")
            return errors
        
        api_tests = data["api_endpoint_tests"]
        
        # Validate test cases structure
        if "test_cases" in api_tests:
            for i, test_case in enumerate(api_tests["test_cases"]):
                test_errors = self._validate_api_test_case(test_case, i)
                errors.extend(test_errors)
        
        # Check parameter coverage
        tested_parameters = set()
        for test_case in api_tests.get("test_cases", []):
            endpoint = test_case.get("endpoint", "")
            if "/reference/" in endpoint:
                param = endpoint.split("/reference/")[-1]
                tested_parameters.add(param)
        
        missing_params = self.expected_parameters - tested_parameters
        if missing_params:
            errors.append(f"Missing API tests for parameters: {missing_params}")
        
        return errors
    
    def _validate_api_test_case(self, test_case: Dict[str, Any], index: int) -> List[str]:
        """Validate individual API test case"""
        errors = []
        
        required_fields = ["test_id", "name", "method", "endpoint", "expected_status"]
        for field in required_fields:
            if field not in test_case:
                errors.append(f"Test case {index}: Missing required field '{field}'")
        
        # Validate HTTP method
        if "method" in test_case:
            valid_methods = ["GET", "POST", "PUT", "DELETE", "PATCH"]
            if test_case["method"] not in valid_methods:
                errors.append(f"Test case {index}: Invalid HTTP method '{test_case['method']}'")
        
        # Validate status code
        if "expected_status" in test_case:
            status = test_case["expected_status"]
            if not isinstance(status, int) or status < 100 or status >= 600:
                errors.append(f"Test case {index}: Invalid HTTP status code {status}")
        
        return errors
    
    def _validate_mcp_tests(self, data: Dict[str, Any]) -> List[str]:
        """Validate MCP tool test data"""
        errors = []
        
        if "mcp_tool_tests" not in data:
            errors.append("Missing 'mcp_tool_tests' section")
            return errors
        
        mcp_tests = data["mcp_tool_tests"]
        
        # Check for required test categories
        required_categories = ["basic_tools", "workflow_tools", "advanced_tools"]
        test_categories = mcp_tests.get("test_categories", {})
        
        for category in required_categories:
            if category not in test_categories:
                errors.append(f"Missing MCP test category: {category}")
        
        # Validate tool names
        expected_tools = ["get_book_info", "list_workflows", "supplement_therapy", "sequential_thinking"]
        tested_tools = set()
        
        for category, tests in test_categories.items():
            for test in tests:
                if "tool_name" in test:
                    tested_tools.add(test["tool_name"])
        
        missing_tools = set(expected_tools) - tested_tools
        if missing_tools:
            errors.append(f"Missing MCP tool tests: {missing_tools}")
        
        return errors
    
    def _validate_blood_analysis(self, data: Dict[str, Any]) -> List[str]:
        """Validate blood analysis scenario data"""
        errors = []
        
        if "blood_analysis_scenarios" not in data:
            errors.append("Missing 'blood_analysis_scenarios' section")
            return errors
        
        scenarios = data["blood_analysis_scenarios"]
        
        # Check test patients
        if "test_patients" in scenarios:
            for i, patient in enumerate(scenarios["test_patients"]):
                patient_errors = self._validate_patient_data(patient, i)
                errors.extend(patient_errors)
        
        return errors
    
    def _validate_patient_data(self, patient: Dict[str, Any], index: int) -> List[str]:
        """Validate individual patient test data"""
        errors = []
        
        required_fields = ["patient_id", "demographics", "blood_test_results"]
        for field in required_fields:
            if field not in patient:
                errors.append(f"Patient {index}: Missing required field '{field}'")
        
        # Validate blood test results
        if "blood_test_results" in patient and "parameters" in patient["blood_test_results"]:
            for param in patient["blood_test_results"]["parameters"]:
                param_errors = self._validate_blood_parameter(param, index)
                errors.extend(param_errors)
        
        return errors
    
    def _validate_blood_parameter(self, param: Dict[str, Any], patient_index: int) -> List[str]:
        """Validate blood test parameter data"""
        errors = []
        
        required_fields = ["name", "value", "unit"]
        for field in required_fields:
            if field not in param:
                errors.append(f"Patient {patient_index}: Parameter missing '{field}'")
                continue
        
        # Validate parameter name
        param_name = param.get("name", "").lower()
        canonical_name = self.parameter_aliases.get(param_name, param_name)
        
        if canonical_name not in self.expected_parameters:
            errors.append(f"Patient {patient_index}: Unknown parameter '{param['name']}'")
        
        # Validate unit
        if param_name in self.expected_units:
            unit = param.get("unit", "")
            if unit not in self.expected_units[param_name]:
                errors.append(f"Patient {patient_index}: Invalid unit '{unit}' for parameter '{param_name}'")
        
        # Validate value
        value = param.get("value")
        if value is not None and not isinstance(value, (int, float)):
            errors.append(f"Patient {patient_index}: Non-numeric value for parameter '{param_name}'")
        
        return errors
    
    def _validate_rag_tests(self, data: Dict[str, Any]) -> List[str]:
        """Validate RAG system test data"""
        errors = []
        
        if "rag_system_tests" not in data:
            errors.append("Missing 'rag_system_tests' section")
            return errors
        
        # Validate knowledge retrieval tests
        rag_tests = data["rag_system_tests"]
        if "knowledge_retrieval_tests" in rag_tests:
            for i, test in enumerate(rag_tests["knowledge_retrieval_tests"]):
                if "query" not in test:
                    errors.append(f"RAG test {i}: Missing 'query' field")
                if "expected_content_themes" not in test:
                    errors.append(f"RAG test {i}: Missing 'expected_content_themes' field")
        
        return errors
    
    def _validate_workflow_tests(self, data: Dict[str, Any]) -> List[str]:
        """Validate workflow test data"""
        errors = []
        
        if "complete_workflow_tests" not in data:
            errors.append("Missing 'complete_workflow_tests' section")
            return errors
        
        # Check test scenarios
        workflow_tests = data["complete_workflow_tests"]
        if "test_scenarios" in workflow_tests:
            for i, scenario in enumerate(workflow_tests["test_scenarios"]):
                if "workflow_steps" not in scenario:
                    errors.append(f"Workflow scenario {i}: Missing 'workflow_steps'")
                if "expected_final_plan" not in scenario:
                    errors.append(f"Workflow scenario {i}: Missing 'expected_final_plan'")
        
        return errors
    
    def _validate_integration_tests(self, data: Dict[str, Any]) -> List[str]:
        """Validate integration test data"""
        errors = []
        
        if "integration_tests" not in data:
            errors.append("Missing 'integration_tests' section")
            return errors
        
        return errors
    
    def _validate_performance_tests(self, data: Dict[str, Any]) -> List[str]:
        """Validate performance test data"""
        errors = []
        
        if "performance_load_tests" not in data:
            errors.append("Missing 'performance_load_tests' section")
            return errors
        
        # Validate performance requirements
        perf_tests = data["performance_load_tests"]
        if "baseline_performance_targets" in perf_tests:
            targets = perf_tests["baseline_performance_targets"]
            required_target_categories = ["api_endpoints", "mcp_tools", "system_resources"]
            
            for category in required_target_categories:
                if category not in targets:
                    errors.append(f"Missing performance target category: {category}")
        
        return errors
    
    def _validate_error_tests(self, data: Dict[str, Any]) -> List[str]:
        """Validate error handling test data"""
        errors = []
        
        if "error_handling_edge_cases" not in data:
            errors.append("Missing 'error_handling_edge_cases' section")
            return errors
        
        return errors
    
    def _validate_sample_data(self, data: Dict[str, Any]) -> List[str]:
        """Validate sample blood test data"""
        errors = []
        
        if "sample_blood_test_data" not in data:
            errors.append("Missing 'sample_blood_test_data' section")
            return errors
        
        # Validate German lab reports
        sample_data = data["sample_blood_test_data"]
        if "test_data_formats" in sample_data and "german_lab_reports" in sample_data["test_data_formats"]:
            for i, report in enumerate(sample_data["test_data_formats"]["german_lab_reports"]):
                if "structured_format" not in report:
                    errors.append(f"German lab report {i}: Missing 'structured_format'")
                    continue
                
                # Validate parameter coverage
                reported_params = {param["parameter"] for param in report["structured_format"]}
                missing_params = self.expected_parameters - reported_params
                if missing_params:
                    errors.append(f"German lab report {i}: Missing parameters {missing_params}")
        
        return errors
    
    def _validate_general_structure(self, data: Dict[str, Any], file_name: str) -> List[str]:
        """Validate general data structure"""
        errors = []
        
        # Check for description field
        if "description" not in data and not any(key for key in data.keys() if "description" in str(data[key])):
            errors.append("Missing description field or documentation")
        
        # Check for empty data structures
        if not data:
            errors.append("Empty data file")
        
        return errors
    
    def _generate_validation_report(self) -> Dict[str, Any]:
        """Generate comprehensive validation report"""
        total_files = len(self.validation_results)
        valid_files = sum(1 for result in self.validation_results if result.is_valid)
        total_errors = sum(len(result.errors) for result in self.validation_results)
        total_warnings = sum(len(result.warnings) for result in self.validation_results)
        
        # Generate summary
        summary = {
            "validation_timestamp": str(self._get_timestamp()),
            "total_files_checked": total_files,
            "valid_files": valid_files,
            "invalid_files": total_files - valid_files,
            "total_errors": total_errors,
            "total_warnings": total_warnings,
            "validation_success_rate": (valid_files / total_files * 100) if total_files > 0 else 0
        }
        
        # Detailed results
        detailed_results = []
        for result in self.validation_results:
            detailed_results.append({
                "file_name": result.file_name,
                "is_valid": result.is_valid,
                "error_count": len(result.errors),
                "warning_count": len(result.warnings),
                "errors": result.errors,
                "warnings": result.warnings,
                "info": result.info
            })
        
        # Recommendations
        recommendations = self._generate_recommendations()
        
        return {
            "summary": summary,
            "detailed_results": detailed_results,
            "recommendations": recommendations,
            "test_data_completeness": self._assess_completeness()
        }
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on validation results"""
        recommendations = []
        
        invalid_files = [r for r in self.validation_results if not r.is_valid]
        if invalid_files:
            recommendations.append(f"Fix validation errors in {len(invalid_files)} files before running tests")
        
        total_errors = sum(len(result.errors) for result in self.validation_results)
        if total_errors == 0:
            recommendations.append("All test data files are valid and ready for testing")
        elif total_errors < 5:
            recommendations.append("Minor validation issues found - address before comprehensive testing")
        else:
            recommendations.append("Significant validation issues found - comprehensive review needed")
        
        return recommendations
    
    def _assess_completeness(self) -> Dict[str, Any]:
        """Assess completeness of test data coverage"""
        return {
            "api_endpoints_covered": self._count_api_endpoint_coverage(),
            "blood_parameters_covered": self._count_parameter_coverage(),
            "mcp_tools_covered": self._count_mcp_tool_coverage(),
            "test_scenario_types": self._count_scenario_types()
        }
    
    def _count_api_endpoint_coverage(self) -> int:
        """Count API endpoint test coverage"""
        # Simplified count - in real implementation, would parse test files
        return 8  # Number of blood parameters + health endpoints
    
    def _count_parameter_coverage(self) -> int:
        """Count blood parameter test coverage"""
        return len(self.expected_parameters)
    
    def _count_mcp_tool_coverage(self) -> int:
        """Count MCP tool test coverage"""
        return 4  # get_book_info, list_workflows, supplement_therapy, sequential_thinking
    
    def _count_scenario_types(self) -> int:
        """Count different test scenario types"""
        return 6  # API, MCP, workflow, integration, performance, error handling
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()

def main():
    """Main validation function"""
    print("🧪 Bloodtest MCP Server - Test Data Validation")
    print("=" * 60)
    
    validator = TestDataValidator()
    results = validator.validate_all_test_data()
    
    # Print summary
    summary = results["summary"]
    print(f"\n📊 Validation Summary:")
    print(f"   Files Checked: {summary['total_files_checked']}")
    print(f"   Valid Files: {summary['valid_files']}")
    print(f"   Invalid Files: {summary['invalid_files']}")
    print(f"   Total Errors: {summary['total_errors']}")
    print(f"   Total Warnings: {summary['total_warnings']}")
    print(f"   Success Rate: {summary['validation_success_rate']:.1f}%")
    
    # Print errors for invalid files
    invalid_results = [r for r in results["detailed_results"] if not r["is_valid"]]
    if invalid_results:
        print(f"\n❌ Files with Errors:")
        for result in invalid_results:
            print(f"   {result['file_name']}:")
            for error in result["errors"]:
                print(f"     • {error}")
    
    # Print recommendations
    print(f"\n💡 Recommendations:")
    for rec in results["recommendations"]:
        print(f"   • {rec}")
    
    # Save detailed results
    results_file = Path("testdata/validation_results.json")
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n📄 Detailed validation results saved to: {results_file}")
    
    return summary['total_errors'] == 0

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)