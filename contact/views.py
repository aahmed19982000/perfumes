from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .forms import ContactForm
from django.utils.translation import gettext as _

def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact_msg = form.save()
            
            # إرسال إيميل للتنبيه
            subject = f"رسالة جديدة من الموقع: {contact_msg.subject}"
            message = f"الاسم: {contact_msg.name}\n" \
                      f"الإيميل: {contact_msg.email}\n" \
                      f"الموضوع: {contact_msg.subject}\n\n" \
                      f"الرسالة:\n{contact_msg.message}"
            
            try:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [settings.DEFAULT_FROM_EMAIL], # إرسال لنفس الإيميل كنوع من التنبيه
                    fail_silently=False,
                )
                messages.success(request, _("تم إرسال رسالتك بنجاح. سنرد عليك في أقرب وقت."))
                return redirect('contact')
            except Exception as e:
                # لو فشل الإرسال (مثلاً مشكلة في الإعدادات) نكتفي بحفظ الرسالة في الداتابيز
                messages.warning(request, _("تم حفظ رسالتك، ولكن واجهنا مشكلة في إرسال التنبيه بالإيميل."))
                return redirect('contact')
    else:
        form = ContactForm()
    
    return render(request, 'contact/contact.html', {'form': form})
