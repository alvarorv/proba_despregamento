from django import forms

from .models import Product


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'product_name',
            'slug',
            'description',
            'price',
            'images',
            'stock',
            'is_available',
            'category',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            css_class = 'form-control'
            if name == 'images':
                css_class = 'form-control-file'
            field.widget.attrs.setdefault('class', css_class)
