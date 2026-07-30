# Amazon Products Data Preprocessing 🧹📊

مشروع تنظيف وتحليل استكشافي (EDA) لبيانات منتجات أمازون، يغطي دورة كاملة من الـ Data Preprocessing: من اكتشاف الـ Outliers والقيم المفقودة، لمعالجتها، وصولًا لرسم مجموعة Visualizations توضح توزيع البيانات والعلاقات بين الأعمدة.

## 📁 نظرة عامة على البيانات

- الملف المصدر: `amazon.csv` — **1465 صف × 16 عمود**
- جميع الأعمدة كانت مخزّنة كنصوص (`object`)، بما فيها الأعمدة الرقمية، وتحتاج تنظيف قبل أي تحليل:

| العمود | المشكلة | المعالجة |
|---|---|---|
| `discounted_price` | يحتوي على `₹` و `,` مثل `₹399` | إزالة الرموز وتحويل إلى `float` |
| `actual_price` | نفس المشكلة `₹1,099` | إزالة الرموز وتحويل إلى `float` |
| `discount_percentage` | يحتوي على `%` مثل `64%` | إزالة `%` وتحويل إلى `float` |
| `rating` | نص لكنه قيم رقمية | `pd.to_numeric(errors='coerce')` |
| `rating_count` | يحتوي على `,` + 2 قيمة مفقودة | إزالة `,` وتحويل إلى `float` |

## 🗂️ محتويات المشروع

### 📜 السكربتات (Scripts)

| الملف | الوظيفة |
|---|---|
| `showoutlier.py` | اكتشاف الـ Outliers فقط (Q1, Q3, IQR, حدود دنيا/عليا) بدون تعديل البيانات، مع رسم Boxplots |
| `handleoutlier.py` | معالجة الـ Outliers فعليًا عبر استبدالها بالـ Median (قابل للتبديل إلى استراتيجية Drop) |
| `handletomissvalue.py` | اكتشاف ومعالجة القيم المفقودة: Median للأعمدة الرقمية، Mode للأعمدة النصية |
| `drawchart.py` | رسم مجموعة Visualizations متنوعة |

## ⚙️ طريقة التشغيل

```bash
pip install pandas numpy matplotlib arabic-reshaper python-bidi
```

```bash
python showoutlier.py
python handleoutlier.py
python handletomissvalue.py
python drawchart.py
```

راجع `preprocessing_plan.md` للتفاصيل الكاملة.
