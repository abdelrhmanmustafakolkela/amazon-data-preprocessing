# خطة Preprocessing لملف amazon.csv

## نظرة عامة على الداتا (بعد الفحص الفعلي)
- الملف: `amazon.csv` — **1465 صف × 16 عمود**
- كل الأعمدة حاليًا من نوع `object` (نص) حتى الأعمدة الرقمية، لازم تتنضف الأول:

| العمود | المشكلة | الحل قبل أي تحليل |
|---|---|---|
| `discounted_price` | فيها `₹` و`,` مثل `₹399` | نشيل `₹` و`,` ونحولها `float` |
| `actual_price` | نفس المشكلة `₹1,099` | نشيل `₹` و`,` ونحولها `float` |
| `discount_percentage` | فيها `%` مثل `64%` | نشيل `%` ونحولها `float` |
| `rating` | نص لكن قيم رقمية زي `4.2`، ممكن فيها قيم غير رقمية غلط | `pd.to_numeric(errors='coerce')` |
| `rating_count` | فيها `,` مثل `24,269` + فيها **2 قيمة null** | نشيل `,` ونحولها `float` |

هذا التنظيف خطوة **مشتركة** لازم تتعمل في أول كل ملف من الملفات الأربعة قبل أي حساب.

### تصنيف الأعمدة
- **رقمية**: `discounted_price`, `actual_price`, `discount_percentage`, `rating`, `rating_count`
- **نصية**: `product_id`, `product_name`, `category`, `about_product`, `user_id`, `user_name`, `review_id`, `review_title`, `review_content`, `img_link`, `product_link`

### الـ Null الموجودة فعليًا
- `rating_count` بها **2 قيمة null فقط**. باقي الأعمدة 0 null.

---

## الملف 1: `showoutlier.py`
اكتشاف الـ outliers بس، من غير تعديل الداتا: تحميل وتنظيف → حساب Q1/Q3/median/IQR/LB/UB لكل عمود رقمي → طباعة جدول بالنتائج → رسم Boxplots 2×3 وحفظها `showoutlier.png` دون تعديل الداتا الأصلية.

## الملف 2: `handleoutlier.py`
معالجة فعلية: لكل عمود رقمي نستبدل أي قيمة خارج الـ LB/UB بالـ median (بدل الحذف، للحفاظ على حجم العينة البالغ 1465 صف). قابل للتحويل إلى استراتيجية حذف عبر flag `METHOD`. يحفظ النتيجة في `amazon_outliers_handled.csv` مع تقرير قبل/بعد.

## الملف 3: `handletomissvalue.py`
اكتشاف ومعالجة الـ null: الأعمدة الرقمية تُستبدل بالـ median، والنصية بالـ mode، مع منطق ذكي لفض التعادل بالاعتماد على متوسط `rating_count`. يحفظ النتيجة في `amazon_missing_handled.csv`.

## الملف 4: `drawchart.py`
رسم Pie / Scatter / Histogram / Bar ولوحة subplots موحدة (2×3) تجمع عدة رسومات في صورة واحدة.

---

## ترتيب التنفيذ المقترح
1. `showoutlier.py`
2. `handleoutlier.py` → `amazon_outliers_handled.csv`
3. `handletomissvalue.py` → `amazon_missing_handled.csv`
4. `drawchart.py`

## ملاحظات تقنية
- استخدم `pandas`, `numpy`, `matplotlib`.
- كل ملف مستقل بذاته ويقرأ `amazon.csv` من جديد.
- استخدم `errors='coerce'` مع `pd.to_numeric`.
