"""
handletomissvalue.py
====================
الهدف: اكتشاف ومعالجة القيم الـ null في كل أعمدة amazon.csv.
المخرجات: تقرير null قبل/بعد لكل عمود + ملف amazon_missing_handled.csv
"""

import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings("ignore")

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
string_cols  = [c for c in df.columns if c not in numeric_cols]

print("=" * 60)
print("📊 تقرير الـ Null قبل المعالجة (لكل الأعمدة الـ 16)")
print("=" * 60)
print(f"{'Column':<30} {'Type':<12} {'Nulls':>6}")
print("-" * 60)

for col in df.columns:
    dtype      = "numeric" if col in numeric_cols else "string"
    null_count = df[col].isnull().sum()
    marker     = " ⚠️" if null_count > 0 else ""
    print(f"{col:<30} {dtype:<12} {null_count:>6}{marker}")

print("=" * 60)
print()

df_handled = df.copy()

print("🔧 بدء معالجة القيم المفقودة...\n")

for col in df.columns:
    null_count = df_handled[col].isnull().sum()
    if null_count == 0:
        continue

    print(f"  ── العمود: [{col}]  (null={null_count})")

    if col in numeric_cols:
        median_val = df_handled[col].median()
        df_handled[col] = df_handled[col].fillna(median_val)
        print(f"     النوع: رقمي → استبدلنا الـ null بـ median = {median_val:.4f}")

    else:
        vc         = df_handled[col].value_counts()
        max_count  = vc.iloc[0]
        top_values = vc[vc == max_count]

        if len(top_values) == 1:
            mode_val  = top_values.index[0]
            mode_cnt  = int(top_values.iloc[0])
            if len(vc) >= 2:
                second_val = vc.index[1]
                second_cnt = int(vc.iloc[1])
                print(f"     النوع: نصي")
                print(f"     أكتر قيمة تكرارًا (mode): '{mode_val}' — تكررت {mode_cnt} مرة")
                print(f"     ثاني أكتر قيمة تكرارًا:  '{second_val}' — تكررت {second_cnt} مرة")
            else:
                print(f"     النوع: نصي")
                print(f"     mode: '{mode_val}' — تكررت {mode_cnt} مرة")
            df_handled[col] = df_handled[col].fillna(mode_val)
            print(f"     ✔ تم استبدال الـ null بـ: '{mode_val}'")

        else:
            print(f"     النوع: نصي")
            print(f"     ⚠️  تعادل بين {len(top_values)} قيمة بنفس عدد التكرار ({max_count}):")
            for val in top_values.index:
                print(f"       - '{val}'")

            tiebreak_col = "rating_count" if "rating_count" in df_handled.columns else None
            if tiebreak_col:
                scores = {}
                for val in top_values.index:
                    rows_with_val  = df_handled[df_handled[col] == val]
                    avg_rc         = rows_with_val[tiebreak_col].mean()
                    scores[val]    = avg_rc if not np.isnan(avg_rc) else 0
                    print(f"       '{val}': متوسط {tiebreak_col} = {avg_rc:.2f}")

                mode_val = max(scores, key=scores.get)
                print(f"     🏆 اخترنا '{mode_val}' لأن صفوفها لها أعلى متوسط {tiebreak_col}")
            else:
                mode_val = top_values.index[0]
                print(f"     Fallback: اخترنا أول قيمة '{mode_val}'")

            df_handled[col] = df_handled[col].fillna(mode_val)
            print(f"     ✔ تم استبدال الـ null بـ: '{mode_val}'")

    print()

print("=" * 60)
print("📊 تقرير الـ Null بعد المعالجة")
print("=" * 60)
total_null_after = df_handled.isnull().sum().sum()
print(f"{'Column':<30} {'Nulls after':>11}")
print("-" * 60)
for col in df_handled.columns:
    null_after = df_handled[col].isnull().sum()
    print(f"{col:<30} {null_after:>11}")
print("=" * 60)

if total_null_after == 0:
    print("\n✅ تأكيد: مفيش أي null متبقي في الداتا. 🎉")
else:
    print(f"\n⚠️  لا يزال هناك {total_null_after} قيمة null! راجع الكود.")

output_file = "amazon_missing_handled.csv"
df_handled.to_csv(output_file, index=False)
print(f"\n✅ تم حفظ الداتا المعالجة في: {output_file}")
print(f"   الحجم النهائي: {df_handled.shape[0]} صف × {df_handled.shape[1]} عمود")
