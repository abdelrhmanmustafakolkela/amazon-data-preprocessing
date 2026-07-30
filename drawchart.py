"""
drawchart.py
============
الهدف: رسم مجموعة charts متنوعة على الداتا بعد التنظيف.
المخرجات:
  - pie_chart.png
  - scatter_chart.png
  - hist_chart.png
  - bar_chart.png
  - combined_subplots.png
"""

import matplotlib
matplotlib.use("Agg")   # non-interactive backend
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import warnings
warnings.filterwarnings("ignore")
import os
import arabic_reshaper
from bidi.algorithm import get_display

def ar(text):
    """إصلاح اتجاه النص العربي لـ matplotlib (reshape + bidi)"""
    return get_display(arabic_reshaper.reshape(str(text)))

if os.path.exists("amazon_missing_handled.csv"):
    df = pd.read_csv("amazon_missing_handled.csv")
    print("✅ تم تحميل: amazon_missing_handled.csv")
elif os.path.exists("amazon_outliers_handled.csv"):
    df = pd.read_csv("amazon_outliers_handled.csv")
    print("✅ تم تحميل: amazon_outliers_handled.csv")
else:
    df = pd.read_csv("amazon.csv")
    print("✅ تم تحميل: amazon.csv (الأصلي)")

print(f"   الحجم: {df.shape[0]} صف × {df.shape[1]} عمود\n")

def clean_numeric_columns(dataframe):
    df_clean = dataframe.copy()
    for col in ["discounted_price", "actual_price"]:
        if df_clean[col].dtype == object:
            df_clean[col] = (
                df_clean[col].astype(str)
                .str.replace("₹", "", regex=False)
                .str.replace(",", "", regex=False)
                .str.strip()
            )
            df_clean[col] = pd.to_numeric(df_clean[col], errors="coerce")

    if df_clean["discount_percentage"].dtype == object:
        df_clean["discount_percentage"] = (
            df_clean["discount_percentage"].astype(str)
            .str.replace("%", "", regex=False)
            .str.strip()
        )
        df_clean["discount_percentage"] = pd.to_numeric(df_clean["discount_percentage"], errors="coerce")

    df_clean["rating"] = pd.to_numeric(df_clean["rating"], errors="coerce")

    if df_clean["rating_count"].dtype == object:
        df_clean["rating_count"] = (
            df_clean["rating_count"].astype(str)
            .str.replace(",", "", regex=False)
            .str.strip()
        )
        df_clean["rating_count"] = pd.to_numeric(df_clean["rating_count"], errors="coerce")

    return df_clean

df = clean_numeric_columns(df)

df["main_category"] = df["category"].astype(str).str.split("|").str[0].str.strip()

PALETTE = [
    "#4C72B0", "#DD8452", "#55A868", "#C44E52", "#8172B2",
    "#937860", "#DA8BC3", "#8C8C8C", "#CCB974", "#64B5CD"
]
plt.rcParams["font.family"] = "DejaVu Sans"
plt.rcParams["axes.spines.top"]   = False
plt.rcParams["axes.spines.right"] = False

cat_counts = df["main_category"].value_counts()
top8       = cat_counts.head(8)
other_sum  = cat_counts.iloc[8:].sum()
labels_pie = list(top8.index) + (["Other"] if other_sum > 0 else [])
sizes_pie  = list(top8.values) + ([other_sum] if other_sum > 0 else [])
colors_pie = PALETTE[:len(labels_pie)]

fig1, ax1 = plt.subplots(figsize=(9, 7))
wedges, texts, autotexts = ax1.pie(
    sizes_pie,
    labels=None,
    autopct="%1.1f%%",
    colors=colors_pie,
    startangle=140,
    pctdistance=0.80,
    wedgeprops=dict(edgecolor="white", linewidth=1.5),
)
for at in autotexts:
    at.set_fontsize(8)
ax1.legend(
    wedges, labels_pie,
    loc="lower center",
    bbox_to_anchor=(0.5, -0.12),
    ncol=3,
    fontsize=9,
    framealpha=0.5,
)
ax1.set_title(ar("توزيع المنتجات حسب الفئة الرئيسية (أعلى 8 فئات)"), fontsize=13, fontweight="bold", pad=15)
plt.tight_layout()
plt.savefig("pie_chart.png", dpi=150, bbox_inches="tight")
plt.close()
print("✅ تم حفظ: pie_chart.png")

fig2, axes2 = plt.subplots(1, 2, figsize=(14, 6))
fig2.suptitle("Scatter Plots – Amazon Dataset", fontsize=13, fontweight="bold")

ax = axes2[0]
df_sc = df[["actual_price", "discounted_price"]].dropna()
ax.scatter(df_sc["actual_price"], df_sc["discounted_price"],
           alpha=0.4, s=18, color=PALETTE[0], edgecolors="none")
max_val = max(df_sc["actual_price"].max(), df_sc["discounted_price"].max())
ax.plot([0, max_val], [0, max_val], "r--", linewidth=1, label=ar("y = x (بدون خصم)"))
ax.set_xlabel("actual_price (₹)", fontsize=10)
ax.set_ylabel("discounted_price (₹)", fontsize=10)
ax.set_title(ar("السعر الأصلي vs السعر بعد الخصم"), fontsize=11)
ax.legend(fontsize=8)
ax.grid(linestyle="--", alpha=0.3)

ax = axes2[1]
df_sc2 = df[["rating", "rating_count"]].dropna()
scatter = ax.scatter(df_sc2["rating"], df_sc2["rating_count"],
                     alpha=0.35, s=18, c=df_sc2["rating"],
                     cmap="RdYlGn", edgecolors="none")
fig2.colorbar(scatter, ax=ax, label="rating")
ax.set_xlabel("rating", fontsize=10)
ax.set_ylabel("rating_count", fontsize=10)
ax.set_title(ar("Rating مقابل عدد التقييمات"), fontsize=11)
ax.grid(linestyle="--", alpha=0.3)

plt.tight_layout()
plt.savefig("scatter_chart.png", dpi=150, bbox_inches="tight")
plt.close()
print("✅ تم حفظ: scatter_chart.png")

fig3, axes3 = plt.subplots(1, 2, figsize=(13, 5))
fig3.suptitle("Histograms – Amazon Dataset", fontsize=13, fontweight="bold")

ax = axes3[0]
data_rating = df["rating"].dropna()
ax.hist(data_rating, bins=20, color=PALETTE[0], edgecolor="white", alpha=0.85)
ax.axvline(data_rating.mean(),   color="red",    linestyle="--", linewidth=1.5, label=f"Mean={data_rating.mean():.2f}")
ax.axvline(data_rating.median(), color="orange", linestyle="-.", linewidth=1.5, label=f"Median={data_rating.median():.2f}")
ax.set_xlabel("Rating", fontsize=10)
ax.set_ylabel("Frequency", fontsize=10)
ax.set_title(ar("توزيع تقييمات المنتجات"), fontsize=11)
ax.legend(fontsize=8)
ax.grid(axis="y", linestyle="--", alpha=0.4)

ax = axes3[1]
data_disc = df["discount_percentage"].dropna()
ax.hist(data_disc, bins=20, color=PALETTE[1], edgecolor="white", alpha=0.85)
ax.axvline(data_disc.mean(),   color="red",    linestyle="--", linewidth=1.5, label=f"Mean={data_disc.mean():.1f}%")
ax.axvline(data_disc.median(), color="orange", linestyle="-.", linewidth=1.5, label=f"Median={data_disc.median():.1f}%")
ax.set_xlabel("Discount %", fontsize=10)
ax.set_ylabel("Frequency", fontsize=10)
ax.set_title(ar("توزيع نسبة الخصم"), fontsize=11)
ax.legend(fontsize=8)
ax.grid(axis="y", linestyle="--", alpha=0.4)

plt.tight_layout()
plt.savefig("hist_chart.png", dpi=150, bbox_inches="tight")
plt.close()
print("✅ تم حفظ: hist_chart.png")

fig4, ax4 = plt.subplots(figsize=(12, 6))

top10_cats = df["main_category"].value_counts().head(10).index.tolist()
df_top10   = df[df["main_category"].isin(top10_cats)]

avg_rating = (
    df_top10.groupby("main_category")["rating"]
    .mean()
    .reindex(top10_cats)
    .sort_values(ascending=True)
)

colors_bar = plt.cm.RdYlGn(np.linspace(0.2, 0.9, len(avg_rating)))
bars = ax4.barh(avg_rating.index, avg_rating.values, color=colors_bar, edgecolor="white", height=0.65)

for bar, val in zip(bars, avg_rating.values):
    ax4.text(val + 0.01, bar.get_y() + bar.get_height() / 2,
             f"{val:.2f}", va="center", ha="left", fontsize=9)

ax4.set_xlabel(ar("متوسط التقييم (Rating)"), fontsize=10)
ax4.set_title(ar("متوسط تقييم المنتجات حسب الفئة الرئيسية (أعلى 10 فئات)"), fontsize=12, fontweight="bold")
ax4.set_xlim(0, avg_rating.max() * 1.15)
ax4.grid(axis="x", linestyle="--", alpha=0.4)
plt.tight_layout()
plt.savefig("bar_chart.png", dpi=150, bbox_inches="tight")
plt.close()
print("✅ تم حفظ: bar_chart.png")

fig5, axes5 = plt.subplots(2, 3, figsize=(18, 10))
fig5.suptitle("Amazon Dataset – Combined Analysis Subplots", fontsize=14, fontweight="bold", y=1.01)

ax = axes5[0][0]
data_r = df["rating"].dropna()
ax.hist(data_r, bins=20, color=PALETTE[0], edgecolor="white", alpha=0.85)
ax.axvline(data_r.mean(), color="red", linestyle="--", linewidth=1.2, label=f"Mean={data_r.mean():.2f}")
ax.set_title(ar("توزيع Rating"), fontsize=10, fontweight="bold")
ax.set_xlabel("Rating"); ax.set_ylabel("Count")
ax.legend(fontsize=7); ax.grid(axis="y", linestyle="--", alpha=0.35)

ax = axes5[0][1]
top8_cats = df["main_category"].value_counts().head(8).index.tolist()
avg_r8 = (
    df[df["main_category"].isin(top8_cats)]
    .groupby("main_category")["rating"]
    .mean()
    .sort_values(ascending=True)
)
c8 = plt.cm.Blues(np.linspace(0.4, 0.9, len(avg_r8)))
ax.barh(avg_r8.index, avg_r8.values, color=c8, edgecolor="white")
ax.set_title(ar("متوسط Rating / فئة"), fontsize=10, fontweight="bold")
ax.set_xlabel("Avg Rating")
ax.grid(axis="x", linestyle="--", alpha=0.35)

ax = axes5[0][2]
df_sc = df[["actual_price", "discounted_price"]].dropna()
ax.scatter(df_sc["actual_price"], df_sc["discounted_price"],
           alpha=0.3, s=12, color=PALETTE[2], edgecolors="none")
mv = max(df_sc["actual_price"].max(), df_sc["discounted_price"].max())
ax.plot([0, mv], [0, mv], "r--", linewidth=1)
ax.set_title("actual_price vs discounted_price", fontsize=10, fontweight="bold")
ax.set_xlabel("actual_price (₹)"); ax.set_ylabel("discounted_price (₹)")
ax.grid(linestyle="--", alpha=0.3)

ax = axes5[1][0]
bp_data = df["discount_percentage"].dropna()
ax.boxplot(bp_data, vert=True, patch_artist=True,
           boxprops=dict(facecolor=PALETTE[3], alpha=0.7),
           medianprops=dict(color="black", linewidth=2),
           flierprops=dict(marker="o", markersize=3, markerfacecolor="red", alpha=0.5))
ax.set_title("Boxplot: Discount %", fontsize=10, fontweight="bold")
ax.set_ylabel("Discount %")
ax.grid(axis="y", linestyle="--", alpha=0.35)

ax = axes5[1][1]
top6 = cat_counts.head(6)
oth  = cat_counts.iloc[6:].sum()
lbs  = list(top6.index) + (["Other"] if oth > 0 else [])
szs  = list(top6.values) + ([oth] if oth > 0 else [])
ax.pie(szs, labels=None, autopct="%1.0f%%", colors=PALETTE[:len(lbs)],
       startangle=90, pctdistance=0.78,
       wedgeprops=dict(edgecolor="white", linewidth=1.2))
ax.legend(lbs, loc="lower center", bbox_to_anchor=(0.5, -0.25),
          ncol=2, fontsize=7, framealpha=0.4)
ax.set_title(ar("توزيع الفئات (Pie)"), fontsize=10, fontweight="bold")

ax = axes5[1][2]
df_sc2 = df[["rating", "rating_count"]].dropna()
sc2 = ax.scatter(df_sc2["rating"], df_sc2["rating_count"],
                 alpha=0.3, s=12, c=df_sc2["rating"],
                 cmap="RdYlGn", edgecolors="none")
fig5.colorbar(sc2, ax=ax, label="rating", shrink=0.8)
ax.set_title("Rating vs Rating Count", fontsize=10, fontweight="bold")
ax.set_xlabel("Rating"); ax.set_ylabel("Rating Count")
ax.grid(linestyle="--", alpha=0.3)

plt.tight_layout()
plt.savefig("combined_subplots.png", dpi=150, bbox_inches="tight")
plt.close()
print("✅ تم حفظ: combined_subplots.png")

print("\n🎉 تم إنشاء كل الـ charts بنجاح!")
print("   pie_chart.png | scatter_chart.png | hist_chart.png | bar_chart.png | combined_subplots.png")
