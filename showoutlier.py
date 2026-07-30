"""
showoutlier.py
==============
الهدف: اكتشاف الـ outliers في amazon.csv بدون تعديل الداتا.
المخرجات: طباعة إحصائيات Q1/Q3/IQR/LB/UB/outliers_count لكل عمود رقمي
           + حفظ صورة boxplot اسمها showoutlier.png
"""

import matplotlib
matplotlib.use("Agg")   # non-interactive backend – no GUI window needed
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import warnings
warnings.filterwarnings("ignore")
import arabic_reshaper
from bidi.algorithm import get_display

def ar(text):
    """إصلاح اتجاه النص العربي لـ matplotlib (reshape + bidi)"""
    return get_display(arabic_reshaper.reshape(str(text)))

df = pd.read_csv("amazon.csv")
print(f"✅ تم تحميل الداتا: {df.shape[0]} صف × {df.shape[1]} عمود\n")

def clean_numeric_columns(dataframe):
    df_clean = dataframe.copy()

    for col in ["discounted_price", "actual_price"]:
        df_clean[col] = (
            df_clean[col]
            .astype(str)
            .str.replace("₹", "", regex=False)
            .str.replace(",", "", regex=False)
            .str.strip()
        )
        df_clean[col] = pd.to_numeric(df_clean[col], errors="coerce")

    df_clean["discount_percentage"] = (
        df_clean["discount_percentage"]
        .astype(str)
        .str.replace("%", "", regex=False)
        .str.strip()
    )
    df_clean["discount_percentage"] = pd.to_numeric(df_clean["discount_percentage"], errors="coerce")
    df_clean["rating"] = pd.to_numeric(df_clean["rating"], errors="coerce")

    df_clean["rating_count"] = (
        df_clean["rating_count"]
        .astype(str)
        .str.replace(",", "", regex=False)
        .str.strip()
    )
    df_clean["rating_count"] = pd.to_numeric(df_clean["rating_count"], errors="coerce")
    return df_clean

df = clean_numeric_columns(df)
print("✅ تم تنظيف الأعمدة الرقمية (إزالة ₹، %، ,)\n")

numeric_cols = ["discounted_price", "actual_price", "discount_percentage", "rating", "rating_count"]

print("=" * 80)
print(f"{'Column':<22} {'Median':>9} {'Q1':>9} {'Q3':>9} {'IQR':>9} {'LB':>9} {'UB':>9} {'Outliers':>9} {'%':>7}")
print("=" * 80)

stats_list = []
for col in numeric_cols:
    series = df[col].dropna()
    q1     = series.quantile(0.25)
    q3     = series.quantile(0.75)
    median = series.median()
    iqr    = q3 - q1
    lb     = q1 - 1.5 * iqr
    ub     = q3 + 1.5 * iqr
    outliers       = series[(series < lb) | (series > ub)]
    outliers_count = len(outliers)
    outliers_pct   = (outliers_count / len(series)) * 100

    stats_list.append({
        "column": col, "median": median, "Q1": q1, "Q3": q3,
        "IQR": iqr, "LB": lb, "UB": ub,
        "outliers_count": outliers_count, "outliers_percentage": outliers_pct,
    })

    print(
        f"{col:<22} {median:>9.2f} {q1:>9.2f} {q3:>9.2f} {iqr:>9.2f} "
        f"{lb:>9.2f} {ub:>9.2f} {outliers_count:>9d} {outliers_pct:>6.2f}%"
    )

print("=" * 80)
print()

fig, axes = plt.subplots(2, 3, figsize=(16, 9))
fig.suptitle("Boxplots – Amazon Products Dataset (Outlier Detection)",
             fontsize=15, fontweight="bold", y=1.01)

colors = ["#4C72B0", "#DD8452", "#55A868", "#C44E52", "#8172B2"]

for idx, col in enumerate(numeric_cols):
    ax   = axes[idx // 3][idx % 3]
    data = df[col].dropna()

    ax.boxplot(
        data, vert=True, patch_artist=True,
        boxprops=dict(facecolor=colors[idx], alpha=0.7),
        medianprops=dict(color="black", linewidth=2),
        whiskerprops=dict(linewidth=1.5),
        capprops=dict(linewidth=1.5),
        flierprops=dict(marker="o", markersize=4, markerfacecolor="red", alpha=0.5),
    )
    ax.set_title(col, fontsize=11, fontweight="bold")
    ax.set_ylabel("Value", fontsize=9)
    ax.grid(axis="y", linestyle="--", alpha=0.5)

    stats = stats_list[idx]
    ax.annotate(
        f"Outliers: {stats['outliers_count']} ({stats['outliers_percentage']:.1f}%)",
        xy=(0.5, 0.97), xycoords="axes fraction",
        ha="center", va="top", fontsize=8.5, color="red",
        bbox=dict(boxstyle="round,pad=0.2", facecolor="white", alpha=0.7),
    )

axes[1][2].set_visible(False)

plt.tight_layout()
plt.savefig("showoutlier.png", dpi=150, bbox_inches="tight")
plt.close()
print("✅ تم حفظ الصورة: showoutlier.png")
print("\n⚠️  ملاحظة: الداتا الأصلية لم تُعدَّل — هذا الملف للاكتشاف فقط.")
