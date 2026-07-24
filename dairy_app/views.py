from decimal import Decimal
from datetime import date
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils import timezone
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from django.db.models import Sum, Count
from .models import Farmer, MilkCollection
import requests
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Farmer, MilkCollection


@login_required(login_url='/admin/login/')
def pay_farmer(request, farmer_id):
    try:
        farmer = Farmer.objects.get(pk=farmer_id)
    except Farmer.DoesNotExist:
        return HttpResponse("Farmer not found", status=404)
    
    unpaid_collections = MilkCollection.objects.filter(farmer=farmer, is_paid=False)
    
    if unpaid_collections.exists():
        today_date = timezone.now().date()
        unpaid_collections.update(is_paid=True, paid_date=today_date)
        
    return redirect('farmer_ledger')


@login_required(login_url='/admin/login/')
def farmer_ledger(request):
    farmers = Farmer.objects.all()
    ledger_data = []
    
    for farmer in farmers:
        collections = MilkCollection.objects.filter(farmer=farmer)
        total_litres = sum(c.litres for c in collections)
        unpaid_amount = sum(c.total_amount for c in collections if not c.is_paid and c.total_amount)
        last_paid = collections.filter(is_paid=True).order_by('-paid_date').first()
        last_paid_date = last_paid.paid_date if last_paid else None
        
        ledger_data.append({
            'id': farmer.id,
            'name': farmer.name,
            'phone': farmer.phone,
            'total_litres': total_litres,
            'unpaid_amount': unpaid_amount,
            'last_paid_date': last_paid_date,
        })
        
    context = {
        'farmers': ledger_data,
    }
    return render(request, 'dairy_app/ledger.html', context)


@login_required(login_url='/admin/login/')
def download_payment_slip(request, farmer_id):
    try:
        farmer = Farmer.objects.get(pk=farmer_id)
    except Farmer.DoesNotExist:
        return HttpResponse("Farmer not found", status=404)

    paid_collections = MilkCollection.objects.filter(farmer=farmer, is_paid=True).order_by('-date')
    
    if not paid_collections.exists():
        return HttpResponse("No paid payment history found for this farmer.", status=404)

    total_paid_amount = sum(c.total_amount for c in paid_collections if c.total_amount)
    total_litres = sum(c.litres for c in paid_collections)
    last_payment_date = paid_collections.first().paid_date

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Payment_Receipt_{farmer.name}.pdf"'

    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    p.setFont("Helvetica-Bold", 20)
    p.drawString(180, height - 50, "DAIRY PAYMENT RECEIPT")
    
    p.setFont("Helvetica", 12)
    p.drawString(50, height - 90, f"Payment Date: {last_payment_date}")
    p.drawString(50, height - 110, f"Status: PAID (10-Day Settlement)")
    
    p.line(50, height - 125, width - 50, height - 125)

    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, height - 160, "Farmer Details:")
    p.setFont("Helvetica", 12)
    p.drawString(50, height - 180, f"Name: {farmer.name}")
    p.drawString(50, height - 200, f"Phone: {farmer.phone}")

    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, height - 240, "Settlement Summary:")
    p.setFont("Helvetica", 12)
    p.drawString(50, height - 260, f"Total Milk Collected: {total_litres} L")
    p.drawString(50, height - 280, f"Total Entries Count: {paid_collections.count()}")
    
    p.line(50, height - 295, width - 50, height - 295)

    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, height - 335, f"Total Amount Paid: Rs. {total_paid_amount}")

    p.setFont("Helvetica-Oblique", 10)
    p.drawString(50, height - 400, "Thank you! All dues cleared for this cycle.")

    p.showPage()
    p.save()
    return response


@login_required(login_url='/admin/login/')
def download_slip(request, pk):
    try:
        collection = MilkCollection.objects.get(pk=pk)
    except MilkCollection.DoesNotExist:
        return HttpResponse("Entry not found", status=404)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Milk_Slip_{collection.id}.pdf"'

    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    p.setFont("Helvetica-Bold", 20)
    p.drawString(200, height - 50, "DAIRY MANAGEMENT SYSTEM")
    
    p.setFont("Helvetica", 12)
    p.drawString(50, height - 90, f"Receipt ID: #{collection.id}")
    p.drawString(50, height - 110, f"Date: {collection.date}")
    p.drawString(50, height - 130, f"Shift: {collection.shift}")
    
    p.line(50, height - 145, width - 50, height - 145)

    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, height - 180, "Farmer Details:")
    p.setFont("Helvetica", 12)
    p.drawString(50, height - 200, f"Name: {collection.farmer.name}")
    p.drawString(50, height - 220, f"Phone: {collection.farmer.phone}")

    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, height - 260, "Collection Details:")
    p.setFont("Helvetica", 12)
    p.drawString(50, height - 280, f"Total Litres: {collection.litres} L")
    p.drawString(50, height - 300, f"FAT Content: {collection.fat}")
    p.drawString(50, height - 320, f"Rate Per Litre: Rs. {collection.price_per_litre}")
    
    p.line(50, height - 335, width - 50, height - 335)

    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, height - 370, f"Total Payout Amount: Rs. {collection.total_amount}")

    p.setFont("Helvetica-Oblique", 10)
    p.drawString(50, height - 430, "Thank you for doing business with us!")

    p.showPage()
    p.save()
    return response


@login_required(login_url='/admin/login/')
def dashboard(request):
    farmers = Farmer.objects.all()
    collections = MilkCollection.objects.all().order_by('-date', '-id')
    
    search_query = request.GET.get('q', '')
    selected_date = request.GET.get('date', '')
    
    if search_query:
        collections = collections.filter(farmer__name__icontains=search_query)
        
    if selected_date:
        collections = collections.filter(date=selected_date)

    total_litres = sum(c.litres for c in collections)
    total_amount = sum(c.total_amount for c in collections if c.total_amount)
    
    context = {
        'farmers': farmers,
        'collections': collections,
        'total_litres': total_litres,
        'total_amount': total_amount,
        'search_query': search_query,
        'selected_date': selected_date,
    }
    return render(request, 'dairy_app/dashboard.html', context)


@login_required(login_url='/admin/login/')
def add_milk(request):
    farmers = Farmer.objects.all()
    
    if request.method == 'POST':
        farmer_id = request.POST.get('farmer')
        litres = request.POST.get('litres')
        fat = request.POST.get('fat')
        price_per_litre = request.POST.get('price_per_litre')
        shift = request.POST.get('shift')
        
        farmer = Farmer.objects.get(id=farmer_id)
        
        # 1. Database mein entry save karna
        collection = MilkCollection.objects.create(
            farmer=farmer,
            litres=litres,
            fat=fat,
            price_per_litre=price_per_litre,
            shift=shift,
            collected_by=request.user
        )
        
        # 2. 🚀 Automatic WhatsApp Message Sending Logic (UltraMsg API)
        try:
            # Apni UltraMsg details yahan daalni hain
            instance_id = "instance185905"  # Tera UltraMsg Instance ID
            token = "vin3048cxiba6j5o"        # Tera UltraMsg Token
            
            url = f"https://api.ultramsg.com/{instance_id}/messages/chat"
            
            # Message format
            message_text = (
                f"🥛 *DAIRY COLLECTION RECEIPT*\n\n"
                f"Hello *{farmer.name}*,\n"
                f"Aapki aaj ki doodh entry darj ho gayi hai:\n\n"
                f"📅 Date: {collection.date} ({collection.shift})\n"
                f"⚖️ Litres: {collection.litres} L\n"
                f"🧪 FAT: {collection.fat}\n"
                f"💰 Rate: ₹{collection.price_per_litre} /L\n"
                f"💵 Total Amount: *₹{collection.total_amount}*\n\n"
                f"Thank you for doing business with us! 🙏"
            )
            
            # Phone number formatting (+91 lagana zaroori hai India ke liye)
            phone_number = f"91{farmer.phone}"
            
            payload = {
                'token': token,
                'to': phone_number,
                'body': message_text
            }
            
            headers = {'content-type': 'application/x-www-form-urlencoded'}
            
            # API Request bhejna
            response = requests.post(url, data=payload, headers=headers)
            print("WhatsApp API Response:", response.text)
            
        except Exception as e:
            print(f"WhatsApp Error: {e}")
            
        return redirect('dashboard')
        
    return render(request, 'dairy_app/add_milk.html', {'farmers': farmers})