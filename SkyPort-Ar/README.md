
مشروع: مطار السماء — نسخة متقدمة (Arabic-first)
============================================

محتويات:
- صفحات HTML: index, flights, services, contact, login (الواجهة بالعربية RTL)
- css/styles.css : تصميم منظم مع متغيرات لتعديل الألوان
- js/main.js : تفاعلات عامة (بحث سريع، نماذج، toasts)
- js/flights.js : تحميل بيانات الرحلات، فلترة، فرز، ترقيم صفحات، مودال
- data/flights.json : بيانات رحلات (قابلة للتعديل)
- images/logo.svg وملفات صور placeholder عبر روابط Unsplash في HTML

تشغيل:
1. فك الضغط وافتح index.html في المتصفح أو استخدم Live Server.
2. لتعديل الرحلات، افتح data/flights.json وعدل/أضف عناصر جديدة.

ملاحظات للترقية:
- لربط بيانات حقيقية: استخدم API مثل Aviationstack أو OpenSky واستبدل تحميل JSON بالـ fetch من الـ API.
- لإضافة ثنائي اللغة: يمكن إضافة ملفات ترجمة أو استخدام مكتبة i18n.
