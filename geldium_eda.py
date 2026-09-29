# Geldium Delinquency Risk Analytics — Exploratory Data Analysis
# Dataset: Geldium_PowerBI_Data.csv
# Author: Rushikesh
#
# Run:
#   pip install pandas numpy matplotlib seaborn jupyter
#   jupyter notebook
#
# This script is designed for a GitHub portfolio project.

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv("data/Geldium_PowerBI_Data.csv")

print("Shape:", df.shape)
print("\nData types:\n", df.dtypes)
print("\nMissing values:\n", df.isna().sum().sort_values(ascending=False))
print("\nDuplicate Customer IDs:", df["Customer_ID"].duplicated().sum())
print("\nTarget distribution:\n", df["Delinquent_Account"].value_counts())
print("\nDelinquency rate: {:.2f}%".format(df["Delinquent_Account"].mean()*100))

# ---------------- Data Quality ----------------
print("\nCredit utilization > 1:", (df["Credit_Utilization"] > 1).sum())
print("Income missing:", df["Income"].isna().sum())
print("Loan Balance missing:", df["Loan_Balance"].isna().sum())

# Cleaned working copy
eda = df.copy()
eda["Credit_Utilization_Clean"] = eda["Credit_Utilization"].clip(upper=1)
eda["Age_Group"] = pd.cut(
    eda["Age"], bins=[17,25,35,45,55,65,120],
    labels=["18-25","26-35","36-45","46-55","56-65","66+"]
)

def delinquency_by(col):
    out = eda.groupby(col, observed=False)["Delinquent_Account"].agg(
        customers="count", delinquent="sum", rate="mean"
    ).reset_index()
    out["rate"] *= 100
    return out.sort_values("rate", ascending=False)

print("\nAge group:\n", delinquency_by("Age_Group"))
print("\nEmployment:\n", delinquency_by("Employment_Status"))
print("\nCard type:\n", delinquency_by("Credit_Card_Type"))
print("\nLocation:\n", delinquency_by("Location"))
print("\nCredit score band:\n", delinquency_by("Credit_Score_Band"))

# ---------------- Correlation ----------------
numeric_cols = [
    "Age","Income","Credit_Score","Credit_Utilization",
    "Missed_Payments","Loan_Balance","Debt_to_Income_Ratio",
    "Account_Tenure"
]
corr = eda[numeric_cols + ["Delinquent_Account"]].corr(numeric_only=True)["Delinquent_Account"]\
       .drop("Delinquent_Account").sort_values()
print("\nCorrelation with delinquency:\n", corr)

# ---------------- Risk flag diagnostic ----------------
cm = pd.crosstab(eda["High_Risk_Flag"], eda["Delinquent_Account"])
print("\nHigh Risk Flag confusion table:\n", cm)

tp = ((eda["High_Risk_Flag"] == 1) & (eda["Delinquent_Account"] == 1)).sum()
fn = ((eda["High_Risk_Flag"] == 0) & (eda["Delinquent_Account"] == 1)).sum()
precision = tp / max((eda["High_Risk_Flag"] == 1).sum(), 1)
recall = tp / max((eda["Delinquent_Account"] == 1).sum(), 1)
print(f"\nHigh-risk precision: {precision:.2%}")
print(f"High-risk recall: {recall:.2%}")

# ---------------- Visual EDA ----------------
sns.set_theme(style="whitegrid")

plt.figure(figsize=(7,5))
sns.countplot(data=eda, x="Delinquent_Account")
plt.title("Delinquent vs Non-Delinquent Customers")
plt.xlabel("Delinquent Account (0=No, 1=Yes)")
plt.ylabel("Customers")
plt.tight_layout()
plt.savefig("outputs/01_delinquency_distribution.png", dpi=160)
plt.close()

age = delinquency_by("Age_Group")
plt.figure(figsize=(9,5))
sns.barplot(data=age, x="Age_Group", y="rate")
plt.title("Delinquency Rate by Age Group")
plt.ylabel("Delinquency Rate (%)")
plt.xlabel("Age Group")
plt.tight_layout()
plt.savefig("outputs/02_delinquency_by_age.png", dpi=160)
plt.close()

emp = delinquency_by("Employment_Status")
plt.figure(figsize=(9,5))
sns.barplot(data=emp, y="Employment_Status", x="rate")
plt.title("Delinquency Rate by Employment Status")
plt.xlabel("Delinquency Rate (%)")
plt.ylabel("")
plt.tight_layout()
plt.savefig("outputs/03_delinquency_by_employment.png", dpi=160)
plt.close()

card = delinquency_by("Credit_Card_Type")
plt.figure(figsize=(9,5))
sns.barplot(data=card, y="Credit_Card_Type", x="rate")
plt.title("Delinquency Rate by Credit Card Type")
plt.xlabel("Delinquency Rate (%)")
plt.ylabel("")
plt.tight_layout()
plt.savefig("outputs/04_delinquency_by_card_type.png", dpi=160)
plt.close()

plt.figure(figsize=(9,6))
sns.scatterplot(
    data=eda, x="Income", y="Loan_Balance",
    hue="Delinquent_Account", alpha=0.7
)
plt.title("Income vs Loan Balance by Delinquency")
plt.tight_layout()
plt.savefig("outputs/05_income_vs_loan_balance.png", dpi=160)
plt.close()

util = eda.assign(Utilization_Band=pd.cut(
    eda["Credit_Utilization_Clean"],
    bins=[-0.01,0.25,0.50,0.75,1.0],
    labels=["0-25%","25-50%","50-75%","75-100%"]
))
util_out = delinquency_by("Utilization_Band")
print("\nUtilization bands:\n", util_out)

month_cols = [f"Month_{i}" for i in range(1,7)]
status_share = pd.DataFrame({
    m: eda[m].value_counts(normalize=True)*100 for m in month_cols
}).fillna(0)
print("\nMonthly payment status share (%):\n", status_share)

print("\nEDA complete.")
