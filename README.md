# AI Image Editor

محرر صور ذكي محلي وخفيف يعمل من المتصفح على Windows، بواجهة عربية/إنجليزية، ويهدف إلى تنفيذ تعديلات الصور محليًا دون مفاتيح API مدفوعة.

## V5
- محرر صور محلي.
- أوامر نصية بالعربية/الإنجليزية.
- دعم القناع للتعديلات الموضعية.
- طبقة اتصال محلية مع ComfyUI.
- فحص RAM وGPU قبل اختيار نموذج AI.
- لا يتم تضمين ملفات النماذج الكبيرة داخل GitHub.

ComfyUI يوفر واجهة API محلية ويمكن تشغيله على Windows وأنواع متعددة من العتاد، لذلك سنختار Workflow ونموذجًا وفق مواصفات الجهاز الفعلية.

## حالة الجهاز المؤكدة

الجهاز الحالي يستخدم **Intel(R) UHD Graphics** مع **128 MB Dedicated VRAM** وحوالي **8 GB Shared Memory** وذاكرة نظام **16 GB RAM**.

لذلك لن نتعامل مع الجهاز على أنه يملك 8 GB VRAM، ولن نثبت نموذج توليد صور ضخم قبل اختبار التوافق. تم توثيق القرار في `docs/HARDWARE-PROFILE.md`.

## الخطة التالية

1. إبقاء محرر الصور المحلي سريعًا للتعديلات العادية.
2. اختبار مسار AI خفيف جدًا فقط إذا كان عمليًا على الجهاز.
3. عدم تحميل نماذج ضخمة على هذا الجهاز دون حاجة.
4. إبقاء ComfyUI كطبقة محلية اختيارية.
5. إضافة Backend أقوى/بعيد فقط كخيار اختياري إذا أثبت الاختبار أن التوليد المحلي غير عملي.

## الاختبار الأساسي للمشروع

> أضف شريكًا يجلس بجانبها بكل حب وود، مع الحفاظ على ملامحها وإضاءة الصورة وتناسق المشهد.

الهدف هو أن يستطيع التطبيق إرسال الصورة + الطلب إلى Backend متوافق ثم عرض النتيجة، سواء كان التنفيذ محليًا أو عبر Backend اختياري أقوى.

> ملاحظة السلامة: المشروع لا يهدف إلى تجاوز أنظمة أمان النماذج أو مزودي الخدمة. الهدف هو جعل تحرير الصور العادي مرنًا وسهلًا قدر الإمكان.


## V6 status

V6 now contains a real local ComfyUI API bridge for masked image editing. The browser sends the image, mask and natural-language prompt to `server.py`, which uploads them to ComfyUI, queues the workflow, waits for completion, and returns the generated image.

The first target workflow is Stable Diffusion v1.5 Inpainting because the current PC has Intel UHD integrated graphics, 16 GB RAM, and only 128 MB dedicated VRAM. Large modern image-editing models are intentionally not the first target.

See `docs/MODEL-STRATEGY-V6.md`.
