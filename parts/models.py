from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse

from django.db.models.signals import post_delete
from django.dispatch import receiver
from .validators import validate_file_extension

# Определение выбора букв для баркодов
letter = [
    ('A', 'A'),
    ('B', 'B'),
    ('C', 'C'),
    ('D', 'D'),
    ('E', 'E'),
    ('F', 'F'),
    ('G', 'G'),
    ('H', 'H'),
    ('I', 'I'),
    ('J', 'J'),
    ('K', 'K'),
    ('L', 'L'),
    ('M', 'M'),
    ('N', 'N'),
    ('O', 'O'),
    ('P', 'P'),
    ('Q', 'Q'),
    ('R', 'R'),
    ('S', 'S'),
    ('T', 'T'),
    ('U', 'U'),
    ('V', 'V'),
    ('W', 'W'),
    ('X', 'X'),
    ('Y', 'Y'),
    ('Z', 'Z'),
]

# Определение выбора чисел для баркодов
number = [
    ('01', '01'),
    ('02', '02'),
    ('03', '03'),
    ('04', '04'),
    ('05', '05'),
    ('06', '06'),
    ('07', '07'),
    ('08', '08'),
    ('09', '09'),
    ('10', '10'),
    ('11', '11'),
    ('12', '12'),
    ('13', '13'),
    ('14', '14'),
    ('15', '15'),
    ('16', '16'),
    ('17', '17'),
    ('18', '18'),
    ('19', '19'),
    ('20', '20'),
    ('21', '21'),
    ('22', '22'),
    ('23', '23'),
    ('24', '24'),
    ('25', '25'),
    ('26', '26'),
    ('27', '27'),
    ('28', '28'),
    ('29', '29'),
    ('30', '30'),
    ('31', '31'),
    ('32', '32'),
    ('33', '33'),
    ('34', '34'),
    ('35', '35'),
    ('36', '36'),
    ('37', '37'),
    ('38', '38'),
    ('39', '39'),
    ('40', '40'),
]

class Parts(models.Model):
    part_barcode = models.CharField(max_length=100, null=True, blank=True, verbose_name='Штрих-код')
    part_name = models.CharField(max_length=200, null=True, blank=True, verbose_name='Наименование')
    part_model = models.CharField(max_length=100, null=True, blank=True, verbose_name='Модель')
    part_note = models.TextField(null=True, blank=True, verbose_name='Примечание') 
    part_manufacturer_barcode = models.CharField(max_length=100, null=True, blank=True, verbose_name='Штрих-код производителя')
    part_manufacturer_part_number = models.CharField(max_length=100, null=True, blank=True, verbose_name='Заводской номер производителя')
    part_oem_number = models.CharField(max_length=100, null=True, blank=True, verbose_name='OEM номер')
    part_qty_in_stock = models.PositiveIntegerField(null=True, blank=True, verbose_name='Количество в наличии')
    part_min_qty = models.PositiveIntegerField(null=True, blank=True, verbose_name='Минимальное количество')
    part_compatible = models.CharField(max_length=100, null=True, blank=True, verbose_name='Где используется')
    
    date_posted = models.DateTimeField(default=timezone.now)    
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True,)

    class Meta:
        ordering = ['part_name']
    def __str__(self):
        return str(self.part_name) + str(self.part_manufacturer_barcode)

    def get_absolute_url(self):
        return reverse('parts-detail-page', kwargs={'pk': self.pk})

class CompatibleMachines(models.Model):
    part_id = models.ForeignKey(Parts, on_delete=models.CASCADE, null=True, related_name='machinparts')
    machine_id = models.CharField(max_length=2, choices=letter, null=True, blank=True, verbose_name='Оборудование')

class CompatibleMolds(models.Model):
    part_id = models.ForeignKey(Parts, on_delete=models.CASCADE, null=True, related_name='moldparts') 
    mold_id = models.CharField(max_length=2, choices=letter, null=True, blank=True, verbose_name='Пресс-форма')

class PartsPurchase(models.Model):
    part_id = models.ForeignKey(Parts, on_delete=models.CASCADE, null=True, related_name='partspurchase')
    date_posted = models.DateTimeField(default=timezone.now)
    purchase_date = models.DateTimeField(default=timezone.now)
    po_number = models.PositiveIntegerField(null=True, blank=True, verbose_name='Номер заказа')
    invoice_number = models.PositiveIntegerField(null=True, blank=True, verbose_name='Номер счета')
    qty_ordered = models.PositiveIntegerField(null=True, blank=True, verbose_name='Заказанное количество')    
    vendor = models.CharField(max_length=100, null=True, blank=True, verbose_name='Наименование поставщика')
    vendor_phone = models.CharField(max_length=100, null=True, blank=True, verbose_name='Телефон поставщика')
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True,)
    purchase_note = models.TextField(null=True, blank=True, verbose_name='Примечание к заказу')

    class Meta:
        ordering = ['-purchase_date']

    def __str__(self):
        return str(self.part_id)

    def get_absolute_url(self):
        return reverse('parts-location-page', kwargs={'purchaseid': self.pk})

class PartsRelease(models.Model):
    part_id = models.ForeignKey(Parts, on_delete=models.CASCADE, null=True, related_name='partsrelease')
    date_posted = models.DateTimeField(default=timezone.now)
    release_date = models.DateTimeField(default=timezone.now)
    qty_released = models.PositiveIntegerField(null=True, blank=True, verbose_name='Выпущенное количество')    
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True,)
    release_note = models.TextField(null=True, blank=True, verbose_name='Примечание к выпуску')

    class Meta:
        ordering = ['-release_date']
        
    def __str__(self):
        return str(self.part_id)

    def get_absolute_url(self):
        return reverse('parts-detail-page', kwargs={'pk': self.part_id.pk})

class PartsLocation(models.Model):
    part_id = models.ForeignKey(Parts, on_delete=models.CASCADE,blank=True, null=True, related_name='partslocation')
    purchase_id = models.ForeignKey(PartsPurchase, on_delete=models.CASCADE, blank=True, null=True, related_name='purchaselocation')
    warehouse = models.CharField(max_length=2, choices=letter, null=True, blank=True, verbose_name='Склад')
    rack = models.CharField(max_length=2, choices=letter, null=True, blank=True, verbose_name='Стеллаж')
    bay = models.CharField(max_length=2, choices=number, null=True, blank=True, verbose_name='Полка')
    level = models.CharField(max_length=2, choices=letter, null=True, blank=True, verbose_name='Уровень')
    position = models.CharField(max_length=2, choices=number, null=True, blank=True, verbose_name='Позиция')   
    quantity = models.PositiveIntegerField(null=True, blank=True, verbose_name='Количество в наличии')
    
    class Meta:
        unique_together = ('part_id', 'warehouse', 'rack', 'bay', 'level', 'position') 
    
    def get_absolute_url(self):
        return reverse('parts-location-page', kwargs={'purchaseid': self.purchase_id.pk}) 

class PartsFiles(models.Model):
    part_id = models.ForeignKey(Parts, on_delete=models.CASCADE, blank=True, null=True, related_name='partsfile')
    description = models.CharField(max_length=255, blank=True, verbose_name='Описание')
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='Создатель')
    partfile = models.FileField(upload_to='partsfiles/%Y/%m/%d/', validators=[validate_file_extension], verbose_name='Файл')
    uploaded_at = models.DateTimeField(default=timezone.now)  

    def __str__(self):
        return f'{str(self.uploaded_at)} - {str(self.partfile)}'
        
    def get_absolute_url(self):
        return reverse('parts-detail-page', kwargs={'pk': self.part_id.pk})
    
    class Meta:
        ordering = ['-uploaded_at'] 
        
@receiver(post_delete, sender=PartsFiles)
def submission_delete(sender, instance, **kwargs):
    instance.partfile.delete(False)
