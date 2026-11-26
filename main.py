# استدعاء الكلاس الرئيسي من ملف app.py
from app import SupermarketApp


# التأكد إن الملف هو نقطة تشغيل البرنامج
if __name__ == "__main__":

    # إنشاء كائن من النظام
    app = SupermarketApp()

    # تشغيل واجهة البرنامج
    app.mainloop()