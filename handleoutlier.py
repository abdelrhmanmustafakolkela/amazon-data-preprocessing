"""
handleoutlier.py
================
الهدف: معالجة الـ outliers باستبدالها بـ median.
المخرجات: تقرير قبل/بعد + ملف amazon_outliers_handled.csv
"""

import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings("ignore")

METHOD = "replace"   # ← غيّر إلى "drop" لو حبيت حذف الـ outliers بدل استبدالها

df = pd.read_csv("amazon.csv")
print(f"✅ تم تحميل الداتا: {df.shape[0]} صف × {df.shape[1]} عمود\n")

def clean_numeric_columns(dataframe):
    df_clean = dataframe.copy()
    for col in ["discounted_price", "actual_price"]:
        df_clean[col] = (
            df_clean[col].astype(str)
            .str.replace("₹", "", regex=False)
            .str.replace(",", "", regex=False)
            .str.strip()
        )
        df_clean[col] = pd.to_numeric(df_clean[col], errors="coerce")

    df_clean["discount_percentage"] = (
        df_clean["discount_percentage"].astype(str)
        .str.replace("%", "", regex=False)
        .str.strip()
    )
    df_clean["discount_percentage"] = pd.to_numeric(df_clean["discount_percentage"], errors="coerce")
    df_clean["rating"] = pd.to_numeric(df_clean["rating"], errors="coerce")

    df_clean["rating_count"] = (
        df_clean["rating_count"].astype(str)
        .str.replace(",", "", regex=False)
        .str.strip()
    )
    df_clean["rating_count"] = pd.to_numeric(df_clean["rating_count"], errors="coerce")
    return df_clean

df = clean_numeric_columns(df)
print("✅ تم تنظيف الأعمدة الرقمية\n")

numeric_cols = ["discounted_price", "actual_price", "discount_percentage", "rating", "rating_count"]

bounds = {}
for col in numeric_cols:
    series = df[col].dropna()
    q1     = series.quantile(0.25)
    q3     = series.quantile(0.75)
    iqr    = q3 - q1
    median = series.median()
    bounds[col] = {
        "Q1": q1, "Q3": q3, "IQR": iqr,
        "LB": q1 - 1.5 * iqr,
        "UB": q3 + 1.5 * iqr,
        "median": median,
    }

print("=" * 65)
print("📊 تقرير الـ Outliers قبل المعالجة")
print("=" * 65)
print(f"{'Column':<25} {'LB':>8} {'UB':>8} {'Median':>8} {'Outliers':>9} {'%':>7}")
print("-" * 65)

before_counts = {}
for col in numeric_cols:
    b      = bounds[col]
    series = df[col].dropna()
    mask   = (series < b["LB"]) | (series > b["UB"])
    count  = mask.sum()
    pct    = (count / len(series)) * 100
    before_counts[col] = count
    print(f"{col:<25} {b['LB']:>8.2f} {b['UB']:>8.2f} {b['median']:>8.2f} {count:>9d} {pct:>6.2f}%")
print("=" * 65)
print()

df_handled = df.copy()

if METHOD == "replace":
    print(f"🔧 الاستراتيجية: استبدال الـ outliers بـ Median (METHOD='{METHOD}')\n")
    for col in numeric_cols:
        b    = bounds[col]
        mask = (df_handled[col] < b["LB"]) | (df_handled[col] > b["UB"])
        df_handled.loc[mask, col] = b["median"]
        print(f"  ✔ {col}: تم استبدال {mask.sum()} قيمة بـ median={b['median']:.2f}")

elif METHOD == "drop":
    print(f"🔧 الاستراتيجية: حذف الصفوف التي تحتوي على outliers (METHOD='{METHOD}')\n")
    rows_before = len(df_handled)
    for col in numeric_cols:
        b            = bounds[col]
        mask_outlier = (df_handled[col] < b["LB"]) | (df_handled[col] > b["UB"])
        df_handled   = df_handled[~mask_outlier]
    rows_after = len(df_handled)
    print(f"  ✔ تم حذف {rows_before - rows_after} صف. الصفوف المتبقية: {rows_after}")

else:
    raise ValueError(f"METHOD غير صالح: '{METHOD}'. اختر replace أو drop.")

print()

print("=" * 65)
print("📊 تقرير الـ Outliers بعد المعالجة")
print("=" * 65)
print(f"{'Column':<25} {'Outliers after':>14} {'%':>7}")
print("-" * 65)

for col in numeric_cols:
    b           = bounds[col]
    series_after = df_handled[col].dropna()
    mask_after   = (series_after < b["LB"]) | (series_after > b["UB"])
    count_after  = mask_after.sum()
    pct_after    = (count_after / len(series_after)) * 100 if len(series_after) > 0 else 0
    print(f"{col:<25} {count_after:>14d} {pct_after:>6.2f}%")

print("=" * 65)
print()

output_file = "amazon_outliers_handled.csv"
df_handled.to_csv(output_file, index=False)
print(f"✅ تم حفظ الداتا المعالجة في: {output_file}")
print(f"   الحجم النهائي: {df_handled.shape[0]} صف × {df_handled.shape[1]} عمود")
