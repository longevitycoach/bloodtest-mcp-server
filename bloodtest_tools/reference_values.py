"""
Reference values for blood test parameters based on Dr. Ulrich Strunz and Dr. med. Helena Orfanos-Boeckel.
"""
from typing import Dict, Optional, Union, List
from dataclasses import dataclass
from enum import Enum

class Sex(str, Enum):
    MALE = "male"
    FEMALE = "female"

@dataclass
class ReferenceRange:
    """Represents a reference range for a blood test parameter."""
    optimal: str = ""
    classical: str = ""
    explanation: str = ""
    unit: str = ""
    women: Optional[str] = None
    men: Optional[str] = None
    
    def __post_init__(self):
        # Ensure required fields are set
        required_fields = {
            'optimal': self.optimal,
            'classical': self.classical,
            'explanation': self.explanation,
            'unit': self.unit
        }
        missing = [field for field, value in required_fields.items() if not value]
        if missing:
            raise ValueError(f"Missing required fields in ReferenceRange: {', '.join(missing)}")

# Reference values data structure
REFERENCE_VALUES: Dict[str, ReferenceRange] = {
    "ferritin": ReferenceRange(
        optimal="70–200 (optimal)",
        women="premenopausal: 15–150, postmenopausal: 15–300, optimal: 70–200",
        men="30–400, optimal: 100–300",
        classical="15-400 depending on sex and age",
        explanation="Iron storage protein; reflects total body iron stores. Low levels indicate iron deficiency before anemia develops. High levels may indicate inflammation, infection, or iron overload conditions.",
        unit="ng/ml"
    ),
    "tsh": ReferenceRange(
        optimal="0.5–2.5",
        women="0.5–2.5 (optimal)",
        men="0.5–2.5 (optimal)",
        classical="0.4–4.0, optimal 0.5–2.5",
        explanation="Thyroid-stimulating hormone. Optimal levels are lower than classical reference ranges. Higher levels may indicate subclinical hypothyroidism.",
        unit="mIU/l"
    ),
    "vitamin_d": ReferenceRange(
        optimal="50–70",
        women="50–70 (optimal)",
        men="50–70 (optimal)",
        classical="10–100, optimal higher",
        explanation="Essential for calcium absorption, bone health, immune function, and gene expression. Influences over 2000 genes and has receptor sites in nearly every cell. Deficiency linked to numerous chronic diseases.",
        unit="ng/ml"
    ),
    "vitamin_b12": ReferenceRange(
        optimal=">100",
        women=">100",
        men=">100",
        classical="37.5–150",
        explanation="Critical for nerve function, DNA synthesis, and red blood cell formation. Functional deficiency can occur even with 'normal' levels; active B12 (holotranscobalamin) is more accurate.",
        unit="pmol/l"
    ),
    "folate_rbc": ReferenceRange(
        optimal=">16",
        women=">16",
        men=">16",
        classical="4.5–20",
        explanation="Crucial for DNA synthesis, repair, and methylation. Works synergistically with B12. Important for cardiovascular health through homocysteine regulation.",
        unit="ng/ml"
    ),
    "zinc": ReferenceRange(
        optimal="6–7",
        women="6–7",
        men="6–7",
        classical="4.5–7.5",
        explanation="Essential for immune function, protein synthesis, wound healing, DNA synthesis, and cell division. Cofactor for over 300 enzymes. Serum levels may not reflect tissue status.",
        unit="mg/l"
    ),
    "magnesium": ReferenceRange(
        optimal="0.85–1.0",
        women="0.85–1.0",
        men="0.85–1.0",
        classical="0.75–1.0",
        explanation="Required for over 600 enzymatic reactions. Critical for energy production, muscle function, nerve transmission, and bone formation. Serum levels represent only 1% of body magnesium.",
        unit="mmol/l"
    ),
    "selenium": ReferenceRange(
        optimal="140–160",
        women="140–160",
        men="140–160",
        classical="100–140",
        explanation="Antioxidant mineral essential for thyroid hormone metabolism, immune function, and fertility. Component of glutathione peroxidase enzymes that protect against oxidative damage.",
        unit="µg/l"
    )
}

def get_reference_range(parameter: str, sex: Optional[Sex] = None) -> Dict[str, Union[str, None]]:
    """
    Get the reference range for a specific blood test parameter.
    
    Args:
        parameter: The blood test parameter to look up (case-insensitive).
        sex: Optional sex of the patient for sex-specific reference ranges.
        
    Returns:
        Dictionary containing reference range information.
        
    Raises:
        ValueError: If the parameter is not found in the reference values.
    """
    param_lower = parameter.lower()
    
    # Handle common parameter name variations
    param_aliases = {
        'ferritin': 'ferritin',
        'tsh': 'tsh',
        'vitamin d': 'vitamin_d',
        'vitamind': 'vitamin_d',
        '25-oh vitamin d': 'vitamin_d',
        '25ohd': 'vitamin_d',
        'vitamin b12': 'vitamin_b12',
        'b12': 'vitamin_b12',
        'folate': 'folate_rbc',
        'rbc folate': 'folate_rbc',
        'zinc': 'zinc',
        'magnesium': 'magnesium',
        'selenium': 'selenium'
    }
    
    # Find the canonical parameter name
    canonical_param = param_aliases.get(param_lower)
    if not canonical_param:
        # Try direct match if no alias found
        canonical_param = param_lower.replace(' ', '_')
    
    if canonical_param not in REFERENCE_VALUES:
        raise ValueError(f"Parameter '{parameter}' not found in reference values")
    
    ref_range = REFERENCE_VALUES[canonical_param]
    
    # Prepare the result
    result = {
        'parameter': parameter,
        'unit': ref_range.unit,
        'optimal_range': ref_range.optimal,
        'classical_range': ref_range.classical,
        'explanation': ref_range.explanation,
        'sex_specific': bool(ref_range.women or ref_range.men)
    }
    
    # Add sex-specific ranges if available
    if sex == Sex.FEMALE and ref_range.women:
        result['sex_specific_range'] = ref_range.women
    elif sex == Sex.MALE and ref_range.men:
        result['sex_specific_range'] = ref_range.men
    
    return result

def list_available_parameters() -> List[Dict[str, str]]:
    """
    Get a list of all available blood test parameters with their units.
    
    Returns:
        List of dictionaries containing parameter names and units.
    """
    return [
        {"parameter": param, "unit": ref.unit}
        for param, ref in REFERENCE_VALUES.items()
    ]
