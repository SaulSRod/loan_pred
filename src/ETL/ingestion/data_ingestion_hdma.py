import os
from pathlib import Path
import pandas as pd
import shutil
import csv
import kaggle
import random

#gather data from a specific csv file and return as a pandas df
def initialize_data_path():
    """
    Returns a path object pointing to the 'training data' folder
    
    This function will always return the ABSOLUTE path IF called from this module

    """
    root = Path(__file__).resolve().parent.parent.parent

    DATA = root / "training_data"

    #Make sure training_data folder exists
    DATA.mkdir(parents= True, exist_ok= True)
    return DATA

def remove_extremes(df = pd.DataFrame()):
    """
    Function that removes nonsense values (negative income or loan amount, etc)
    """

    values = [
        'loan_amount', 'loan_term', 'debt_to_income_ratio', 'loan_to_value_ratio', 'income'
    ]

    filtered = df.copy()

    for col in values:
        filtered = filtered[filtered[col] >= 0]
        
    return filtered

def clean_data(df = pd.DataFrame(), sample = bool, seed = int): 
    """
    Helper function made to clean the HDMA dataframes
    """
    int_values = [
        'activity_year', 'action_taken', 'preapproval', 'loan_purpose', 'loan_amount', 'loan_term', 'applicant_credit_score_type',
        'co_applicant_credit_score_type', 'debt_to_income_ratio'
    ]

    float_values = [
        'loan_to_value_ratio', 'income'
    ]

    string_values = [
        'derived_loan_product_type'
    ]

    #Fix the income to be in thousands value
    df['income'] = df['income'] * 1000

    #Fix any columns that have values in the form 'Exempt'
    exempt_cols = ['debt_to_income_ratio', 'income', 'loan_term', 'loan_to_value_ratio']
    for columns in exempt_cols:
        df[columns] = df[columns].replace({'Exempt': None})
    
    #Fix the 1111's in denial reason
    if "denial_reason_1" in df.columns:
        df["denial_reason_1"] = df["denial_reason_1"].replace(1111, 1)
        df["denial_reason_1"] = df["denial_reason_1"].fillna(df["denial_reason_1"].value_counts().reset_index().iat[0, 0])
        try:
            df["denial_reason_1"] = df["denial_reason_1"].astype('int64')

        except Exception as e:
            print(f"skipping int conversion: denial_reason_1 due to error: {e}") 
    
    #Convert any ranges in the debt_income cat into the middle of that range, or leave it at that range if its too broad
    df['debt_to_income_ratio'] = df['debt_to_income_ratio'].replace(">60%", 62)
    df['debt_to_income_ratio'] = df['debt_to_income_ratio'].replace("<20%", 19)
    df['debt_to_income_ratio'] = df['debt_to_income_ratio'].replace("50%-60%", 55)
    df['debt_to_income_ratio'] = df['debt_to_income_ratio'].replace("20%-<30%", (29+20)//2)
    df['debt_to_income_ratio'] = df['debt_to_income_ratio'].replace("30%-<36%", (35+30)//2)
    
    #replace int values with mode since the values are all whole numbers
    for column in int_values:
        df[column] = df[column].fillna(df[column].value_counts().reset_index().iat[0, 0])
        try:
            df[column] = df[column].astype('int64')

        except Exception as e:
            print(f"skipping int conversion: {column} due to error: {e}") 
            continue
        
    #Fix float columns by replacing NA's with mean 
    for column in float_values:
        try:
            df[column] = pd.to_numeric(df[column], errors='coerce')
        except Exception as e:
            print(f"error when trying to convert {column} to int: {e}")
            continue
        
        try:
            mean = df[column].mean()
            #print(f"mean of {column} is {mean}")
            df[column] = df[column].fillna(mean)
        except Exception as e:
            print(f"skipping float mean: {column} due to error: {e}") 
            continue

    #Fix string columns by replacing with mode
    for column in string_values:
        df[column] = df[column].fillna(df[column].value_counts().reset_index().iat[0, 0])

    cleaned = remove_extremes(df.copy())

    try:
        if sample is True and seed != 0:
                #Create a random seed for sampling the large dataset if no seed is provided
                return cleaned.sample(200000, random_state = seed)
        elif sample is True:
                seed = random.randint(0,999)
                print(f"Random seed to replicate accepted loans df: {seed}")
                return cleaned.sample(200000, random_state = seed)
        else:
            print(f"Sample input was set --> {sample}, thus the entire dataset will be returned")
            return cleaned
    except Exception as e:
        print(f"Error when attempting to get the dataframe cleaned up : {e}")
        return

def read_hdma(file = Path):
    """
    Helper function that retrieves specific data from the gzip files
    Params:
        DATA : Path object that points to the 'training data' folder
    """
    filtered_columns = [
        'activity_year', 'action_taken', 'preapproval', 'loan_purpose', 'loan_amount', 'loan_term', 'applicant_credit_score_type',
        'co-applicant_credit_score_type' , 'denial_reason-1', 'loan_to_value_ratio', 'income', 'debt_to_income_ratio',
        'derived_loan_product_type' 
    ]

    if not file.exists():
        raise FileNotFoundError(f"HDMA file not found: {file}")
    
    df = pd.read_parquet(file)

    #checks whats missing
    missing = [c for c in filtered_columns if c not in df.columns]
    if missing:
        print(f"[read_hdma] missing columns in {file.name}: {missing}")
    present_cols = [c for c in filtered_columns if c in df.columns]

    if not present_cols:
        raise ValueError(
            f"[read_hdma] no HDMA columns found in {file.name}. "
            f"Available columns: {list(df.columns)[:20]} ..."
        )
    
    df_recovered = df[present_cols].copy()

    for col in missing:
        df_recovered[col] = pd.NA

    # problematic names
    renamer = {}

    if "denial_reason-1" in df_recovered.columns:
        renamer["denial_reason-1"] = "denial_reason_1"

    if "co-applicant_credit_score_type" in df_recovered.columns:
        renamer["co-applicant_credit_score_type"] = "co_applicant_credit_score_type"

    if renamer:
        df_recovered.rename(columns=renamer, inplace=True)

    return df_recovered

def clean_hdma_rejected(sample = True, seed = 0):
    """
    Function that reads the parquet.gzip file to return a cleaned dataframe with only rejected loans in the US during 2023
    https://ffiec.cfpb.gov/documentation/publications/loan-level-datasets/lar-data-fields#loan_amount
    The link above provides details in regards to each column
    Params:
        sample = True or False value. If true return a df with 200000 entries, else return all values in data (2 mil +)
        seed (random seed is default) : integer between 0 and 999, used to replicate pd.random_sample output for debugging. If no seed is passed a random one will be generated
    """
    try:
        DATA = initialize_data_path()
        hdma_rejected_parquet = DATA / 'hdma_rejected_raw.parquet.gzip'
        
        rejected_df = read_hdma(hdma_rejected_parquet)
        rejected_cleaned = clean_data(rejected_df, sample, seed)
        return rejected_cleaned
    except Exception as e:
        print(f"Error when retrieving rejected HDMA as a df: {e}")
        print(f"using: {DATA}")

def clean_hdma_accepted(sample = True, seed = 0):
    """
    Function that reads the parquet.gzip file to return a cleaned dataframe with only rejected loans in the US during 2023
    https://ffiec.cfpb.gov/documentation/publications/loan-level-datasets/lar-data-fields#loan_amount
    The link above provides details in regards to each column
    Params:
        sample = True or False value. If true return a df with 200000 entries, else return all values in data (3 mil +)
        seed (random seed is default) : integer between 0 and 999, used to replicate pd.random_sample output for debugging. If no seed is passed a random one will be generated
    """
    try:
        DATA = initialize_data_path()
        hdma_accepted_parquet = DATA / 'hdma_accepted_raw.parquet.gzip'
        accepted_df = read_hdma(hdma_accepted_parquet)
        accepted_cleaned = clean_data(accepted_df, sample, seed)
        return accepted_cleaned.drop(columns=['denial_reason_1'])
    except Exception as e:
        print(f"Error when retrieving accepted HDMA as a df in data_ingestion_hdma.py: {e}")


if __name__ == "__main__":
    print(initialize_data_path())