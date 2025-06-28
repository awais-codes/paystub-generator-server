# templates/utils/w2_field_map.py

# W2 Form Field Mapping
# Map your business field names to the PDF field names below
# 
# All detected PDF fields from your W2 template:
# - f1_01[0] (Type: /Tx) - Text field
# - f1_02[0] (Type: /Tx) - Text field  
# - f1_03[0] (Type: /Tx) - Text field
# - f1_04[0] (Type: /Tx) - Text field
# - f1_05[0] (Type: /Tx) - Text field
# - f1_06[0] (Type: /Tx) - Text field
# - f1_07[0] (Type: /Tx) - Text field
# - f1_08[0] (Type: /Tx) - Text field
# - f1_09[0] (Type: /Tx) - Text field
# - f1_10[0] (Type: /Tx) - Text field
# - f1_11[0] (Type: /Tx) - Text field
# - f1_12[0] (Type: /Tx) - Text field
# - f1_13[0] (Type: /Tx) - Text field
# - f1_14[0] (Type: /Tx) - Text field
# - f1_15[0] (Type: /Tx) - Text field
# - f1_16[0] (Type: /Tx) - Text field
# - f1_17[0] (Type: /Tx) - Text field
# - f1_18[0] (Type: /Tx) - Text field
# - f1_19[0] (Type: /Tx) - Text field
# - f1_20[0] (Type: /Tx) - Text field
# - f1_21[0] (Type: /Tx) - Text field
# - f1_22[0] (Type: /Tx) - Text field
# - f1_23[0] (Type: /Tx) - Text field
# - f1_24[0] (Type: /Tx) - Text field
# - f1_25[0] (Type: /Tx) - Text field
# - f1_26[0] (Type: /Tx) - Text field
# - f1_27[0] (Type: /Tx) - Text field
# - f1_28[0] (Type: /Tx) - Text field
# - f1_29[0] (Type: /Tx) - Text field
# - f1_30[0] (Type: /Tx) - Text field
# - f1_31[0] (Type: /Tx) - Text field
# - f1_32[0] (Type: /Tx) - Text field
# - f1_33[0] (Type: /Tx) - Text field
# - f1_34[0] (Type: /Tx) - Text field
# - f1_35[0] (Type: /Tx) - Text field
# - f1_36[0] (Type: /Tx) - Text field
# - f1_37[0] (Type: /Tx) - Text field
# - f1_38[0] (Type: /Tx) - Text field
# - f1_39[0] (Type: /Tx) - Text field
# - f1_40[0] (Type: /Tx) - Text field
# - f1_41[0] (Type: /Tx) - Text field
# - f1_42[0] (Type: /Tx) - Text field
# - f2_01[0] (Type: /Tx) - Text field
# - f2_02[0] (Type: /Tx) - Text field
# - f2_03[0] (Type: /Tx) - Text field
# - f2_04[0] (Type: /Tx) - Text field
# - f2_05[0] (Type: /Tx) - Text field
# - f2_06[0] (Type: /Tx) - Text field
# - f2_07[0] (Type: /Tx) - Text field
# - f2_08[0] (Type: /Tx) - Text field
# - f2_09[0] (Type: /Tx) - Text field
# - f2_10[0] (Type: /Tx) - Text field
# - f2_11[0] (Type: /Tx) - Text field
# - f2_12[0] (Type: /Tx) - Text field
# - f2_13[0] (Type: /Tx) - Text field
# - f2_14[0] (Type: /Tx) - Text field
# - f2_15[0] (Type: /Tx) - Text field
# - f2_16[0] (Type: /Tx) - Text field
# - f2_17[0] (Type: /Tx) - Text field
# - f2_18[0] (Type: /Tx) - Text field
# - f2_19[0] (Type: /Tx) - Text field
# - f2_20[0] (Type: /Tx) - Text field
# - f2_21[0] (Type: /Tx) - Text field
# - f2_22[0] (Type: /Tx) - Text field
# - f2_23[0] (Type: /Tx) - Text field
# - f2_24[0] (Type: /Tx) - Text field
# - f2_25[0] (Type: /Tx) - Text field
# - f2_26[0] (Type: /Tx) - Text field
# - f2_27[0] (Type: /Tx) - Text field
# - f2_28[0] (Type: /Tx) - Text field
# - f2_29[0] (Type: /Tx) - Text field
# - f2_30[0] (Type: /Tx) - Text field
# - f2_31[0] (Type: /Tx) - Text field
# - f2_32[0] (Type: /Tx) - Text field
# - f2_33[0] (Type: /Tx) - Text field
# - f2_34[0] (Type: /Tx) - Text field
# - f2_35[0] (Type: /Tx) - Text field
# - f2_36[0] (Type: /Tx) - Text field
# - f2_37[0] (Type: /Tx) - Text field
# - f2_38[0] (Type: /Tx) - Text field
# - f2_39[0] (Type: /Tx) - Text field
# - f2_40[0] (Type: /Tx) - Text field
# - f2_41[0] (Type: /Tx) - Text field
# - f2_42[0] (Type: /Tx) - Text field
# - c1_1[0] (Type: /Btn) - Button/Checkbox field
# - c1_2[0] (Type: /Btn) - Button/Checkbox field
# - c1_3[0] (Type: /Btn) - Button/Checkbox field
# - c1_4[0] (Type: /Btn) - Button/Checkbox field
# - c2_1[0] (Type: /Btn) - Button/Checkbox field
# - c2_2[0] (Type: /Btn) - Button/Checkbox field
# - c2_3[0] (Type: /Btn) - Button/Checkbox field
# - c2_4[0] (Type: /Btn) - Button/Checkbox field
#
# Non-fillable fields (for reference):
# - topmostSubform[0] (Type: Unknown)
# - CopyA[0] (Type: Unknown)
# - Void_ReadOrder[0] (Type: Unknown)
# - BoxA_ReadOrder[0] (Type: Unknown)
# - Col_Left[0] (Type: Unknown)
# - FirstName_ReadOrder[0] (Type: Unknown)
# - LastName_ReadOrder[0] (Type: Unknown)
# - Col_Right[0] (Type: Unknown)
# - Box1_ReadOrder[0] (Type: Unknown)
# - Box3_ReadOrder[0] (Type: Unknown)
# - Box5_ReadOrder[0] (Type: Unknown)
# - Box7_ReadOrder[0] (Type: Unknown)
# - Box9_ReadOrder[0] (Type: Unknown)
# - Box11_ReadOrder[0] (Type: Unknown)
# - Line12_ReadOrder[0] (Type: Unknown)
# - Statutory_ReadOrder[0] (Type: Unknown)
# - Retirement_ReadOrder[0] (Type: Unknown)
# - Boxes15_ReadOrder[0] (Type: Unknown)
# - Box15_ReadOrder[0] (Type: Unknown)
# - Box16_ReadOrder[0] (Type: Unknown)
# - Box17_ReadOrder[0] (Type: Unknown)
# - Box18_ReadOrder[0] (Type: Unknown)
# - Box19_ReadOrder[0] (Type: Unknown)
# - Copy1[0] (Type: Unknown)
# - Box11__ReadOrder[0] (Type: Unknown)
# - Box12_ReadOrder[0] (Type: Unknown)
# - CopyB[0] (Type: Unknown)
# - CopyC[0] (Type: Unknown)
# - Copy2[0] (Type: Unknown)
# - CopyD[0] (Type: Unknown)
#
# Instructions:
# 1. Open your W2 PDF in a PDF editor (like Adobe Acrobat or PDF-XChange Editor)
# 2. Click on each field to see its name in the properties
# 3. Map the business field names below to the corresponding PDF field names
# 4. Uncomment and fill in the mappings below

FIELD_MAP = {
    # Example mappings (uncomment and modify as needed):
    'employee_ssn': 'f1_01[0]',
    'employee_ein': 'f1_02[0]',
    'employer_name_address_zip': 'f1_03[0]',
    'control_number': 'f1_04[0]',
    'firt_name_and_initial': 'f1_05[0]',
    'last_name': 'f1_06[0]',
    'stuff': 'f1_07[0]',
    'adress_and_code': 'f1_08[0]',
    'wages_tips': 'f1_09[0]',
    'fed_income_tax_withheld': 'f1_10[0]',
    'social_security_wages': 'f1_11[0]',
    'social_security_wages_withheld': 'f1_12[0]',
    'medicare_wages': 'f1_13[0]',
    'medicare_tax_witheld': 'f1_14[0]',
    'social_security_tips': 'f1_15[0]',
    'allocated_tips': 'f1_16[0]',
    # 'deferrals_401k': 'f1_17[0]',
    'dependent_care_benefits': 'f1_18[0]',
    'non_qualified_plans': 'f1_19[0]',
    'twelve_a_0': 'f1_20[0]',
    'twelve_a_1': 'f1_21[0]',
    'twelve_b_0': 'f1_22[0]',
    'twelve_b_1': 'f1_23[0]',
    'twelve_c_0': 'f1_24[0]',
    'twelve_c_1': 'f1_25[0]',
    'twelve_d_0': 'f1_26[0]',
    'twelve_d_1': 'f1_27[0]',
    'other': 'f1_28[0]',
    'state_1': 'f1_29[0]',
    'state_1_employee_id': 'f1_30[0]',
    'state_2': 'f1_31[0]',
    'state_2_employee_id': 'f1_32[0]',
    'state_1_wages_tips': 'f1_33[0]',
    'state_2_wages_tips': 'f1_34[0]',
    'state_1_income_tax': 'f1_35[0]',
    'state_2_income_tax': 'f1_36[0]',
    'state_1_local_wages_tips': 'f1_37[0]',
    'state_2_local_wages_tips': 'f1_38[0]',
    'state_1_local_income_tax': 'f1_39[0]',
    'state_2_local_income_tax': 'f1_40[0]',
    'state_1_locality_name': 'f1_41[0]',
    'state_2_locality_name': 'f1_42[0]',
    'void': 'c1_1[0]',
    'statutory_employee': 'c1_2[0]',
    'retirement_plan': 'c1_3[0]',
    'third_party_sick_pay': 'c1_4[0]',
    
    # f2_* fields following the same pattern (likely for additional copies or sections)
    'employee_ssn_2': 'f2_01[0]',
    'employee_ein_2': 'f2_02[0]',
    'employer_name_address_zip_2': 'f2_03[0]',
    'control_number_2': 'f2_04[0]',
    'firt_name_and_initial_2': 'f2_05[0]',
    'last_name_2': 'f2_06[0]',
    'stuff_2': 'f2_07[0]',
    'adress_and_code_2': 'f2_08[0]',
    'wages_tips_2': 'f2_09[0]',
    'fed_income_tax_withheld_2': 'f2_10[0]',
    'social_security_wages_2': 'f2_11[0]',
    'social_security_wages_withheld_2': 'f2_12[0]',
    'medicare_wages_2': 'f2_13[0]',
    'medicare_tax_witheld_2': 'f2_14[0]',
    'social_security_tips_2': 'f2_15[0]',
    'allocated_tips_2': 'f2_16[0]',
    # 'deferrals_401k_2': 'f2_17[0]',
    'dependent_care_benefits_2': 'f2_18[0]',
    'non_qualified_plans_2': 'f2_19[0]',
    'twelve_a_0_2': 'f2_20[0]',
    'twelve_a_1_2': 'f2_21[0]',
    'twelve_b_0_2': 'f2_22[0]',
    'twelve_b_1_2': 'f2_23[0]',
    'twelve_c_0_2': 'f2_24[0]',
    'twelve_c_1_2': 'f2_25[0]',
    'twelve_d_0_2': 'f2_26[0]',
    'twelve_d_1_2': 'f2_27[0]',
    'other_2': 'f2_28[0]',
    'state_1_2': 'f2_29[0]',
    'state_1_employee_id_2': 'f2_30[0]',
    'state_2_2': 'f2_31[0]',
    'state_2_employee_id_2': 'f2_32[0]',
    'state_1_wages_tips_2': 'f2_33[0]',
    'state_2_wages_tips_2': 'f2_34[0]',
    'state_1_income_tax_2': 'f2_35[0]',
    'state_2_income_tax_2': 'f2_36[0]',
    'state_1_local_wages_tips_2': 'f2_37[0]',
    'state_2_local_wages_tips_2': 'f2_38[0]',
    'state_1_local_income_tax_2': 'f2_39[0]',
    'state_2_local_income_tax_2': 'f2_40[0]',
    'state_1_locality_name_2': 'f2_41[0]',
    'state_2_locality_name_2': 'f2_42[0]',
    'void_2': 'c2_1[0]',
    'statutory_employee_2': 'c2_2[0]',
    'retirement_plan_2': 'c2_3[0]',
    'third_party_sick_pay_2': 'c2_4[0]',
} 